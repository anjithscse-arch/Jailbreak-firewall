import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  MessageSquare,
  LayoutDashboard,
  Terminal,
  FileText,
  Sliders,
  BarChart3,
  Settings,
  LogOut,
  UserCheck,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('firewall_auth_token');
  const user = localStorage.getItem('firewall_user') || 'Admin';

  const handleLogout = () => {
    localStorage.removeItem('firewall_auth_token');
    localStorage.removeItem('firewall_user');
    navigate('/login');
  };

  const navItems = [
    { to: '/chat', label: 'AI Chatbot', icon: MessageSquare },
    { to: '/dashboard', label: 'Overview Dashboard', icon: LayoutDashboard },
    { to: '/analyze', label: 'Analyze Sandbox', icon: Terminal },
    { to: '/logs', label: 'Security Audit Logs', icon: FileText },
    { to: '/rules', label: 'Rule Management', icon: Sliders },
    { to: '/evaluation', label: 'Model Evaluation', icon: BarChart3 },
    { to: '/settings', label: 'Gateway Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0f172a] border-r border-slate-800 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand header */}
        <div className="h-16 flex items-center px-6 gap-3 border-b border-slate-800/80">
          <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-slate-100 font-mono">
              AI FIREWALL
            </h1>
            <span className="text-[10px] text-slate-400 font-mono block">
              v1.0.0 Hybrid Guard
            </span>
          </div>
        </div>

        {/* Navigation list */}
        <nav className="p-4 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              <UserCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="truncate">
              <span className="text-xs font-medium text-slate-200 block truncate">
                {user}
              </span>
              <span className="text-[10px] font-mono text-emerald-400 block">
                Authenticated
              </span>
            </div>
          </div>
          {token && (
            <button
              onClick={handleLogout}
              title="Logout"
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
};
