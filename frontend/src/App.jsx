import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    hcp_name: "",
    date: "19-04-2025",
    time: "19:36",
    interaction_type: "Meeting",
    attendees: "",
    topics_discussed: "",
    materials_shared: "No materials added",
    samples_distributed: "No samples added",
    sentiment: "Neutral",
    outcomes: "",
    follow_up_actions: ""
  });

  const [messages, setMessages] = useState([
    { type: "ai", text: "Hello! Describe the HCP interaction in natural language.\nExample: Met Dr. Sharma, discussed Product X efficacy, positive sentiment, shared brochure." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const chatRef = useRef(null);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { type: "user", text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/chat', {
        message: input
      });

      setMessages(prev => [...prev, { type: "ai", text: response.data.ai_response }]);
      setFormData(response.data.form_data || formData);
    } catch (error) {
      setMessages(prev => [...prev, { type: "ai", text: "❌ Backend not responding. Make sure FastAPI is running on port 8000." }]);
    }
    setLoading(false);
  };

  useEffect(() => {
    chatRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="app-container">
      <h1>Log HCP Interaction</h1>

      <div className="split-container">
        {/* LEFT PANEL - FORM */}
        <div className="left-panel">
          <h3>Interaction Details</h3>

          <div className="form-row">
            <div className="field">
              <label>HCP Name</label>
              <input type="text" value={formData.hcp_name} readOnly placeholder="Search or select HCP..." />
            </div>
            <div className="field">
              <label>Interaction Type</label>
              <select value={formData.interaction_type} disabled>
                <option>Meeting</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="field">
              <label>Date</label>
              <input type="text" value={formData.date} readOnly />
            </div>
            <div className="field">
              <label>Time</label>
              <input type="text" value={formData.time} readOnly />
            </div>
          </div>

          <div className="field">
            <label>Attendees</label>
            <input type="text" value={formData.attendees} readOnly placeholder="Enter names or search..." />
          </div>

          <div className="field">
            <label>Topics Discussed</label>
            <textarea value={formData.topics_discussed} readOnly rows="4" placeholder="Enter key discussion points..." />
          </div>

          <div className="field">
            <label>Materials Shared</label>
            <div className="material-box">{formData.materials_shared}</div>
          </div>

          <div className="field">
            <label>Samples Distributed</label>
            <div className="material-box">{formData.samples_distributed}</div>
          </div>

          <div className="sentiment-section">
  <label>Observed/Inferred HCP Sentiment</label>
  <div className="sentiment-options">
    <span 
      className={`sentiment-btn ${formData.sentiment === "Positive" ? "active positive" : ""}`}
      onClick={() => {}} // readonly for now
    >
      Positive
    </span>
    <span 
      className={`sentiment-btn ${formData.sentiment === "Neutral" ? "active neutral" : ""}`}
    >
      Neutral
    </span>
    <span 
      className={`sentiment-btn ${formData.sentiment === "Negative" ? "active negative" : ""}`}
    >
      Negative
    </span>
  </div>
</div>

          <div className="field">
            <label>Outcomes</label>
            <textarea value={formData.outcomes} readOnly rows="2" placeholder="Key outcomes or agreements..." />
          </div>

          <div className="field">
            <label>Follow-up Actions</label>
            <textarea value={formData.follow_up_actions} readOnly rows="3" placeholder="Enter next steps or tasks..." />
          </div>
        </div>

        {/* RIGHT PANEL - AI ASSISTANT */}
        <div className="right-panel">
          <div className="ai-header">
            <strong>AI Assistant</strong>
            <small>Log interaction via chat</small>
          </div>

          <div className="chat-window">
            {messages.map((msg, index) => (
              <div key={index} className={`chat-bubble ${msg.type}`}>
                {msg.text}
              </div>
            ))}
            {loading && <div className="chat-bubble ai">Thinking...</div>}
            <div ref={chatRef} />
          </div>

          <div className="chat-input">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Describe interaction... (e.g. Met Dr. Smith, discussed Product X...)"
            />
            <button onClick={sendMessage} disabled={loading}>Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;