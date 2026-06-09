import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [text, setText] = useState("");
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [analytics, setAnalytics] = useState(null);
  const [retrieved, setRetrieved] = useState([]);
  const [history, setHistory] = useState([]);
  
  
  
  
const fetchHistory = async () => {
  const res = await axios.get(`${API_BASE}/analytics/history`);

  const formatted = res.data.history.map((item, index) => ({
    ...item,
    step: index + 1,
  }));

  setHistory(formatted);
};

  const fetchAnalytics = async () => {
    const res = await axios.get(`${API_BASE}/analytics/`);
    setAnalytics(res.data);
  };

  useEffect(() => {
    fetchAnalytics();
    fetchHistory();
}, []);

  const uploadText = async () => {
    await axios.post(`${API_BASE}/documents/upload_text`, {
      text,
      source: "frontend_upload",
    });

    setText("");
    fetchAnalytics();
  };

  const chat = async () => {
    const res = await axios.post(`${API_BASE}/chat/`, {
      query,
      top_k: 5,
    });

    setAnswer(res.data.answer);
    setRetrieved(res.data.retrieved);
    fetchAnalytics();
    fetchHistory();
  };

  return (
    <div className="container">
      <h1>MemoryRAG Dashboard</h1>
      <p className="subtitle">
        Long-term conversational memory RAG with memory score and decay-aware retrieval.
      </p>

      <div className="cards">
        <div className="card">
          <h3>Total Memories</h3>
          <p>{analytics?.memory_count ?? 0}</p>
        </div>

        <div className="card">
          <h3>Avg Memory Score</h3>
          <p>{analytics?.avg_memory_score?.toFixed(3) ?? 0}</p>
        </div>

        <div className="card">
          <h3>Avg Retrieval Count</h3>
          <p>{analytics?.avg_retrieval_count?.toFixed(2) ?? 0}</p>
        </div>
      </div>

      <section>
        <h2>Upload Memory</h2>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste document or memory text here..."
        />
        <button onClick={uploadText}>Upload</button>
      </section>

      <section>
        <h2>Chat</h2>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something..."
        />
        <button onClick={chat}>Ask</button>

        {answer && (
          <div className="answer">
            <h3>Answer</h3>
            <pre>{answer}</pre>
          </div>
        )}
      </section>

      <section>
        <h2>Memory Score Curve</h2>
        <p className="chartHint">
            Tracks how memory score changes across retrieval steps.
            </p>

        <div className="chartBox">
            <ResponsiveContainer width="100%" height={300}>
            <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="step" />
                <YAxis />
                <Tooltip />
                <Line
                type="monotone"
                dataKey="memory_score"
                strokeWidth={3}
                />
            </LineChart>
            </ResponsiveContainer>
        </div>
      </section>

      <section>
        <h2>Retrieved Memories</h2>
        <table>
          <thead>
            <tr>
              <th>Text</th>
              <th>Semantic</th>
              <th>Memory</th>
              <th>Combined</th>
              <th>Retrieved</th>
            </tr>
          </thead>
          <tbody>
            {retrieved.map((item, idx) => (
              <tr key={idx}>
                <td>{item.text}</td>
                <td>{item.semantic_score?.toFixed(3)}</td>
                <td>{item.memory_score?.toFixed(3)}</td>
                <td>{item.combined_score?.toFixed(3)}</td>
                <td>{item.metadata?.retrieval_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2>Top Memories</h2>
        <table>
          <thead>
            <tr>
              <th>Memory</th>
              <th>Score</th>
              <th>Retrieval Count</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {analytics?.top_memories?.map((m, idx) => (
              <tr key={idx}>
                <td>{m.text}</td>
                <td>{m.memory_score?.toFixed(3)}</td>
                <td>{m.retrieval_count}</td>
                <td>{m.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default App; 