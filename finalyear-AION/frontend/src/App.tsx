import { useEffect, useState } from "react";
import FloatingAssistant from "./components/FloatingAssistant";
import Onboarding from "./components/Onboarding";
import { fetchMemory } from "./services/api";

export default function App() {
  const [ready, setReady] = useState(false);
  const [needsOnboarding, setNeedsOnboarding] = useState(true);

  useEffect(() => {
    fetchMemory()
      .then((data) => {
        const name = data?.preferences?.user_name;
        setNeedsOnboarding(!name);
      })
      .catch(() => setNeedsOnboarding(true))
      .finally(() => setReady(true));
  }, []);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_#24344a,_#0b1118_45%,_#05080c)] text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-5xl items-center justify-center px-4">
        {ready && (needsOnboarding ? <Onboarding onDone={() => setNeedsOnboarding(false)} /> : <FloatingAssistant />)}
      </div>
    </main>
  );
}
