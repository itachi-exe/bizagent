import { useEffect, useState } from "react";
import useSWR from "swr";
import Navbar from "../components/Navbar";
import StatTile from "../components/StatTile";
import ActivityFeed from "../components/ActivityFeed";
import BrainPanel from "../components/BrainPanel";
import KnowledgeGapsPanel from "../components/KnowledgeGapsPanel";
import { api, type PendingOrder } from "../api/client";
import { useActivityStream } from "../hooks/useActivityStream";
export default function Dashboard() {
  const { events, connected } = useActivityStream();
  const { data } = useSWR("summary", api.getSummary);
  const pending = useSWR("pending", api.getPendingFulfillment);
  const [showInitialSkeleton, setShowInitialSkeleton] = useState(true);
  const [summaryLoadedFromApi, setSummaryLoadedFromApi] = useState(false);
  useEffect(() => {
    const timer = window.setTimeout(() => setShowInitialSkeleton(false), 200);
    return () => window.clearTimeout(timer);
  }, []);
  const summary = data ?? { conversations: 12, orders: 4, escalations: 2, leads: 8 };
  useEffect(() => {
    setSummaryLoadedFromApi(data !== undefined);
  }, [data]);
  const isFallbackSummary =
    !summaryLoadedFromApi &&
    summary.conversations === 12 &&
    summary.orders === 4 &&
    summary.escalations === 2 &&
    summary.leads === 8;
  const showDemoMode = !connected && isFallbackSummary;
  return (
    <main className="min-h-screen bg-[#0d0d0d]">
      <Navbar />
      <div className="mx-auto max-w-6xl px-12 py-14">
        <div className="mb-12 flex items-center justify-between">
          <div>
            <p className="section-label">Owner dashboard</p>
            <h1 className="mt-3 text-4xl font-light">Your agent at work</h1>
          </div>
          <span
            className={
              showDemoMode
                ? "text-xs text-[rgba(255,255,255,0.3)]"
                : `text-sm ${connected ? "text-green" : "text-secondary"}`
            }
          >
            <span
              className={`mr-2 inline-block h-2 w-2 rounded-full ${connected ? "animate-pulse bg-green" : showDemoMode ? "bg-[rgba(255,255,255,0.3)]" : "bg-secondary"}`}
            />
            {connected ? "Live" : showDemoMode ? "Demo mode" : "Connecting"}
          </span>
        </div>
        <section className="panel grid grid-cols-4">
          {data || !showInitialSkeleton ? (
            <>
              <StatTile
                value={
                  summary.conversations_today ?? summary.conversations ?? 0
                }
                label="Conversations"
                detail="Today"
              />
              <StatTile
                value={summary.orders_today ?? summary.orders ?? 0}
                label="Orders"
                detail={
                  summary.orders_total_ngn
                    ? `NGN ${Number(summary.orders_total_ngn).toLocaleString()}`
                    : "Today"
                }
              />
              <StatTile
                value={summary.open_escalations ?? summary.escalations ?? 0}
                label="Escalations"
                detail="Open"
              />
              <StatTile
                value={summary.leads_today ?? summary.leads ?? 0}
                label="Leads"
                detail="Today"
              />
            </>
          ) : (
            Array.from({ length: 4 }).map((_, i) => (
              <div className="p-8" key={i}>
                <div className="skeleton h-9 w-16" />
                <div className="skeleton mt-3 h-3 w-24" />
              </div>
            ))
          )}
        </section>
        <div className="mt-10 space-y-6">
          <ActivityFeed events={events} />
          <BrainPanel />
          <KnowledgeGapsPanel events={events} />
          <PendingPanel orders={pending.data} />
        </div>
      </div>
    </main>
  );
}
function PendingPanel({
  orders,
}: {
  orders?: PendingOrder[] | { orders: PendingOrder[] };
}) {
  const rows = Array.isArray(orders)
    ? orders
    : orders?.orders ?? [
        { order_ref: "ORD-KA-1031", customer_name: "Kunle", items: "1x Langstroth Beehive", total_ngn: 35000 },
        { order_ref: "ORD-AB-1032", customer_name: "Amaka", items: "2x Bee Smoker", total_ngn: 17000 },
      ];
  return (
    <section className="panel p-7">
      <div className="mb-5 flex justify-between">
        <h2 className="section-label">Pending Fulfillment</h2>
        <span className="section-label">{rows.length} awaiting</span>
      </div>
      {rows.length === 0 ? (
        <p className="border-t border-border pt-4 text-sm text-secondary">
          No orders awaiting fulfillment.
        </p>
      ) : (
        <div>
          {rows.map((order, i) => (
            <div
              key={order.id ?? i}
              className="flex items-center gap-4 border-t border-border py-5 text-sm"
            >
              <b className="font-medium">{order.order_ref}</b>
              <span>
                {order.customer_name} · {order.items} · NGN{" "}
                {Number(order.total_ngn).toLocaleString()}
              </span>
              <button
                onClick={() =>
                  navigator.clipboard?.writeText(`/deliver ${order.order_ref} `)
                }
                className="button-outline ml-auto py-1.5 text-[10px] uppercase tracking-[0.1em]"
              >
                Copy command
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
