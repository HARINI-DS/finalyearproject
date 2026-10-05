import type { PlanResponse } from "../types/api";

const API_BASE = "http://127.0.0.1:8000";

export async function planWorkflow(goal: string): Promise<PlanResponse> {
  const response = await fetch(`${API_BASE}/api/workflow/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function grantPermission(capability: string, scopes: string[]) {
  const response = await fetch(`${API_BASE}/api/permissions/grant`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ capability, scopes })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function getPermissions() {
  const response = await fetch(`${API_BASE}/api/permissions`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function approveWorkflow(workflowId: string, approved = true) {
  const response = await fetch(`${API_BASE}/api/workflow/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workflow_id: workflowId, approved })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function executeWorkflow(workflowId: string, approved = true) {
  const response = await fetch(`${API_BASE}/api/workflow/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workflow_id: workflowId, approved })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function fetchHistory() {
  const response = await fetch(`${API_BASE}/api/workflow/history`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function fetchMemory() {
  const response = await fetch(`${API_BASE}/api/memory`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function savePreference(key: string, value: string) {
  const response = await fetch(`${API_BASE}/api/memory/preferences`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key, value })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
