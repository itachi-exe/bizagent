import { useEffect, useState, type ReactNode } from "react";
import Navbar from "../components/Navbar";
import ToneSelector from "../components/ToneSelector";
import WhatsAppPreview from "../components/WhatsAppPreview";
import {
  api,
  type BotSettings,
  type BusinessSettings,
  type PermissionSettings,
  type PolicySettings,
} from "../api/client";

const botDefaults: BotSettings = {
  agent_name: "Zara",
  agent_personality:
    "Warm and knowledgeable about beekeeping. You speak to customers like a helpful friend who happens to know everything about bees.",
  agent_greeting: "Hi there! 🐝 I'm Zara from Macaney. How can I help you today?",
  agent_language_style: "friendly",
};
const businessDefaults: BusinessSettings = {
  business_name: "",
  tagline: "",
  location: "",
  opening_hours: "",
  contact_email: "",
  business_type: "Retail",
  whatsapp_number: "",
  owner_phone: "",
};
const policyDefaults: PolicySettings = {
  delivery_policy: "",
  returns_policy: "",
  payment_methods: [],
  cancellation_policy: "",
  max_discount_ceiling: 0,
};
const permissionDefaults: PermissionSettings = {
  can_create_orders: false,
  can_create_quotes: false,
  can_confirm_delivery_date: false,
  negotiation_enabled: false,
  max_discount_agent_can_approve: 0,
  markup: 0,
  floor: 0,
  escalate_on: [],
};

const tabs = ["Bot Identity", "Business Profile", "Policies", "Permissions"] as const;
type Tab = (typeof tabs)[number];

const businessTypes = [
  "Retail", "Wholesale", "School", "Hospital", "Clinic",
  "Events", "Restaurant", "Services", "Real Estate", "Logistics",
];
const paymentMethods = ["Cash", "Bank Transfer", "Card", "POS", "USSD", "Crypto"];
const escalationOptions = ["out_of_stock", "price_complaint", "rude_customer", "refund_request", "complaint"];

