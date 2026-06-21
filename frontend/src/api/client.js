import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export const createWorkflow = (request) =>
  api.post("/workflow", { request }).then((r) => r.data);

export const getWorkflow = (id) =>
  api.get(`/workflow/${id}`).then((r) => r.data);

export const submitApproval = (id, approved, comment = "") =>
  api.post(`/workflow/${id}/approval`, { approved, comment }).then((r) => r.data);

export const getMetrics = () => api.get("/metrics").then((r) => r.data);

export const ingestFile = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/ingest", form).then((r) => r.data);
};
