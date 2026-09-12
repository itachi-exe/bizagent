import { Link, useLocation } from "react-router-dom";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "../context/ThemeContext";
export default function Navbar({ landing = false }: { landing?: boolean }) {
  const { pathname } = useLocation();
  const { theme, toggle } = useTheme();
  const links = [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/settings/bot", label: "Bot Settings" },
    { to: "/settings/upload", label: "Upload Database" },
  ];
  return (
    <header
      className={`flex items-center justify-between px-10 ${landing ? "absolute inset-x-0 top-0 z-10 h-16" : "sticky top-0 z-10 h-14 border-b border-[var(--app-border)] bg-[var(--app-surface)]"}`}
    >
      <Link
        to="/"
        className={`text-[11px] font-normal tracking-[0.25em] ${landing ? "text-[#1a1a1a]" : "text-[var(--app-ink)]"}`}
      >
        BIZAGENT
      </Link>
      {landing ? (
        <Link to="/settings/bot" className="text-xs uppercase tracking-[0.12em] px-5 py-2.5 bg-[#1a1a1a] text-white hover:bg-[#333] transition-colors">
          Request Access
        </Link>
      ) : (
        <div className="flex items-center gap-8">
          <span className="text-xs text-[var(--app-muted)]">
            Macaney Sustainable Solutions
          </span>
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`text-[10px] uppercase tracking-[0.18em] ${pathname === link.to ? "text-[var(--app-ink)]" : "text-[var(--app-muted)] hover:text-[var(--app-ink)]"}`}
            >
              {link.label}
            </Link>
          ))}
          <button
            onClick={toggle}
            className="flex h-8 w-8 items-center justify-center border border-[var(--app-border)] text-[var(--app-muted)] transition-colors hover:text-[var(--app-ink)]"
            aria-label="Toggle theme"
          >
            {theme === "light" ? <Moon size={14} /> : <Sun size={14} />}
          </button>
        </div>
      )}
    </header>
  );
}
