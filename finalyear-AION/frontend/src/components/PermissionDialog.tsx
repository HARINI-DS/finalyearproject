import { useState } from "react";

export type PermissionRequest = {
  action: string;
  path: string;
  capability: string;
  message: string;
};

type Props = {
  permission: PermissionRequest;
  currentPermissions: Array<{ capability: string; scope: string; granted: boolean }>;
  onAllow: (capability: string, scope: string, permanent: boolean) => void;
  onCancel: () => void;
  loading?: boolean;
};

export default function PermissionDialog({
  permission,
  currentPermissions,
  onAllow,
  onCancel,
  loading = false
}: Props) {
  const [permanent, setPermanent] = useState(false);

  const alreadyGranted = currentPermissions.some(
    (p) =>
      p.capability === permission.capability &&
      p.scope === permission.path &&
      p.granted
  );

  if (alreadyGranted) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-96 max-w-[90vw] rounded-xl border border-line bg-panel shadow-xl">
        {/* Header */}
        <div className="border-b border-line bg-gradient-to-r from-[#1e2d3f] via-[#163949] to-[#0c2231] px-6 py-4 rounded-t-xl">
          <h2 className="text-sm font-semibold text-neon uppercase tracking-wider">Permission Required</h2>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Action Description */}
          <div className="bg-panel2 rounded-lg p-4 border border-line">
            <p className="text-xs uppercase tracking-widest text-slate-400 mb-2">Action</p>
            <p className="text-sm font-semibold text-slate-100">{permission.action}</p>
            <p className="text-xs text-slate-400 mt-2">{permission.message}</p>
          </div>

          {/* Location */}
          <div className="bg-panel2 rounded-lg p-4 border border-line">
            <p className="text-xs uppercase tracking-widest text-slate-400 mb-2">Location</p>
            <p className="text-sm font-mono text-slate-200 break-all">{permission.path}</p>
          </div>

          {/* Required Capability */}
          <div className="bg-panel2 rounded-lg p-4 border border-line">
            <p className="text-xs uppercase tracking-widest text-slate-400 mb-2">Required Access</p>
            <div className="flex items-center gap-2">
              <div className="px-3 py-1 rounded-full bg-neon/20 border border-neon">
                <p className="text-xs font-semibold text-neon">{permission.capability}</p>
              </div>
              <p className="text-xs text-slate-400">to {permission.path}</p>
            </div>
          </div>

          {/* Explanation */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <p className="text-xs text-blue-200 leading-relaxed">
              ℹ️ I need permission to perform this action. You can allow this operation once, 
              or grant permanent permission for future operations on this location.
            </p>
          </div>

          {/* Permanent toggle */}
          <div className="flex items-center gap-3 py-2">
            <button
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                permanent ? "bg-neon" : "bg-slate-600"
              }`}
              onClick={() => setPermanent(!permanent)}
              disabled={loading}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  permanent ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
            <label className="text-xs text-slate-300 cursor-pointer" onClick={() => setPermanent(!permanent)}>
              {permanent ? "Always allow for this location" : "Ask me next time"}
            </label>
          </div>
        </div>

        {/* Buttons */}
        <div className="border-t border-line bg-panel2 px-6 py-4 rounded-b-xl flex gap-3 justify-end">
          <button
            className="px-4 py-2 rounded-lg border border-line text-slate-300 text-xs font-semibold hover:bg-panel disabled:opacity-60"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 rounded-lg bg-neon text-slate-900 text-xs font-semibold hover:bg-neon/90 disabled:opacity-60"
            onClick={() => {
              onAllow(permission.capability, permission.path, permanent);
            }}
            disabled={loading}
          >
            {loading ? "Processing..." : permanent ? "Always Allow" : "Allow Once"}
          </button>
        </div>
      </div>
    </div>
  );
}
