import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import ToneSelector from "../components/ToneSelector";
import WhatsAppPreview from "../components/WhatsAppPreview";
import { api, type BotSettings } from "../api/client";
const defaults: BotSettings = {
  agent_name: "Zara",
  agent_personality:
    "Warm and knowledgeable about beekeeping. You speak to customers like a helpful friend who happens to know everything about bees.",
  agent_greeting:
    "Hi there! 🐝 I'm Zara from Macaney. How can I help you today?",
  agent_language_style: "friendly",
};
const businessTypes = [
  "Retail",
  "Wholesale",
  "School",
  "Hospital",
  "Clinic",
  "Events",
  "Restaurant",
  "Services",
  "Real Estate",
  "Logistics",
];
export default function BotSettings() {
  const [form, setForm] = useState(defaults);
  const [type, setType] = useState("Retail");
  const [extended, setExtended] = useState<Record<string, string>>({});
  const [status, setStatus] = useState("");
  useEffect(() => {
    api
      .getBotSettings()
      .then(setForm)
      .catch(() => undefined);
    api
      .getExtendedBrain()
      .then((v) => {
        if (v.business_type) setType(v.business_type);
        setExtended(v);
      })
      .catch(() => undefined);
  }, []);
  const edit = (field: keyof BotSettings, value: string) =>
    setForm((v) => ({ ...v, [field]: value }));
  const save = async () => {
    setStatus("");
    try {
      await Promise.all([
        api.updateBotSettings(form),
        api.updateExtendedBrain({ business_type: type, ...extended }),
      ]);
      setStatus("Saved ✓");
      setTimeout(() => setStatus(""), 2000);
    } catch {
      setStatus("Could not save changes. Please try again.");
    }
  };
  const fields =
    type === "School"
      ? ["Term dates", "Admission requirements", "Fee structure"]
      : type === "Restaurant"
        ? ["Menu", "Opening hours", "Delivery areas"]
        : type === "Logistics"
          ? ["Service areas", "Rate card", "Delivery times"]
          : ["Business policies", "Operating hours"];
  return (
    <main className="min-h-screen bg-[#0d0d0d]">
      <Navbar />
    <div className="mx-auto max-w-6xl px-12 py-14">
        <p className="section-label">Agent configuration</p>
      <h1 className="mt-3 text-4xl font-light">Bot Identity</h1>
      <div className="mt-10 grid grid-cols-[1.1fr_.9fr] gap-10">
        <section className="panel divide-y divide-[rgba(255,255,255,0.04)] p-10">
            <Field
              label="Bot Name"
              help="This is the name your bot uses when greeting customers."
              count={`${form.agent_name.length}/40`}
            >
              <input
                maxLength={40}
                value={form.agent_name}
                onChange={(e) => edit("agent_name", e.target.value)}
                className="input"
              />
            </Field>
            <Field
              label="Personality"
              help="Describe your bot's character."
              count={`${form.agent_personality.length}/500`}
            >
              <textarea
                maxLength={500}
                rows={5}
                value={form.agent_personality}
                onChange={(e) => edit("agent_personality", e.target.value)}
                className="input resize-none"
              />
            </Field>
            <Field
              label="Greeting Message"
              help="Sent automatically when a new customer messages you. Leave empty to skip the greeting."
              count={`${form.agent_greeting.length}/300`}
            >
              <textarea
                maxLength={300}
                rows={3}
                value={form.agent_greeting}
                onChange={(e) => edit("agent_greeting", e.target.value)}
                className="input resize-none"
              />
            </Field>
            <div className="py-7">
              <label className="mb-3 block text-xs uppercase tracking-[0.1em] text-secondary">Tone</label>
              <ToneSelector
                value={form.agent_language_style}
                onChange={(value) => edit("agent_language_style", value)}
              />
            </div>
            <div className="mt-2 border-t border-[rgba(255,255,255,0.04)] pt-7">
              <label className="mb-3 block text-xs uppercase tracking-[0.1em] text-secondary">Business Type</label>
              <div className="flex flex-wrap gap-2">
                {businessTypes.map((item) => (
                  <button
                    key={item}
                    onClick={() => setType(item)}
                    className={`rounded-none border px-4 py-2 text-xs ${type === item ? "border-green bg-green/5 text-green" : "border-[rgba(255,255,255,0.1)] text-[rgba(255,255,255,0.4)]"}`}
                  >
                    {item}
                  </button>
                ))}
              </div>
              <div className="mt-5 grid grid-cols-2 gap-4">
                {fields.map((field) => (
                  <label key={field} className="text-xs uppercase tracking-[0.1em] text-secondary">
                    {field}
                    <input
                      value={extended[field] ?? ""}
                      onChange={(e) =>
                        setExtended((v) => ({ ...v, [field]: e.target.value }))
                      }
                      className="input mt-2"
                    />
                  </label>
                ))}
              </div>
            </div>
            <div className="flex items-center justify-end gap-4 pt-7">
              <span
                className={
                  status.startsWith("Saved")
                    ? "text-sm text-green"
                    : "text-sm text-red"
                }
              >
                {status}
              </span>
              <button onClick={save} className="button-primary">
                Save Changes
              </button>
            </div>
          </section>
          <aside>
            <p className="section-label mb-3">Live preview</p>
            <WhatsAppPreview settings={form} />
          </aside>
        </div>
      </div>
    </main>
  );
}
function Field({
  label,
  help,
  count,
  children,
}: {
  label: string;
  help: string;
  count: string;
  children: React.ReactNode;
}) {
  return (
    <div className="py-7 first:pt-0">
      <label className="mb-2 block text-xs uppercase tracking-[0.1em] text-secondary">{label}</label>
      {children}
      <div className="mt-2 flex justify-between text-xs text-secondary">
        <span>{help}</span>
        <span>{count}</span>
      </div>
    </div>
  );
}
