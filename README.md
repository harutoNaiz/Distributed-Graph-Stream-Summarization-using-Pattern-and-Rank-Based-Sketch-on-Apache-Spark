<h1>Distributed Graph Stream Summarization using Pattern and Rank-Based Sketch on Apache Spark</h1>

<p>
A scalable, memory-efficient system for <b>real-time summarization and querying of massive graph streams</b>. 
This project extends the PR-Sketch algorithm
to a distributed environment using <b>Apache Spark</b>, enabling low-latency analytics over high-throughput streaming graph data.
</p>

<hr>

<h2>Overview</h2>
<ul>
  <li>Conventional graph systems are insufficient for processing high-frequency, real-time updates over large-scale graphs.</li>
  <li>This system modifies and distributes the <b>Pattern and Rank Sketch</b> (PR-Sketch) algorithm for <b>scalable, fault-tolerant execution</b>.</li>
  <li>Applicable to domains such as <i>social networks, real-time recommendation systems, network traffic analysis, and transactional graph processing</i>.</li>
</ul>

<hr>

<h2>Key Features</h2>
<ul>
  <li><b>Enhanced PR-Sketch</b> with optimized hashing strategy and rank-aware updates for efficient memory use under collision constraints</li>
  <li><b>Apache Spark Integration</b> using structured streaming and batch-wise transformations for scalable distributed edge processing</li>
  <li><b>Client-Server Query Engine</b> designed to support real-time estimation of edge weights and multi-hop reachability</li>
  <li><b>Compact Sketch Representation</b> ensuring efficient ingestion and summarization of continuously evolving graph data</li>
</ul>

<hr>

<h2>Architecture</h2>
<p>The system is composed of three modular components:</p>
<ol>
  <li><b>Sketching Module:</b> Maintains a compressed in-memory summary of the graph using enhanced pattern and rank-based logic</li>
  <li><b>Distributed Spark Backend:</b> Processes edge updates in batches across cluster nodes using Spark DataFrame APIs and custom aggregators</li>
  <li><b>Client-Server Interface:</b> Handles external query requests, serializes responses, and supports concurrent sessions</li>
</ol>

<hr>

<h2>Tech Stack</h2>
<ul>
  <li><b>Apache Spark</b> – Stream processing and distributed data transformations</li>
  <li><b>Python</b> – Core implementation of the sketching logic and server logic</li>
  <li><b>Socket Programming</b> – TCP-based client-server communication for real-time interaction</li>
  <li><b>Structured Streaming</b> – Incremental data ingestion with batch triggers</li>
</ul>

<hr>

<h2>Getting Started</h2>
<ol>
  <li>Clone the repository:<br>
    <pre><code>git clone https://github.com/your-username/distributed-prsketch.git</code></pre>
  </li>
  <li>Install Python dependencies and configure the Apache Spark environment</li>
  <li>Launch the server to begin processing incoming graph stream data</li>
  <li>Use the client script to issue queries such as reachability and edge weight estimation</li>
</ol>

<hr>

<h2>Example Query</h2>
<pre><code>
Client sends: A -> B
Server responds: Reachable: True | Edge Weight Estimate: 12.0
</code></pre>
