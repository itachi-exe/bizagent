import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";

const activities = [
  {
    color: "bg-green",
    title: "Order #BA-2048 created",
    detail: "Ama Mensah · NGN 84,500 · 2 min ago",
  },
  {
    color: "bg-blue",
    title: "Product availability confirmed",
    detail: "Honeycomb Gift Set · 8 min ago",
  },
  {
    color: "bg-[#d6a84b]",
    title: "Conversation escalated",
    detail: "Custom wholesale enquiry · 14 min ago",
  },
  {
    color: "bg-green",
    title: "New lead qualified",
    detail: "Kofi Asare · 21 min ago",
  },
  {
    color: "bg-blue",
    title: "Quote Q-1042 sent",
    detail: "Honey starter kit · 28 min ago",
  },
  {
    color: "bg-green",
    title: "Payment confirmed",
    detail: "Order #BA-2046 · 34 min ago",
  },
];

export default function Landing() {
  return (
    <main className="min-h-screen bg-bg">
      <section className="relative h-screen flex flex-col items-center justify-center overflow-hidden bg-[url('/assets/bizagent-bg.jpg')] bg-cover bg-bottom">
        <Navbar landing />
        <div className="relative mx-auto w-full max-w-6xl px-14 -mt-32">
          <p className="mb-7 text-[10px] font-medium uppercase tracking-[0.3em] text-[#9a9a8a]">
            WhatsApp-native business operations
          </p>
          <h1 className="max-w-5xl text-7xl font-light leading-[1.05] tracking-tight text-[#1a1a1a] lg:text-8xl">
            Your business already runs on WhatsApp. Now your AI can run there
            too.
          </h1>
          <p className="mt-8 max-w-xl text-lg font-light leading-8 text-[#555]">
            BizAgent is an AI employee that knows your products, enforces your
            policies, and creates real orders. Directly in WhatsApp.
          </p>
          <Link
            to="/settings/bot"
            className="mt-12 inline-block px-8 py-3 bg-[#1a1a1a] text-white text-xs uppercase tracking-[0.12em] hover:bg-[#333] transition-colors"
          >
            Request Access
          </Link>
        </div>
      </section>
      <div className="border-t border-[rgba(255,255,255,0.06)]" />
      <section className="mx-auto max-w-6xl px-10 py-40">
        <p className="section-label mb-8 border-t border-[rgba(255,255,255,0.05)] pt-8">Not a chatbot. An AI employee.</p>
        <div className="mt-0 grid grid-cols-3 gap-20">
          <Pillar
            number="01"
            title="Quotes real prices"
            text="Pulls from your live inventory, never guesses."
          />
          <Pillar
            number="02"
            title="Creates actual orders"
            text="Writes to your database, not just says so."
          />
          <Pillar
            number="03"
            title="Knows its limits"
            text="Escalates to a human when it should."
          />
        </div>
      </section>
      <div className="mx-auto max-w-6xl border-t border-[rgba(255,255,255,0.06)]" />
      <section className="mx-auto max-w-6xl px-10 py-40">
        <p className="section-label">The operating layer</p>
        <div className="mt-7 grid grid-cols-[1fr_1.4fr] gap-20">
          <div>
            <h2 className="text-5xl font-light leading-[1.08] tracking-tight lg:text-6xl">
              Clarity for every conversation.
            </h2>
            <p className="mt-8 max-w-md text-base font-light leading-7 text-primary/70">
              See what your agent is doing, where customers need a person, and
              what is moving through your business, all from one quiet
              workspace.
            </p>
          </div>
          <DashboardMockup />
        </div>
      </section>
      <footer className="border-t border-[rgba(255,255,255,0.06)] px-10 py-10 text-xs text-secondary">
        © 2026 BizAgent
      </footer>
    </main>
  );
}

function Pillar({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <article>
      <div className="mb-6 text-[10px] tracking-[0.3em] text-[rgba(255,255,255,0.25)]">{number}</div>
      <h2 className="text-2xl font-light">{title}</h2>
      <p className="mt-3 text-base leading-8 text-[rgba(255,255,255,0.45)]">{text}</p>
    </article>
  );
}

function DashboardMockup() {
  return (
    <div className="border border-[rgba(255,255,255,0.06)] bg-[#0d0d0d] p-10">
      <div className="mb-9 flex items-center justify-between">
        <span className="section-label">Owner dashboard</span>
        <span className="text-xs text-green">
          <span className="mr-2 inline-block h-1.5 w-1.5 bg-green" />
          Live
        </span>
      </div>
      <div className="grid grid-cols-4 border-y border-[rgba(255,255,255,0.06)] py-6">
        <MockStat value="128" label="Conversations" />
        <MockStat value="24" label="Orders" />
        <MockStat value="03" label="Escalations" />
        <MockStat value="41" label="Leads" />
      </div>
      <div className="mt-4">
        {activities.map((activity) => (
          <div
            key={activity.title}
            className="flex items-center gap-4 border-b border-[rgba(255,255,255,0.06)] py-4 last:border-b-0"
          >
            <span className={`h-2 w-2 shrink-0 ${activity.color}`} />
            <div>
              <p className="text-sm text-primary">{activity.title}</p>
              <p className="mt-1 text-xs text-secondary">{activity.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MockStat({ value, label }: { value: string; label: string }) {
  return (
    <div className="border-r border-[rgba(255,255,255,0.06)] px-4 first:pl-0 last:border-r-0 last:pr-0">
      <div className="text-2xl font-light">{value}</div>
      <div className="section-label mt-2">{label}</div>
    </div>
  );
}