export default function BotSettings() {
  const [activeTab, setActiveTab] = useState<Tab>("Bot Identity");
  const [bot, setBot] = useState(botDefaults);
  const [business, setBusiness] = useState(businessDefaults);
  const [policies, setPolicies] = useState(policyDefaults);
  const [permissions, setPermissions] = useState(permissionDefaults);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("");

  useEffect(() => {
    let live = true;
    setLoading(true);
    const load = async () => {
      try {
        if (activeTab === "Bot Identity") {
          const v = await api.getBotSettings();
          if (live) setBot(v as BotSettings);
        } else if (activeTab === "Business Profile") {
          const v = await api.getBusiness();
          if (live) setBusiness(v as BusinessSettings);
        } else if (activeTab === "Policies") {
          const v = await api.getPolicies();
          if (live) setPolicies(v as PolicySettings);
        } else {
          const v = await api.getPermissions();
          if (live) setPermissions(v as PermissionSettings);
        }
      } catch {
        /* defaults remain */
      } finally {
        if (live) setLoading(false);
      }
    };
    load();
    return () => { live = false; };
  }, [activeTab]);

  useEffect(() => {
    if (status !== "Saved") return;
    const t = window.setTimeout(() => setStatus(""), 2000);
    return () => window.clearTimeout(t);
  }, [status]);

  const save = async () => {
    setStatus("");
    try {
      if (activeTab === "Bot Identity") await api.updateBotSettings(bot);
      else if (activeTab === "Business Profile") await api.updateBusiness(business);
      else if (activeTab === "Policies") await api.updatePolicies(policies);
      else await api.updatePermissions(permissions);
      setStatus("Saved");
    } catch {
      setStatus("Could not save changes. Please try again.");
    }
  };

  return (
    <main className="min-h-screen bg-[var(--app-bg)] text-[var(--app-ink)]">
      <Navbar />

      <div className="mx-auto px-4 py-6 lg:px-10 lg:py-10">
        <p className="app-section-label">Agent configuration</p>
        <h1 className="mt-2 text-2xl font-light sm:text-3xl">Settings</h1>

        {/* Tabs — horizontally scrollable on mobile */}
        <div className="-mx-4 mt-8 overflow-x-auto px-4 md:mx-0 md:px-0" role="tablist">
          <div className="flex w-max gap-6 border-b border-[var(--app-border)] md:w-auto">
            {tabs.map((tab) => (
              <button
                key={tab}
                role="tab"
                aria-selected={activeTab === tab}
                onClick={() => { setActiveTab(tab); setStatus(""); }}
                className={`whitespace-nowrap pb-3 text-xs transition-colors sm:text-sm ${
                  activeTab === tab
                    ? "border-b-2 border-[var(--app-olive)] text-[var(--app-olive)]"
                    : "text-[var(--app-muted)] hover:text-[var(--app-ink)]"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Content grid: form (+ preview on Bot Identity) */}
        <div className={`mt-8 ${activeTab === "Bot Identity" ? "grid grid-cols-1 gap-6 lg:grid-cols-[1fr_400px]" : ""}`}>

          <section className="app-panel p-5 sm:p-8">
            {loading ? (
              <Skeleton />
            ) : activeTab === "Bot Identity" ? (
              <Identity form={bot} setForm={setBot} />
            ) : activeTab === "Business Profile" ? (
              <Business form={business} setForm={setBusiness} />
            ) : activeTab === "Policies" ? (
              <Policies form={policies} setForm={setPolicies} />
            ) : (
              <Permissions form={permissions} setForm={setPermissions} />
            )}

            {/* Footer actions */}
            <div className="mt-7 flex flex-col gap-3 border-t border-[var(--app-border)] pt-6 sm:flex-row sm:items-center sm:justify-end">
              {status && (
                <span className={`text-xs ${status === "Saved" ? "text-[var(--app-olive)]" : "text-red-400"}`}>
                  {status}
                </span>
              )}
              <button
                onClick={save}
                disabled={loading}
                className="app-btn-primary w-full disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
              >
                Save changes
              </button>
            </div>
          </section>

          {activeTab === "Bot Identity" && (
            <aside className="min-w-0">
              <p className="app-section-label mb-3">WhatsApp preview</p>
              <WhatsAppPreview settings={bot} />
            </aside>
          )}
        </div>
      </div>
    </main>
  );
}

/* ---- Tab forms ---- */

function Identity({ form, setForm }: { form: BotSettings; setForm: (v: BotSettings) => void }) {
  const edit = (field: keyof BotSettings, value: string) => setForm({ ...form, [field]: value });
  return (
    <>
      <Field label="Agent name" help="The name your bot uses when greeting customers." count={`${form.agent_name.length}/40`}>
        <input maxLength={40} value={form.agent_name} onChange={e => edit("agent_name", e.target.value)} className="app-input" />
      </Field>
      <Field label="Personality" help="Describe your bot's character." count={`${form.agent_personality.length}/500`}>
        <textarea maxLength={500} rows={5} value={form.agent_personality} onChange={e => edit("agent_personality", e.target.value)} className="app-input resize-none" />
      </Field>
      <Field label="Greeting message" help="Sent automatically when a new customer messages you." count={`${form.agent_greeting.length}/300`}>
        <textarea maxLength={300} rows={3} value={form.agent_greeting} onChange={e => edit("agent_greeting", e.target.value)} className="app-input resize-none" />
      </Field>
      <div>
        <label className="app-section-label mb-2 block">Language style</label>
        <ToneSelector value={form.agent_language_style} onChange={value => edit("agent_language_style", value)} />
      </div>
    </>
  );
}

function Business({ form, setForm }: { form: BusinessSettings; setForm: (v: BusinessSettings) => void }) {
  const edit = (field: keyof BusinessSettings, value: string) => setForm({ ...form, [field]: value });
  return (
    <div className="grid grid-cols-1 gap-x-5 sm:grid-cols-2">
      <Field label="Business name"><input value={form.business_name} onChange={e => edit("business_name", e.target.value)} className="app-input" /></Field>
      <Field label="Tagline"><input value={form.tagline} onChange={e => edit("tagline", e.target.value)} className="app-input" /></Field>
      <Field label="Location"><input value={form.location} onChange={e => edit("location", e.target.value)} className="app-input" /></Field>
      <Field label="Opening hours"><input value={form.opening_hours} onChange={e => edit("opening_hours", e.target.value)} className="app-input" /></Field>
      <Field label="Contact email"><input type="email" value={form.contact_email} onChange={e => edit("contact_email", e.target.value)} className="app-input" /></Field>
      <Field label="Business type">
        <select value={form.business_type} onChange={e => edit("business_type", e.target.value)} className="app-input">
          {businessTypes.map(t => <option key={t}>{t}</option>)}
        </select>
      </Field>
      <Field label="WhatsApp number"><input value={form.whatsapp_number} onChange={e => edit("whatsapp_number", e.target.value)} className="app-input" /></Field>
      <Field label="Owner phone"><input value={form.owner_phone} onChange={e => edit("owner_phone", e.target.value)} className="app-input" /></Field>
    </div>
  );
}

function Policies({ form, setForm }: { form: PolicySettings; setForm: (v: PolicySettings) => void }) {
  const edit = (field: keyof PolicySettings, value: string | number | string[]) =>
    setForm({ ...form, [field]: value } as PolicySettings);
  return (
    <>
      <Field label="Delivery policy"><textarea rows={4} value={form.delivery_policy} onChange={e => edit("delivery_policy", e.target.value)} className="app-input resize-none" /></Field>
      <Field label="Returns policy"><textarea rows={4} value={form.returns_policy} onChange={e => edit("returns_policy", e.target.value)} className="app-input resize-none" /></Field>
      <CheckGroup label="Payment methods" options={paymentMethods} selected={form.payment_methods} onChange={v => edit("payment_methods", v)} />
      <Field label="Cancellation policy"><textarea rows={4} value={form.cancellation_policy} onChange={e => edit("cancellation_policy", e.target.value)} className="app-input resize-none" /></Field>
      <Field label="Max discount ceiling %"><input type="number" min={0} max={100} value={form.max_discount_ceiling} onChange={e => edit("max_discount_ceiling", Number(e.target.value))} className="app-input" /></Field>
    </>
  );
}

function Permissions({ form, setForm }: { form: PermissionSettings; setForm: (v: PermissionSettings) => void }) {
  const toggle = (field: keyof PermissionSettings) => setForm({ ...form, [field]: !form[field] } as PermissionSettings);
  const number = (field: keyof PermissionSettings, value: number) => setForm({ ...form, [field]: value } as PermissionSettings);
  return (
    <>
      <div className="space-y-5">
        {(
          [
            ["Can create orders", "can_create_orders"],
            ["Can create quotes", "can_create_quotes"],
            ["Can confirm delivery date", "can_confirm_delivery_date"],
            ["Negotiation enabled", "negotiation_enabled"],
          ] as [string, keyof PermissionSettings][]
        ).map(([label, field]) => (
          <Toggle key={field} label={label} checked={Boolean(form[field])} onChange={() => toggle(field)} />
        ))}
      </div>
      <div className="mt-7 grid grid-cols-1 gap-4 sm:grid-cols-3">
        {(
          [
            ["Max discount agent can approve %", "max_discount_agent_can_approve"],
            ["Markup %", "markup"],
            ["Floor %", "floor"],
          ] as [string, keyof PermissionSettings][]
        ).map(([label, field]) => (
          <Field key={field} label={label}>
            <input type="number" min={0} max={100} value={form[field] as number} onChange={e => number(field, Number(e.target.value))} className="app-input" />
          </Field>
        ))}
      </div>
      <CheckGroup label="Escalate on" options={escalationOptions} selected={form.escalate_on} onChange={v => setForm({ ...form, escalate_on: v })} />
    </>
  );
}

/* ---- Shared primitives ---- */

function Field({ label, help, count, children }: { label: string; help?: string; count?: string; children: ReactNode }) {
  return (
    <div className="mb-6">
      <label className="app-section-label mb-2 block">{label}</label>
      {children}
      {(help || count) && (
        <div className="mt-1.5 flex justify-between text-xs text-[var(--app-muted)]">
          <span>{help}</span>
          <span>{count}</span>
        </div>
      )}
    </div>
  );
}

function CheckGroup({ label, options, selected, onChange }: { label: string; options: string[]; selected: string[]; onChange: (v: string[]) => void }) {
  return (
    <div className="mb-6">
      <p className="app-section-label mb-3">{label}</p>
      <div className="flex flex-wrap gap-x-5 gap-y-3">
        {options.map(option => (
          <label key={option} className="flex cursor-pointer items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={selected.includes(option)}
              onChange={() =>
                onChange(selected.includes(option) ? selected.filter(x => x !== option) : [...selected, option])
              }
              className="accent-[var(--app-olive)]"
            />
            {option}
          </label>
        ))}
      </div>
    </div>
  );
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: () => void }) {
  return (
    <label className="flex cursor-pointer items-center justify-between text-sm">
      <span className="text-[var(--app-ink)]">{label}</span>
      <input className="peer sr-only" type="checkbox" checked={checked} onChange={onChange} />
      <span className="relative h-6 w-11 shrink-0 rounded-full bg-[var(--app-border)] transition-colors after:absolute after:left-1 after:top-1 after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-transform peer-checked:bg-[var(--app-olive)] peer-checked:after:translate-x-5" />
    </label>
  );
}

function Skeleton() {
  return (
    <div className="space-y-6">
      {[1, 2, 3, 4].map(i => (
        <div key={i} className="space-y-2">
          <div className="h-3 w-28 animate-pulse rounded bg-[var(--app-skeleton)]" />
          <div className="h-10 animate-pulse rounded bg-[var(--app-skeleton)]" />
        </div>
      ))}
    </div>
  );
}
