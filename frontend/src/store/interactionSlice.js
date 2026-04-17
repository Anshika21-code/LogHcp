import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  hcpName: "",
  date: "",
  time: "",
  attendees: "",
  topics: "",
  sentiment: "neutral",
  outcomes: "",
  followUp: "",
};

const interactionSlice = createSlice({
  name: "interaction",
  initialState,
  reducers: {
    setField: (state, action) => {
      const { field, value } = action.payload;
      state[field] = value;
    },
    setAllFields: (state, action) => {
      return { ...state, ...action.payload };
    },
  },
});

export const { setField, setAllFields } = interactionSlice.actions;
export default interactionSlice.reducer;