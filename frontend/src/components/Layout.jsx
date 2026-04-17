import InteractionForm from "./InteractionForm";
import ChatPanel from "./ChatPanel";

export default function Layout() {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ flex: 2, padding: "20px", background: "#f5f5f5" }}>
        <InteractionForm />
      </div>
      <div style={{ flex: 1, borderLeft: "1px solid #ddd" }}>
        <ChatPanel />
      </div>
    </div>
  );
}