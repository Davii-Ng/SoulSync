import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import logo from "@assets/logo_1.png";

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
  { to: "/home", icon: "home", label: "Home" },
  { to: "/resources", icon: "health_and_safety", label: "Resources" },
  { to: "/settings", icon: "settings", label: "Settings" },
];

export function Layout({ isConnected }: Props) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen font-body text-on-surface bg-transparent">
      {/* ── Header ── */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-5 py-2 header-bar">
        <div className="flex items-center gap-2">
          {/* Sidebar toggle (desktop only) */}
          <button
            type="button"
            onClick={() => setSidebarOpen((o) => !o)}
            className="hidden md:flex w-8 h-8 items-center justify-center rounded-lg hover:bg-soul-accent-pale transition-colors"
            aria-label="Toggle sidebar"
          >
            <span className="material-symbols-outlined text-xl text-soul-text-secondary">
              {sidebarOpen ? "menu_open" : "menu"}
            </span>
          </button>
          <NavLink
            to="/"
            className="text-xl font-bold tracking-tight text-soul-text flex items-center gap-2"
          >
            <img src={logo} alt="SoulSync" className="w-7 h-7 rounded-md" />
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
      <div className="mt-[52px] block">
        {/* Sidebar (desktop, retractable) */}
        <aside
          className={`hidden md:flex flex-col fixed top-[52px] bottom-[60px] left-0 z-40 sidebar-panel sidebar-transition ${
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

        {/* Main content workspace — stays put when sidebar opens */}
        <main className="flex-1 flex flex-col items-center justify-start pt-6 pb-24 px-5 md:px-8 w-full bg-transparent min-h-[calc(100vh-112px)]">
          <div className="w-full max-w-3xl">
            <Outlet />
          </div>
        </main>
      </div>

      {/* ── Bottom Nav — centered pill ── */}
      <div className="fixed bottom-4 left-0 right-0 z-50 flex justify-center pointer-events-none">
        <nav className="bottom-nav-bar pointer-events-auto inline-flex items-center gap-6 px-6 pb-2 pt-1.5 rounded-full">
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
        </nav>
      </div>
    </div>
  );
}
