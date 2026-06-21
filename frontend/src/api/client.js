import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export const createWorkflow = (request) =>
  api.post("/workflow", { request }).then((r) => r.data);

export const getWorkflow = (id) =>
  api.get(`/workflow/${id}`).then((r) => r.data);

export const submitApproval = (id, approved, comment = "", modifiedRecommendations = null) =>
  api.post(`/workflow/${id}/approval`, {
    approved,
    comment,
    ...(modifiedRecommendations !== null && { modified_recommendations: modifiedRecommendations }),
  }).then((r) => r.data);

export const submitFeedback = (id, rating) =>
  api.post(`/workflow/${id}/feedback`, { rating }).then((r) => r.data);

export const getMetrics = () => api.get("/metrics").then((r) => r.data);

export const getMetricsHistory = (days = 7) =>
  api.get(`/metrics/history?days=${days}`).then((r) => r.data);

export const runPlayground = (agent, query) =>
  api.post("/playground", { agent, query }).then((r) => r.data);

export const getMemoryHistory = (limit = 20) =>
  api.get(`/memory?limit=${limit}`).then((r) => r.data);

export const getMemoryStats = () =>
  api.get("/memory/stats").then((r) => r.data);

export const getEntityMemories = (limit = 20) =>
  api.get(`/memory/entities?limit=${limit}`).then((r) => r.data);

export const getFeedbackHistory = (limit = 20) =>
  api.get(`/memory/feedback?limit=${limit}`).then((r) => r.data);

export const ingestFile = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/ingest", form).then((r) => r.data);
};
