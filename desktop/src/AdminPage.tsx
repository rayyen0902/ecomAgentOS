import { useState } from "react";

/**
 * 管理后台页面 - 租户管理 + 运营数据 + 系统监控
 * 仅供管理员使用，普通用户不可见
 */
export function AdminPage() {
  const [activeTab, setActiveTab] = useState<"tenants" | "dashboard" | "monitor">("dashboard");

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ marginBottom: 24 }}>🛡️ 管理后台</h1>

      {/* 标签切换 */}
      <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        {([
          { key: "dashboard", label: "📊 运营数据" },
          { key: "tenants", label: "👥 租户管理" },
          { key: "monitor", label: "🔧 系统监控" },
        ] as const).map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: "8px 20px",
              borderRadius: 8,
              border: "none",
              background: activeTab === tab.key ? "#1a73e8" : "#fff",
              color: activeTab === tab.key ? "#fff" : "#333",
              cursor: "pointer",
              fontSize: 14,
              fontWeight: activeTab === tab.key ? "bold" : "normal",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "dashboard" && <DashboardTab />}
      {activeTab === "tenants" && <TenantsTab />}
      {activeTab === "monitor" && <MonitorTab />}
    </div>
  );
}

// ========== 运营数据标签 ==========
function DashboardTab() {
  const stats = [
    { label: "总租户数", value: "156", trend: "+12%", color: "#1a73e8" },
    { label: "活跃租户", value: "142", trend: "91%", color: "#28a745" },
    { label: "月收入", value: "¥89,500", trend: "+18%", color: "#9c27b0" },
    { label: "总店铺数", value: "1,234", trend: "+56", color: "#ff9800" },
    { label: "运行中Agent", value: "89", trend: "", color: "#00bcd4" },
    { label: "RPA成功率", value: "97.2%", trend: "+0.5%", color: "#4caf50" },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 16 }}>运营数据总览</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
        {stats.map((stat) => (
          <div
            key={stat.label}
            style={{
              background: "#fff",
              borderRadius: 12,
              padding: 20,
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              borderLeft: `4px solid ${stat.color}`,
            }}
          >
            <div style={{ fontSize: 14, color: "#666" }}>{stat.label}</div>
            <div style={{ fontSize: 28, fontWeight: "bold", marginTop: 4 }}>{stat.value}</div>
            {stat.trend && (
              <div style={{ fontSize: 13, color: stat.trend.startsWith("+") ? "#28a745" : "#666", marginTop: 4 }}>
                {stat.trend}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 套餐分布 */}
      <div style={{ background: "#fff", borderRadius: 12, padding: 20, marginTop: 20, boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <h3 style={{ marginBottom: 16 }}>套餐分布</h3>
        {[
          { plan: "Starter", count: 68, pct: 44 },
          { plan: "Basic", count: 42, pct: 27 },
          { plan: "Growth", count: 25, pct: 16 },
          { plan: "Pro", count: 15, pct: 10 },
          { plan: "Enterprise", count: 6, pct: 4 },
        ].map((item) => (
          <div key={item.plan} style={{ display: "flex", alignItems: "center", marginBottom: 12 }}>
            <span style={{ width: 80, fontSize: 14 }}>{item.plan}</span>
            <div style={{ flex: 1, background: "#eee", borderRadius: 4, height: 20, overflow: "hidden" }}>
              <div
                style={{
                  width: `${item.pct}%`,
                  height: "100%",
                  background: "#1a73e8",
                  borderRadius: 4,
                  transition: "width 0.3s",
                }}
              />
            </div>
            <span style={{ marginLeft: 12, fontSize: 14, minWidth: 60, textAlign: "right" }}>
              {item.count} ({item.pct}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ========== 租户管理标签 ==========
function TenantsTab() {
  const tenants = [
    { id: "t_001", name: "张三电商", email: "zhang@example.com", plan: "growth", status: "active", shops: 8, joined: "2025-01-15" },
    { id: "t_002", name: "李四百货", email: "li@example.com", plan: "pro", status: "active", shops: 15, joined: "2025-02-03" },
    { id: "t_003", name: "王五美妆", email: "wang@example.com", plan: "basic", status: "active", shops: 5, joined: "2025-03-10" },
    { id: "t_004", name: "赵六日用", email: "zhao@example.com", plan: "starter", status: "suspended", shops: 3, joined: "2025-01-20" },
    { id: "t_005", name: "孙七跨境", email: "sun@example.com", plan: "enterprise", status: "active", shops: 25, joined: "2025-04-01" },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 16 }}>租户列表</h2>
      <div style={{ background: "#fff", borderRadius: 12, overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#f5f5f5" }}>
              <th style={{ textAlign: "left", padding: "12px 16px", fontSize: 13, color: "#666" }}>租户</th>
              <th style={{ textAlign: "left", padding: "12px 16px", fontSize: 13, color: "#666" }}>邮箱</th>
              <th style={{ textAlign: "left", padding: "12px 16px", fontSize: 13, color: "#666" }}>套餐</th>
              <th style={{ textAlign: "left", padding: "12px 16px", fontSize: 13, color: "#666" }}>店铺数</th>
              <th style={{ textAlign: "left", padding: "12px 16px", fontSize: 13, color: "#666" }}>状态</th>
              <th style={{ textAlign: "left", padding: "12px 16px", fontSize: 13, color: "#666" }}>注册时间</th>
            </tr>
          </thead>
          <tbody>
            {tenants.map((t) => (
              <tr key={t.id} style={{ borderBottom: "1px solid #f0f0f0" }}>
                <td style={{ padding: "12px 16px", fontWeight: 600 }}>{t.name}</td>
                <td style={{ padding: "12px 16px", fontSize: 13, color: "#666" }}>{t.email}</td>
                <td style={{ padding: "12px 16px" }}>
                  <span style={{ display: "inline-block", padding: "2px 8px", borderRadius: 4, fontSize: 12, background: "#e3f2fd", color: "#1565c0" }}>
                    {t.plan}
                  </span>
                </td>
                <td style={{ padding: "12px 16px", fontSize: 13 }}>{t.shops}</td>
                <td style={{ padding: "12px 16px" }}>
                  <span style={{ color: t.status === "active" ? "#28a745" : "#dc3545", fontSize: 13 }}>
                    {t.status === "active" ? "● 正常" : "● 暂停"}
                  </span>
                </td>
                <td style={{ padding: "12px 16px", fontSize: 13, color: "#666" }}>{t.joined}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ========== 系统监控标签 ==========
function MonitorTab() {
  const services = [
    { name: "FastAPI", status: "healthy", uptime: "99.9%", cpu: "12%", memory: "256MB" },
    { name: "PostgreSQL", status: "healthy", uptime: "99.99%", cpu: "8%", memory: "512MB" },
    { name: "Redis", status: "healthy", uptime: "99.95%", cpu: "2%", memory: "128MB" },
    { name: "Celery Workers", status: "healthy", uptime: "99.8%", cpu: "45%", memory: "1GB" },
    { name: "ComfyUI", status: "healthy", uptime: "98.5%", cpu: "78%", memory: "4GB" },
    { name: "Playwright", status: "warning", uptime: "97.2%", cpu: "65%", memory: "2GB" },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 16 }}>系统监控</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
        {services.map((svc) => (
          <div
            key={svc.name}
            style={{
              background: "#fff",
              borderRadius: 12,
              padding: 16,
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              borderLeft: `3px solid ${svc.status === "healthy" ? "#28a745" : "#ffc107"}`,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span style={{ fontWeight: 600 }}>{svc.name}</span>
              <span style={{ color: svc.status === "healthy" ? "#28a745" : "#ffc107", fontSize: 13 }}>
                ● {svc.status === "healthy" ? "正常" : "告警"}
              </span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, fontSize: 12, color: "#666" }}>
              <div>运行时长: {svc.uptime}</div>
              <div>CPU: {svc.cpu}</div>
              <div>内存: {svc.memory}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
