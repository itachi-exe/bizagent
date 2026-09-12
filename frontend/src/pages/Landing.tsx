import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";

const activities = [
  { color: "bg-[#5a7a5a]", title: "Order #BA-2048 created", detail: "Ama Mensah · NGN 84,500 · 2 min ago" },
  { color: "bg-[#4a6fa5]", title: "Product availability confirmed", detail: "Honeycomb Gift Set · 8 min ago" },
  { color: "bg-[#d6a84b]", title: "Conversation escalated", detail: "Custom wholesale enquiry · 14 min ago" },
  { color: "bg-[#5a7a5a]", title: "New lead qualified", detail: "Kofi Asare · 21 min ago" },
  { color: "bg-[#4a6fa5]", title: "Quote Q-1042 sent", detail: "Honey starter kit · 28 min ago" },
  { color: "bg-[#5a7a5a]", title: "Payment confirmed", detail: "Order #BA-2046 · 34 min ago" },
];

export default function Landing() {
  return (
    <main className="min-h-screen bg-[#0a0a0a] text-white">

      {/* Hero */}
      <section className="relative flex h-screen flex-col items-start justify-center overflow-hidden bg-[url('/assets/bizagent-bg.jpg')] bg-cover bg-bottom">
        <Navbar landing />
        <div className="relative w-full px-6 lg:-mt-32 lg:px-20">
          <p className="mb-7 text-[10px] font-medium uppercase tracking-[0.3em] text-[#9a9a8a]">
            WhatsApp-native business operations
          </p>
          <h1 className="max-w-5xl text-4xl font-light leading-[1.05] tracking-tight text-[#1a1a1a] sm:text-5xl md:text-6xl lg:text-8xl">
            Your business already runs on WhatsApp. Now your AI can run there too.
          </h1>
          <p className="mt-8 max-w-xl text-base font-light leading-8 text-[#555] lg:text-lg">
            BizAgent is an AI employee that knows your products, enforces your
            policies, and creates real orders. Directly in WhatsApp.
          </p>
          <Link
            to="/settings/bot"
            className="mt-12 inline-block w-full bg-[#1a1a1a] px-8 py-3.5 text-center text-xs uppercase tracking-[0.12em] text-white transition-colors hover:bg-[#333] sm:w-auto"
          >
            Get Started
          </Link>
        </div>
      </section>

      {/* Pillars */}
      <div className="border-t border-white/[0.06]" />
      <section className="mx-auto max-w-6xl px-6 py-20 md:py-32 lg:px-10 lg:py-40">
        <p className="mb-12 text-[10px] font-medium uppercase tracking-[0.2em] text-white/40">
          Not a chatbot. An AI employee.
        </p>
        <div className="grid grid-cols-1 gap-12 md:grid-cols-3 lg:gap-20">
          <Pillar number="01" title="Quotes real prices" text="Pulls from your live inventory, never guesses." />
          <Pillar number="02" title="Creates actual orders" text="Writes to your database, not just says so." />
          <Pillar number="03" title="Knows its limits" text="Escalates to a human when it should." />
        </div>
      </section>

      {/* Dashboard mockup section */}
      <div className="mx-auto max-w-6xl border-t border-white/[0.06]" />
      <section className="mx-auto max-w-6xl px-6 py-20 md:py-32 lg:px-10 lg:py-40">
        <p className="mb-7 text-[10px] font-medium uppercase tracking-[0.2em] text-white/40">
          The operating layer
        </p>
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-[1fr_1.4fr] lg:gap-20">
          <div>
            <h2 className="text-4xl font-light leading-[1.08] tracking-tight md:text-5xl lg:text-6xl">
              Clarity for every conversation.
            </h2>
            <p className="mt-8 max-w-md text-base font-light leading-7 text-white/50">
              See what your agent is doing, where customers need a person, and
              what is moving through your business. All from one quiet workspace.
            </p>
          </div>
          <DashboardMockup />
        </div>
      </section>

      <footer className="border-t border-white/[0.06] px-6 py-10 text-xs text-white/25 lg:px-10">
        2026 BizAgent
      </footer>
    </main>
  );
}

function Pillar({ number, title, text }: { number: string; title: string; text: string }) {
  return (
    <article>
      <div className="mb-6 text-[10px] tracking-[0.3em] text-white/25">{number}</div>
      <h2 className="text-2xl font-light text-white">{title}</h2>
      <p className="mt-3 text-base leading-8 text-white/45">{text}</p>
    </article>
  );
}

function DashboardMockup() {
  return (
    <div className="border border-white/[0.06] bg-[#0d0d0d] p-5 md:p-8">
      <div className="mb-8 flex items-center justify-between">
        <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-white/40">Owner dashboard</span>
        <span className="flex items-center gap-2 text-xs text-[#5a7a5a]">
          <span className="h-1.5 w-1.5 bg-[#5a7a5a]" />
          Live
        </span>
      </div>
      <div className="grid grid-cols-2 border-y border-white/[0.06] py-5 sm:grid-cols-4">
        <MockStat value="128" label="Conversations" />
        <MockStat value="24" label="Orders" />
        <MockStat value="03" label="Escalations" />
        <MockStat value="41" label="Leads" />
      </div>
      <div className="mt-4">
        {activities.map((activity) => (
          <div
            key={activity.title}
            className="flex items-center gap-4 border-b border-white/[0.06] py-3.5 last:border-b-0"
          >
            <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${activity.color}`} />
            <div className="min-w-0">
              <p className="truncate text-sm text-white/80">{activity.title}</p>
              <p className="mt-0.5 truncate text-xs text-white/35">{activity.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MockStat({ value, label }: { value: string; label: string }) {
  return (
    <div className="border-r border-white/[0.06] px-4 first:pl-0 last:border-r-0 last:pr-0">
      <div className="text-2xl font-light text-white">{value}</div>
      <div className="mt-1.5 text-[9px] font-medium uppercase tracking-[0.18em] text-white/35">{label}</div>
    </div>
  );
}
