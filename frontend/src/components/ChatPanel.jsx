import { useState } from "react";
import { useDispatch } from "react-redux";
import { setAllFields } from "../store/interactionSlice";
import axios from "axios";

export default function ChatPanel() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const dispatch = useDispatch();

  const handleSend = async () => {
    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await axios.post("http://localhost:8000/api/chat", {
        message: input,
      });

      const aiData = res.data;

      // 🔥 THIS IS KEY (AI updates form)
      dispatch(setAllFields(aiData));

      setMessages((prev) => [
        ...prev,
        { role: "ai", text: "Form updated successfully" },
      ]);
    } catch (err) {
      console.log(err);
    }

    setInput("");
  };

  return (
    <div style={{ padding: "10px" }}>
      <h3>AI Assistant</h3>

      <div style={{ height: "70vh", overflow: "auto" }}>
        {messages.map((m, i) => (
          <div key={i}>
            <b>{m.role}:</b> {m.text}
          </div>
        ))}
      </div>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Describe interaction..."
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}