import { type ChangeEvent, useEffect, useMemo, useState } from "react";
import { approveWorkflow, executeWorkflow, grantPermission, planWorkflow, getPermissions } from "../services/api";
import PermissionDialog, { PermissionRequest } from "./PermissionDialog";
import DeleteConfirmDialog from "./DeleteConfirmDialog";

type ProgressEvent = { task_id?: string; status: string; message: string; error?: string };
type PlanTask = { id: string; action: string; agent: string; parameters: Record<string, unknown> };
type PlanData = {
  workflow_id: string;
  goal: string;
  tasks: PlanTask[];
  required_capabilities: Record<string, string[]>;
};

export default function FloatingAssistant() {
  const [goal, setGoal] = useState("");
  const [plan, setPlan] = useState<PlanData | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [minimized, setMinimized] = useState(true);
  const [pendingPermission, setPendingPermission] = useState<PermissionRequest | null>(null);
  const [pendingDelete, setPendingDelete] = useState<{ path: string; type: "file" | "folder" } | null>(null);
  const [currentPermissions, setCurrentPermissions] = useState<Array<{ capability: string; scope: string; granted: boolean }>>([]);

  // Load initial permissions
  useEffect(() => {
    const loadPermissions = async () => {
      try {
        const perms = await getPermissions();
        // Handle both array and object responses
        const permArray = Array.isArray(perms) ? perms : perms.value || [];
        setCurrentPermissions(permArray.map((p: any) => ({
          capability: p.capability,
          scope: p.resource_path || p.scope,
          granted: p.granted
        })));
      } catch (err) {
        // Silently fail - permissions start empty
        console.log("Failed to load permissions:", err);
      }
    };
    loadPermissions();
  }, []);

  const iconState = useMemo(() => {
    if (busy) return "EXECUTING";
    if (plan) return "WAITING FOR PERMISSION";
    return "IDLE";
  }, [busy, plan]);

  const pushLog = (entry: string) =>
    setLog((prev: string[]) => [`${new Date().toLocaleTimeString()} ${entry}`, ...prev].slice(0, 40));

  const onPlan = async () => {
    console.log("onPlan called with goal:", goal);
    if (!goal.trim()) {
      console.log("Goal is empty, returning");
      return;
    }
    setBusy(true);
    try {
      console.log("Calling planWorkflow API...");
      const response = await planWorkflow(goal);
      console.log("API response received:", response);
      setPlan(response);
      pushLog("Goal interpreted and workflow planned");
    } catch (error: any) {
      console.error("Planning error:", error);
      pushLog(`Planning failed: ${String(error)}`);
    } finally {
      setBusy(false);
    }
  };

  const onApproveAndRun = async () => {
    if (!plan) return;
    setBusy(true);
    pushLog("Checking permissions required for workflow...");

    try {
      // Check if any DELETE operations are in the plan
      const hasDeleteOps = plan.tasks.some((t) => t.action === "delete_item" || t.action === "delete");
      if (hasDeleteOps) {
        // Find the first delete operation for confirmation
        const deleteTask = plan.tasks.find((t) => t.action === "delete_item" || t.action === "delete");
        if (deleteTask) {
          const itemPath = (deleteTask.parameters.path as string) || "item";
          setPendingDelete({ path: itemPath, type: "file" });
          pushLog("Delete operation detected - awaiting confirmation");
          setBusy(false);
          return;
        }
      }

      // Check permissions for each capability
      const allCapabilities = plan.required_capabilities || {};
      for (const [capability, scopes] of Object.entries(allCapabilities)) {
        for (const scope of scopes as string[]) {
          // Simulate permission check
          const alreadyGranted = currentPermissions.some(
            (p) => p.capability === capability && p.scope === scope && p.granted
          );

          if (!alreadyGranted) {
            // Request permission
            setPendingPermission({
              action: plan.tasks[0]?.action || "unknown",
              path: scope,
              capability,
              message: `I need ${capability} access to perform the requested workflow`,
            });
            pushLog(`Permission required: ${capability} on ${scope}`);
            setBusy(false);
            return;
          }
        }
      }

      // All permissions granted, execute workflow
      await executeWorkflowNow();
    } catch (error: any) {
      pushLog(`Workflow failed: ${String(error)}`);
      setBusy(false);
    }
  };

  const executeWorkflowNow = async () => {
    if (!plan) return;

    try {
      pushLog("Approving workflow...");
      await approveWorkflow(plan.workflow_id, true);

      pushLog("Executing workflow...");
      const result = await executeWorkflow(plan.workflow_id, true);
      pushLog("Workflow completed successfully");

      if (result.learning_candidates?.length) {
        pushLog("Workflow pattern detected for learning");
      }

      // Reset state
      setGoal("");
      setPlan(null);
    } catch (error: any) {
      pushLog(`Execution failed: ${String(error)}`);
    } finally {
      setBusy(false);
    }
  };

  const handlePermissionAllow = async (capability: string, scope: string, permanent: boolean) => {
    setBusy(true);
    try {
      pushLog(`Granting ${capability} access to ${scope}${permanent ? " (permanent)" : ""}...`);
      await grantPermission(capability, [scope]);

      // Update current permissions
      setCurrentPermissions([
        ...currentPermissions.filter((p) => !(p.capability === capability && p.scope === scope)),
        { capability, scope, granted: true },
      ]);

      pushLog(`Permission granted for ${capability}`);
      setPendingPermission(null);

      // Continue with workflow
      setTimeout(() => {
        onApproveAndRun();
      }, 500);
    } catch (error: any) {
      pushLog(`Failed to grant permission: ${String(error)}`);
      setBusy(false);
    }
  };

  const handlePermissionCancel = () => {
    setPendingPermission(null);
    pushLog("Permission denied. Workflow cancelled.");
    setBusy(false);
  };

  const handleDeleteConfirm = async () => {
    setBusy(true);
    try {
      pushLog("Delete confirmed. Executing workflow...");
      setPendingDelete(null);
      await executeWorkflowNow();
    } catch (error: any) {
      pushLog(`Deletion failed: ${String(error)}`);
      setBusy(false);
    }
  };

  const handleDeleteCancel = () => {
    setPendingDelete(null);
    pushLog("Deletion cancelled. Workflow stopped.");
    setBusy(false);
  };

  return (
    <>
      {pendingPermission && (
        <PermissionDialog
          permission={pendingPermission}
          currentPermissions={currentPermissions}
          onAllow={handlePermissionAllow}
          onCancel={handlePermissionCancel}
          loading={busy}
        />
      )}

      {pendingDelete && (
        <DeleteConfirmDialog
          itemPath={pendingDelete.path}
          itemType={pendingDelete.type}
          onConfirm={handleDeleteConfirm}
          onCancel={handleDeleteCancel}
          loading={busy}
        />
      )}

      <div className="fixed bottom-6 right-6 z-40">
        {minimized ? (
          <button
            type="button"
            onClick={() => setMinimized(false)}
            className="flex items-center gap-2 rounded-full border border-[#5cc8ff]/40 bg-[#101b2a]/95 px-4 py-2 text-sm font-semibold text-slate-100 shadow-lg shadow-slate-950/40 transition hover:scale-[1.02]"
            aria-label="Open AION"
          >
            <span className="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.9)]" />
            <span>AION</span>
          </button>
        ) : (
          <div className="w-[380px] max-w-[92vw] rounded-card border border-line bg-panel/95 shadow-float backdrop-blur">
            <div className="flex items-center justify-between rounded-t-card bg-gradient-to-r from-[#1e2d3f] via-[#163949] to-[#0c2231] px-4 py-3">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-neon">AION</p>
                <p className="text-xs text-slate-300">State: {iconState}</p>
              </div>
              <button
                type="button"
                onClick={() => setMinimized(true)}
                className="rounded-full border border-line px-2 py-1 text-[10px] uppercase tracking-wide text-slate-300"
              >
                Minimize
              </button>
            </div>

            <div className="space-y-3 p-4">
              <p className="text-sm text-slate-200">What would you like me to accomplish?</p>

              <textarea
                value={goal}
                onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setGoal(e.target.value)}
                rows={3}
                placeholder="Type your goal..."
                className="w-full resize-none rounded-xl border border-line bg-panel2 px-3 py-2 text-sm text-slate-100 outline-none focus:border-neon"
              />

              <div className="flex gap-2">
                <button
                  className="rounded-lg bg-neon px-3 py-2 text-xs font-semibold text-slate-900 disabled:opacity-60"
                  onClick={onPlan}
                  disabled={busy}
                >
                  Plan Workflow
                </button>
                <button
                  className="rounded-lg border border-good px-3 py-2 text-xs font-semibold text-good disabled:opacity-60"
                  onClick={onApproveAndRun}
                  disabled={busy || !plan}
                >
                  Approve and Run
                </button>
                <button
                  className="rounded-lg border border-line px-3 py-2 text-xs text-slate-300"
                  onClick={() => setShowDetails((s: boolean) => !s)}
                >
                  {showDetails ? "Hide Details" : "View Details"}
                </button>
              </div>

              {plan && (
                <div className="rounded-xl border border-line bg-panel2 p-3 text-xs text-slate-300">
                  <p className="mb-2 font-semibold text-slate-100">Workflow Ready</p>
                  <p className="mb-2">Goal: {plan.goal}</p>
                  <ul className="space-y-1">
                    {plan.tasks.map((task: PlanTask) => (
                      <li key={task.id}>- {task.action} via {task.agent}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="max-h-40 space-y-1 overflow-auto rounded-xl border border-line bg-[#0d1117] p-2 text-[11px] text-slate-400">
                {log.length === 0 ? <p>No execution log yet.</p> : log.map((entry: string) => <p key={entry}>{entry}</p>)}
              </div>

              {showDetails && (
                <div className="rounded-xl border border-line bg-panel2 p-3 text-xs text-slate-300">
                  <p className="font-semibold text-slate-100">Expanded View</p>
                  <p>Workflow history, memory, learning, and settings are available through API-backed pages.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
