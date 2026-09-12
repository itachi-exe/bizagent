import { Link, useLocation } from "react-router-dom";
import { Moon, Sun } from "lucide-react";
import { useState } from "react";
import { useTheme } from "../context/ThemeContext";
export default function Navbar({ landing = false }: { landing?: boolean }) {
  const { pathname } = useLocation();
  const { theme, toggle } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const links = [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/settings/bot", label: "Bot Settings" },
    { to: "/settings/upload", label: "Upload Database" },
  ];
  return (
    <header
      className={`flex items-center justify-between px-4 md:px-10 ${landing ? "absolute inset-x-0 top-0 z-10 h-16" : "relative sticky top-0 z-10 h-14 border-b border-[var(--app-border)] bg-[var(--app-surface)]"}`}
    >
      <Link
        to="/"
        className={`text-[11px] font-normal tracking-[0.25em] ${landing ? "text-[#1a1a1a]" : "text-[var(--app-ink)]"}`}
      >
        BIZAGENT
      </Link>
      {landing ? (<>
        <Link to="/settings/bot" className="hidden text-xs uppercase tracking-[0.12em] px-5 py-2.5 bg-[#1a1a1a] text-white hover:bg-[#333] transition-colors md:block">
          Get Started
        </Link>
        <button onClick={() => setMenuOpen(open => !open)} className="text-2xl leading-none text-[#1a1a1a] md:hidden" aria-label="Toggle navigation" aria-expanded={menuOpen}>☰</button>
      </>) : (<>
        <div className="hidden items-center gap-8 md:flex">
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
        <button onClick={() => setMenuOpen(open => !open)} className="text-2xl leading-none text-[var(--app-ink)] md:hidden" aria-label="Toggle navigation" aria-expanded={menuOpen}>☰</button>
      </>)}
      <div className={`absolute inset-x-0 top-full border-b border-[var(--app-border)] bg-[var(--app-surface)] transition-all duration-200 md:hidden ${menuOpen ? "visible translate-y-0 opacity-100" : "invisible -translate-y-3 opacity-0"}`}>
        <nav className="flex flex-col px-4 py-4">
          {landing ? <Link to="/settings/bot" onClick={() => setMenuOpen(false)} className="py-3 text-xs uppercase tracking-[0.12em] text-[var(--app-ink)]">Get Started</Link> : <>
            {links.map(link => <Link key={link.to} to={link.to} onClick={() => setMenuOpen(false)} className={`py-3 text-xs uppercase tracking-[0.12em] ${pathname === link.to ? "text-[var(--app-ink)]" : "text-[var(--app-muted)]"}`}>{link.label}</Link>)}
            <button onClick={toggle} className="flex items-center gap-2 py-3 text-left text-xs uppercase tracking-[0.12em] text-[var(--app-muted)]">{theme === "light" ? <Moon size={14} /> : <Sun size={14} />} Toggle theme</button>
          </>}
        </nav>
      </div>
    </header>
  );
}
