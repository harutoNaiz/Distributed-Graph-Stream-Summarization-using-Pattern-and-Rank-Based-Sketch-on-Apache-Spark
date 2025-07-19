<h1>Distributed Graph Stream Summarization using Pattern and Rank-Based Sketch on Apache Spark</h1>

<p>
A scalable, memory-efficient system for <b>real-time summarization and querying of massive graph streams</b>. 
This project introduces a novel sketch-based approach
to distributed graph stream processing using <b>Apache Spark</b>, enabling low-latency analytics over high-throughput streaming graph data.
</p>

<hr>

<h2>Overview</h2>
<ul>
  <li>Conventional graph systems are insufficient for processing high-frequency, real-time updates over large-scale graphs.</li>
  <li>This system proposes a <b>custom pattern- and rank-based hashing mechanism</b> for <b>scalable, fault-tolerant execution</b>.</li>
  <li>Applicable to domains such as <i>social networks, real-time recommendation systems, network traffic analysis, and transactional graph processing</i>.</li>
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

<h2>Mathematical Foundations</h2>
<p>Our approach summarizes a continuous graph stream <code>S = {e₁, e₂, ..., eₜ}</code>, where each edge <code>e = (s, d, t, w)</code> contains source <code>s</code>, destination <code>d</code>, timestamp <code>t</code>, and weight <code>w</code>. To encode the graph compactly, we use pattern-based hashing and rank-aware updates, defined as follows:</p>

<h3>1. Pattern Construction</h3>
<p>
Each node is hashed multiple times to form a set of patterns:
</p>
<pre><code>Pₛ⁽ʲ⁾ = H₁(s) + H₂(s, j) mod W</code></pre>
<pre><code>P_d⁽ʲ⁾ = H₁(d) + H₂(d, j) mod W</code></pre>
<p>
Here, <code>j</code> is the pattern index and <code>W</code> is the hash width. The Cartesian product of <code>Pₛ</code> and <code>P_d</code> gives a diverse set of candidate cells for storing the edge.
</p>

<h3>2. Rank Construction</h3>
<p>
Each node is assigned a rank vector by permuting integers from 1 to L:
</p>
<pre><code>Rₛ = permute(1, 2, ..., L)</code></pre>
<pre><code>R_d = permute(1, 2, ..., L)</code></pre>
<p>
The rank of an edge is then computed as the elementwise sum of <code>Rₛ</code> and <code>R_d</code>:
</p>
<pre><code>Rankₑ⁽ⁱ,ʲ⁾ = Rₛ⁽ⁱ⁾ + R_d⁽ʲ⁾</code></pre>

<h3>3. Sketch Insertion</h3>
<p>
An edge is inserted into a 3D memory array <code>Sketch[i][j][z]</code> where:
</p>
<ul>
  <li><code>i, j</code> are selected from pattern combinations</li>
  <li><code>z</code> is the hash layer (for redundancy)</li>
</ul>
<p>
Insertion logic compares existing rank in the cell:
</p>
<ul>
  <li>If incoming rank is higher → overwrite (evict and insert)</li>
  <li>If ranks match → increment weight</li>
  <li>If incoming rank is lower → ignore</li>
</ul>

<h3>4. Reachability Query</h3>
<p>
To check if node <code>A</code> can reach node <code>C</code>, we look for paths like <code>A → B</code> and <code>B → C</code> in the sketch. This allows us to infer <code>A → C</code> without storing full paths. Since the structure is compact, some false positives are allowed, but never false negatives (if no path is reported, there truly isn’t one).
</p>

<h3>5. Edge Weight Query</h3>
<p>
To estimate the weight of an edge <code>(s, d)</code>, we:
</p>
<ol>
  <li>Recompute patterns and ranks</li>
  <li>Scan all matching cells with correct rank</li>
  <li>Return the minimum recorded weight among them</li>
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
