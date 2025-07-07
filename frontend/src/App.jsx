import React, { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [chat, setChat] = useState([]);
  const [sessionId, setSessionId] = useState("");

  useEffect(() => {
    let sid = localStorage.getItem("session_id");
    if (!sid) {
      sid = uuidv4();
      localStorage.setItem("session_id", sid);
    }
    setSessionId(sid);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const form = new FormData();
    form.append("query", query);
    form.append("session_id", sessionId);

    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      body: form,
    });
    const data = await res.json();
    const userMessage = { role: "user", content: query };
    const botMessage = { role: "assistant", content: data.reply };

    setChat([...chat, userMessage, botMessage]);
    setResponse(data.reply);
    setQuery("");
  };

  const handleReset = () => {
    const newSession = uuidv4();
    localStorage.setItem("session_id", newSession);
    setSessionId(newSession);
    setChat([]);
    setResponse("");
    setQuery("");
  };

  return (
    <div
      style={{
        padding: "2rem",
        maxWidth: 700,
        margin: "auto",
        fontFamily: "Arial",
      }}
    >
      <h1>🎓 Smart Course Selector</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          rows={4}
          placeholder="Ask about courses, requirements, or interests..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ width: "100%", padding: "1rem", fontSize: "1rem" }}
        />
        <div style={{ marginTop: "1rem" }}>
          <button type="submit">Ask</button>
          <button
            type="button"
            onClick={handleReset}
            style={{ marginLeft: "1rem" }}
          >
            🔄 New Chat
          </button>
        </div>
      </form>

      <div style={{ marginTop: "2rem" }}>
        {chat.map((msg, idx) => (
          <div key={idx} style={{ marginBottom: "1rem" }}>
            <strong>{msg.role === "user" ? "You" : "Advisor"}:</strong>
            <p style={{ whiteSpace: "pre-wrap" }}>{msg.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
