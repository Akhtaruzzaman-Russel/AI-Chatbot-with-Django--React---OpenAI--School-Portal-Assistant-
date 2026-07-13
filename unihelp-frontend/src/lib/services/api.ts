import axios from "axios"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function promptOpenai(data: { message: string }) {
  try {
    const response = await axios.post(`${API_BASE_URL}/ai/chat_with_unihelp/`, data);
    return response.data;
  } catch (err: unknown) {
    if (axios.isAxiosError(err)) {
      throw new Error(err.response?.data?.error || err.message);
    }

    throw new Error("Unable to reach the chat service.");
  }
}