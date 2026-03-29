import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

interface Props {
  isConnected: boolean;
}

// Primary nav lives in the bottom bar (always visible)
const bottomItems = [
  { to: "/", icon: "mic", label: "Speak" },
  { to: "/journal", icon: "auto_stories", label: "Journal" },
  { to: "/calendar", icon: "calendar_month", label: "Calendar" },
];

// Secondary nav lives in the collapsible sidebar
const sideItems = [
  { to: "/history", icon: "history", label: "History" },
  { to: "/resources", icon: "health_and_safety", label: "Resources" },
  { to: "/settings", icon: "settings", label: "Settings" },
];

export function Layout({ isConnected }: Props) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div
      className="min-h-screen flex flex-col font-body text-on-surface"
      style={{ background: "var(--soul-bg)" }}
    >
      {/* ── Header ── */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 py-4 header-bar">
        <div className="flex items-center gap-3">
          {/* Sidebar toggle (desktop only) */}
          <button
            type="button"
            onClick={() => setSidebarOpen((o) => !o)}
            className="hidden md:flex w-9 h-9 items-center justify-center rounded-lg hover:bg-[var(--soul-accent-pale)] transition-colors"
            aria-label="Toggle sidebar"
          >
            <span
              className="material-symbols-outlined text-xl"
              style={{ color: "var(--soul-text-secondary)" }}
            >
              {sidebarOpen ? "menu_open" : "menu"}
            </span>
          </button>
          <NavLink
            to="/"
            className="header-title text-3xl font-extrabold tracking-tighter"
            style={{ color: "var(--soul-text)" }}
          >
            SoulSync
          </NavLink>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`w-2.5 h-2.5 rounded-full ${isConnected ? "bg-green-400" : "bg-red-400"}`}
            title={isConnected ? "Connected" : "Disconnected"}
          />
          <button
            type="button"
            className="w-9 h-9 rounded-full flex items-center justify-center header-avatar"
            aria-label="User profile"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            >
              <circle cx="12" cy="8" r="4" />
              <path d="M20 21a8 8 0 0 0-16 0" />
            </svg>
          </button>
        </div>
      </header>

      {/* ── Body: sidebar + main ── */}
      <div className="flex flex-1 mt-[72px] mb-[88px]">
        {/* Sidebar (desktop, retractable) — only History & Resources */}
        <aside
          className={`hidden md:flex flex-col fixed top-[72px] bottom-[88px] left-0 z-40 sidebar-panel sidebar-transition ${
            sidebarOpen ? "w-56" : "w-0 overflow-hidden border-r-0"
          }`}
        >
          <nav className="flex-1 flex flex-col gap-1 px-3 py-4 min-w-[14rem]">
            <p
              className="sidebar-insights-heading px-3 mb-2 uppercase"
              style={{ color: "var(--soul-text-muted)" }}
            >
              Insights
            </p>
            {sideItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? "sidebar-link-active" : ""}`
                }
              >
                <span className="material-symbols-outlined text-xl">
                  {item.icon}
                </span>
                <span className="text-sm font-medium">{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        {/* Main content — centered with top padding */}
        <main
          className={`flex-1 flex justify-center px-4 pt-12 pb-5 md:px-8 md:pt-14 md:pb-6 overflow-y-auto transition-[margin] duration-300 ease-in-out ${
            sidebarOpen ? "md:ml-56" : "md:ml-0"
          }`}
        >
          <div className="w-full max-w-5xl">
            <Outlet />
          </div>
        </main>
      </div>

      {/* ── Bottom Nav (always visible) — Speak, Journal, Calendar + mobile: History, Resources ── */}
      <nav className="fixed bottom-0 left-0 w-full z-50 bottom-nav-bar">
        <div className="flex justify-center items-center gap-1 md:gap-2 px-2 pb-5 pt-2 max-w-3xl mx-auto">
          {/* On mobile show all tabs; on desktop only primary tabs */}
          {bottomItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `bottom-nav-item ${isActive ? "bottom-nav-item-active" : ""}`
              }
            >
              <span className="material-symbols-outlined text-xl">
                {item.icon}
              </span>
              <span className="text-[11px] font-medium tracking-wide uppercase mt-0.5">
                {item.label}
              </span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
