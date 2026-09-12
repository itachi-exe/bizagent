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
      className={`flex h-16 items-center justify-between px-10 ${landing ? "absolute inset-x-0 top-0 z-10" : "border-b border-[rgba(255,255,255,0.06)]"}`}
    >
      <Link
        to="/"
        className="text-[11px] font-normal tracking-[0.3em] text-primary"
      >
        BIZAGENT
      </Link>
      {landing ? (
        <Link to="/settings/bot" className="button-primary">
          Request Access
        </Link>
      ) : (
        <div className="flex items-center gap-7">
          <span className="mr-3 text-xs text-[rgba(255,255,255,0.3)]">
            Macaney Sustainable Solutions
          </span>
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`text-[10px] uppercase tracking-[0.2em] ${pathname === link.to ? "text-green" : "text-[rgba(255,255,255,0.4)] hover:text-primary"}`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}
