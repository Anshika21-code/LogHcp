import { useSelector } from "react-redux";

export default function InteractionForm() {
  const data = useSelector((state) => state.interaction);

  return (
    <div>
      <h2>Log HCP Interaction</h2>

      <input placeholder="HCP Name" value={data.hcpName} readOnly />
      <input type="date" value={data.date} readOnly />
      <input type="time" value={data.time} readOnly />

      <textarea placeholder="Attendees" value={data.attendees} readOnly />
      <textarea placeholder="Topics" value={data.topics} readOnly />

      <select value={data.sentiment} disabled>
        <option>positive</option>
        <option>neutral</option>
        <option>negative</option>
      </select>

      <textarea placeholder="Outcomes" value={data.outcomes} readOnly />
      <textarea placeholder="Follow-up" value={data.followUp} readOnly />
    </div>
  );
}