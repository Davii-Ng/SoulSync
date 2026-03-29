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
  { to: "/", icon: "history", label: "History" },
  { to: "/resources", icon: "health_and_safety", label: "Resources" },
  { to: "/settings", icon: "settings", label: "Settings" },
];

export function Layout({ isConnected }: Props) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen font-body text-on-surface bg-transparent">
      {/* ── Header ── */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 py-4 header-bar">
        <div className="flex items-center gap-3">
          {/* Sidebar toggle (desktop only) */}
          <button
            type="button"
            onClick={() => setSidebarOpen((o) => !o)}
            className="hidden md:flex w-9 h-9 items-center justify-center rounded-lg hover:bg-soul-accent-pale transition-colors"
            aria-label="Toggle sidebar"
          >
            <span className="material-symbols-outlined text-xl text-soul-text-secondary">
              {sidebarOpen ? "menu_open" : "menu"}
            </span>
          </button>
          <NavLink
            to="/"
            className="text-2xl font-bold tracking-tight text-soul-text flex items-center gap-2"
          >
            <span className="tech-font text-soul-accent">&lt;</span>
            SoulSync
            <span className="tech-font text-soul-accent">/&gt;</span>
          </NavLink>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`w-2.5 h-2.5 rounded-full ${isConnected ? "bg-green-400" : "bg-red-400"}`}
            title={isConnected ? "Connected" : "Disconnected"}
          />
          <button
            type="button"
            className="w-9 h-9 rounded-full flex items-center justify-center header-avatar text-soul-text"
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
      <div className="mt-[80px] block">
        {/* Sidebar (desktop, retractable) — only History & Resources */}
        <aside
          className={`hidden md:flex flex-col fixed top-[80px] bottom-[88px] left-0 z-40 sidebar-panel sidebar-transition ${
            sidebarOpen ? "w-56" : "w-0 overflow-hidden border-r-0"
          }`}
        >
          <nav className="flex-1 flex flex-col gap-1 px-3 py-4 min-w-[14rem]">
            <p className="sidebar-insights-heading px-3 mb-2 uppercase">
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

        {/* Main content workspace */}
        <div style={{ marginLeft: sidebarOpen ? '14rem' : '0' }} className="hidden md:block bg-transparent min-h-[calc(100vh-160px)]">
          <main className="flex-1 flex flex-col items-center justify-start pt-8 pb-56 px-5 md:px-8 w-full">
            <div className="w-full max-w-3xl">
              <Outlet />
            </div>
          </main>
        </div>
        <div className="md:hidden block bg-transparent min-h-[calc(100vh-160px)]">
          <main className="flex-1 flex flex-col items-center justify-start pt-8 pb-56 px-5 w-full">
            <div className="w-full max-w-3xl">
              <Outlet />
            </div>
          </main>
        </div>
      </div>

      {/* ── Bottom Nav (always visible) ── */}
      <nav style={{ left: sidebarOpen ? '14rem' : '0' }} className="hidden md:flex fixed bottom-0 z-50 bottom-nav-bar transition-all duration-300 right-0 justify-center">
        <div className="flex justify-center items-center gap-8 px-4 pb-6 pt-3 w-full">
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
              <span className="text-xs font-medium tracking-wide uppercase mt-0.5">
                {item.label}
              </span>
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Mobile nav */}
      <nav className="flex md:hidden fixed bottom-0 z-50 bottom-nav-bar left-0 right-0 justify-center">
        <div className="flex justify-center items-center gap-4 px-4 pb-6 pt-3 w-full">
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
              <span className="text-xs font-medium tracking-wide uppercase mt-0.5">
                {item.label}
              </span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
