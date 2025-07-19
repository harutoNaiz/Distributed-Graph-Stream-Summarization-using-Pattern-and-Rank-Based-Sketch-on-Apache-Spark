<h1>Distributed Graph Stream Summarization using Pattern and Rank-Based Sketch on Apache Spark</h1>

<p>
A scalable, memory-efficient system for <b>real-time summarization and querying of massive graph streams</b>. 
This project introduces a novel sketch-based approach
to distributed graph stream processing using <b>Apache Spark</b>, enabling low-latency analytics over high-throughput streaming graph data.
</p>

<hr>

<h2>Mathematical Foundations & Overview</h2>

<p>
Our system compresses a dynamic graph stream <code>S = {e₁, e₂, ..., eₜ}</code>, where each edge <code>e = (s, d, t, w)</code> represents a connection from node <code>s</code> to node <code>d</code> at time <code>t</code> with weight <code>w &gt; 0</code>.
</p>

<ul>
  <li>Unlike static methods, this system supports <b>real-time updates and queries</b> on continuously evolving graphs.</li>
  <li>We introduce a self-designed <b>pattern-and-rank-based hash sketch</b> that compresses the graph into a compact memory structure while preserving query accuracy.</li>
</ul>

<p style="text-align: center;">
  <img src="assets/_architecture.png" alt="System Architecture Diagram" style="width: 40%; height: auto; border: 1px solid #ccc; padding: 4px;">
</p>


<h3>1. Pattern Construction</h3>
<p>
Each node is hashed multiple times using diverse hash functions to generate a pattern set:
</p>
<pre><code>Pₛ⁽ʲ⁾ = H₁(s) + H₂(s, j) mod W</code></pre>
<pre><code>P_d⁽ʲ⁾ = H₁(d) + H₂(d, j) mod W</code></pre>
<p>
The Cartesian product of <code>Pₛ</code> and <code>P_d</code> provides multiple candidate cells for sketch updates, improving distribution and reducing collisions.
</p>

<h3>2. Rank Construction</h3>
<p>
Each node is associated with a random permutation of ranks:
</p>
<pre><code>Rₛ = permute(1, 2, ..., L)</code></pre>
<pre><code>R_d = permute(1, 2, ..., L)</code></pre>
<p>
The edge's rank vector is then defined as:
</p>
<pre><code>Rankₑ⁽ⁱ,ʲ⁾ = Rₛ⁽ⁱ⁾ + R_d⁽ʲ⁾</code></pre>

<h3>3. Sketch Insertion Logic</h3>
<p>
We maintain a 3D sketch array <code>Sketch[i][j][z]</code> where:
</p>
<ul>
  <li><code>i, j</code> are pattern coordinates from the Cartesian product of <code>Pₛ</code> and <code>P_d</code></li>
  <li><code>z</code> is the hash table layer (for redundancy)</li>
</ul>

<p>For each candidate cell:</p>
<ul>
  <li>If the incoming rank is higher than the stored one → overwrite (eviction)</li>
  <li>If the rank matches → increment the frequency counter</li>
  <li>If the incoming rank is lower → do nothing</li>
</ul>

<h3>4. Edge Weight Query</h3>
<p>
To estimate the frequency of an edge <code>(s, d)</code>:
</p>
<ol>
  <li>Compute all pattern and rank pairs</li>
  <li>Scan corresponding cells in each layer</li>
  <li>Return the smallest valid count value</li>
</ol>

<h3>5. Reachability Query</h3>
<p>
Given nodes <code>A</code> and <code>C</code>, we infer a reachable path exists if there is a sequence like <code>A → B</code> and <code>B → C</code> present in the sketch. This allows multi-hop connectivity detection with no false negatives: if the sketch says "not reachable", then it's truly not reachable.
</p>

<h3>Applications</h3>
<ul>
  <li>Social networks: friend-of-a-friend detection, trending links</li>
  <li>Fraud analytics: detection of transaction chains</li>
  <li>Network traffic: flow aggregation and hotspot identification</li>
  <li>Recommendation systems: link estimation in real-time</li>
</ul>

<hr>

<h2>Key Features</h2>
<ul>
  <li><b>Optimized Hashing Strategy</b> with pattern diversity and rank-aware conflict resolution for efficient memory usage</li>
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
    <pre><code>git clone https://github.com/harutoNaiz/Distributed-Graph-Stream-Summarization-using-Pattern-and-Rank-Based-Sketch-on-Apache-Spark.git</code></pre>
  </li>
  <li>Install Spark</li>
  <li>Navigate to the server's dir and run : </li>
  <pre><code>python server.py</code></pre>
  <li>Use the client script to issue queries such as reachability and edge weight estimation my make changes in the config and run : </li>
  <pre><code>python client.py</code></pre>
</ol>

<hr>

<h2>Example Query</h2>
<pre><code>
Client sends: Edge query A -> B
Server responds: Reachable: True | Edge Weight Estimate: 12.0
</code></pre>
