import { type ChangeEvent, useState } from "react";
import { savePreference } from "../services/api";

type Props = { onDone: () => void };

export default function Onboarding({ onDone }: Props) {
  const [name, setName] = useState("");
  const [folders, setFolders] = useState<string[]>(["Downloads", "Documents"]);
  const [capabilities, setCapabilities] = useState<string[]>([
    "file_access",
    "application_access",
    "browser_access"
  ]);

  const toggle = (value: string, current: string[], setter: (next: string[]) => void) => {
    if (current.includes(value)) {
      setter(current.filter((v) => v !== value));
      return;
    }
    setter([...current, value]);
  };

  const complete = async () => {
    await savePreference("user_name", name || "User");
    await savePreference("approved_folders", JSON.stringify(folders));
    await savePreference("enabled_capabilities", JSON.stringify(capabilities));
    onDone();
  };

  return (
    <div className="fixed bottom-6 right-6 w-[380px] max-w-[92vw] rounded-card border border-line bg-panel/95 p-4 shadow-float">
      <p className="text-xs uppercase tracking-[0.2em] text-neon">AION</p>
      <h2 className="mb-2 mt-1 text-lg font-semibold text-slate-100">Welcome to AION</h2>
      <p className="mb-3 text-xs text-slate-300">I am your desktop companion. What should I call you?</p>
      <input
        className="mb-3 w-full rounded-lg border border-line bg-panel2 px-3 py-2 text-sm text-slate-100"
        value={name}
        onChange={(e: ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
        placeholder="Your name"
      />

      <p className="mb-2 text-xs text-slate-300">Which folders should I be allowed to work with?</p>
      <div className="mb-3 flex flex-wrap gap-2 text-xs">
        {["Downloads", "Documents", "Desktop"].map((folder) => (
          <button
            key={folder}
            className={`rounded-full border px-3 py-1 ${
              folders.includes(folder)
                ? "border-neon text-neon"
                : "border-line text-slate-400"
            }`}
            onClick={() => toggle(folder, folders, setFolders)}
          >
            {folder}
          </button>
        ))}
      </div>

      <p className="mb-2 text-xs text-slate-300">Which capabilities should I enable?</p>
      <div className="mb-4 flex flex-wrap gap-2 text-xs">
        {[
          ["file_access", "File management"],
          ["application_access", "App launching"],
          ["browser_access", "Browser automation"]
        ].map(([value, label]) => (
          <button
            key={value}
            className={`rounded-full border px-3 py-1 ${
              capabilities.includes(value)
                ? "border-good text-good"
                : "border-line text-slate-400"
            }`}
            onClick={() => toggle(value, capabilities, setCapabilities)}
          >
            {label}
          </button>
        ))}
      </div>

      <button className="rounded-lg bg-neon px-3 py-2 text-xs font-semibold text-slate-900" onClick={complete}>
        Get Started
      </button>
    </div>
  );
}
