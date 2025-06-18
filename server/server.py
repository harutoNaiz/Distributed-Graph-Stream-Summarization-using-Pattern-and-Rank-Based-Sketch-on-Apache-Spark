import socket
import threading
import pickle
import time
import os
import shutil
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, split, trim
from pyspark.sql.types import StructType, StructField, StringType
from pyspark_pr_sketch import PRSketchSpark

class SparkPRSketchServer:
    def __init__(self, host='localhost', port=9992):
        self.host = host
        self.port = port
        self.clients = []
        self.spark = SparkSession.builder \
            .appName("PRSketchServer") \
            .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
            .getOrCreate()
        self.sketch = None
        self.running = False
        self.query = None

    def handle_client(self, conn, addr):
        print(f"[SERVER] Connected to {addr}")
        
        try:
            config = pickle.loads(conn.recv(4096))
            width = config['width']
            depth = config['depth']
            pattern_length = config['pattern_length']
            conflict_limit = config['conflict_limit']
            file_path = config['file_path']
            queries = config['queries']
            batch_size = config.get('batch_size', 1000)

            print(f"[SERVER] Config received:")
            print(f"  → Width: {width}")
            print(f"  → Depth: {depth}")
            print(f"  → Pattern Length: {pattern_length}")
            print(f"  → Conflict Limit: {conflict_limit}")
            print(f"  → File Path: {file_path}")
            print(f"  → Batch Size: {batch_size}")
            print(f"  → Queries: {queries}")

            # Initialize PRSketch
            self.sketch = PRSketchSpark(
                width=width,
                depth=depth,
                pattern_length=pattern_length,
                conflict_limit=conflict_limit
            )

            # Create a temp directory for streaming
            temp_dir = "/tmp/pr_sketch_stream"
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            # Copy input file to temp location
            temp_file = os.path.join(temp_dir, "data.txt")
            shutil.copy2(file_path, temp_file)

            # Define schema for streaming
            schema = StructType([
                StructField("value", StringType(), True)
            ])

            # Process each batch
            def process_batch(batch_df, batch_id):
                if batch_df.count() == 0:
                    return
                
                # Clean and process the batch
                cleaned_df = batch_df.filter(~batch_df.value.startswith("#"))
                edges_df = cleaned_df.select(
                    split(trim(cleaned_df.value), "\t").getItem(0).alias("source"),
                    split(trim(cleaned_df.value), "\t").getItem(1).alias("dest")
                ).withColumn("weight", lit(1.0))
                
                # Update sketch with this batch (collect to driver first)
                edges_collected = edges_df.collect()
                self.sketch.update(edges_collected)
                print(f"Processed batch {batch_id} with {len(edges_collected)} edges")

            # Start streaming query
            stream_df = self.spark.readStream \
                .schema(schema) \
                .option("maxFilesPerTrigger", 1) \
                .text(temp_dir)

            self.query = stream_df.writeStream \
                .foreachBatch(process_batch) \
                .start()

            # Query processing thread
            def run_query():
                self.running = True
                while self.running:
                    try:
                        results = []
                        for (src, dest) in queries:
                            edge_weight = self.sketch.edge_query(src, dest)
                            reachability = self.sketch.reachability_query(src, dest)
                            results.append({
                                'query': (src, dest),
                                'edge_weight': edge_weight,
                                'reachability': reachability
                            })
                        conn.sendall(pickle.dumps(results))
                        time.sleep(2)
                    except Exception as e:
                        print(f"Query error: {e}")
                        break

            query_thread = threading.Thread(target=run_query, daemon=True)
            query_thread.start()

            self.query.awaitTermination()

        except Exception as e:
            print(f"Client handling error: {e}")
        finally:
            self.running = False
            if self.query:
                self.query.stop()
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            conn.close()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"[SERVER] Listening on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True
                )
                client_thread.start()
                self.clients.append(conn)

    def stop(self):
        self.running = False
        self.spark.stop()

if __name__ == "__main__":
    server = SparkPRSketchServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()