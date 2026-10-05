type Props = {
  itemPath: string;
  itemType: "file" | "folder";
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
};

export default function DeleteConfirmDialog({
  itemPath,
  itemType,
  onConfirm,
  onCancel,
  loading = false
}: Props) {
  const fileName = itemPath.split("\\").pop() || itemPath.split("/").pop() || "item";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-96 max-w-[90vw] rounded-xl border border-danger bg-panel shadow-xl">
        {/* Header */}
        <div className="border-b border-danger bg-gradient-to-r from-[#3d2621] via-[#5c3636] to-[#2d1818] px-6 py-4 rounded-t-xl">
          <h2 className="text-sm font-semibold text-danger uppercase tracking-wider">⚠ Confirm Deletion</h2>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Warning */}
          <div className="bg-danger/10 border border-danger/30 rounded-lg p-4">
            <p className="text-sm text-danger font-semibold mb-1">Permanent Action</p>
            <p className="text-xs text-slate-300 leading-relaxed">
              This action will permanently delete the {itemType}. This cannot be undone.
            </p>
          </div>

          {/* Item Details */}
          <div className="bg-panel2 rounded-lg p-4 border border-line">
            <p className="text-xs uppercase tracking-widest text-slate-400 mb-2">Item to Delete</p>
            <p className="text-sm font-mono text-slate-200 break-all line-clamp-2">{itemPath}</p>
            <p className="text-xs text-slate-400 mt-2 capitalize">{itemType}</p>
          </div>

          {/* Additional Warning */}
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
            <p className="text-xs text-yellow-200 leading-relaxed">
              Make sure you want to delete <span className="font-semibold">"{fileName}"</span> before confirming.
            </p>
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
            className="px-4 py-2 rounded-lg bg-danger text-white text-xs font-semibold hover:bg-danger/90 disabled:opacity-60"
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? "Deleting..." : "Yes, Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}
