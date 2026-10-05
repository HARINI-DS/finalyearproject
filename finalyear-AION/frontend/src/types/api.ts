export type PlanResponse = {
  workflow_id: string;
  workflow_db_id: number;
  goal: string;
  tasks: Array<{ id: string; action: string; agent: string; parameters: Record<string, unknown> }>;
  required_capabilities: Record<string, string[]>;
};
