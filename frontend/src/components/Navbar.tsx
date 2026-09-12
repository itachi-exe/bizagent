import { Link, useLocation } from "react-router-dom";
export default function Navbar({ landing = false }: { landing?: boolean }) {
  const { pathname } = useLocation();
  const links = [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/settings/bot", label: "Bot Settings" },
    { to: "/settings/upload", label: "Upload Database" },
  ];
  return (
    <header
      className={`flex items-center justify-between px-10 ${landing ? "absolute inset-x-0 top-0 z-10 h-16" : "sticky top-0 z-10 h-14 border-b border-[#e8e6e0] bg-white"}`}
    >
      <Link
        to="/"
        className={`text-[11px] font-normal tracking-[0.25em] ${landing ? "text-primary" : "text-[#1a1a1a]"}`}
      >
        BIZAGENT
      </Link>
      {landing ? (
        <Link to="/settings/bot" className="button-primary">
          Request Access
        </Link>
      ) : (
        <div className="flex items-center gap-8">
          <span className="text-xs text-[#9a9a8a]">
            Macaney Sustainable Solutions
          </span>
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`text-[10px] uppercase tracking-[0.18em] ${pathname === link.to ? "text-[#1a1a1a]" : "text-[#9a9a8a] hover:text-[#1a1a1a]"}`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}
