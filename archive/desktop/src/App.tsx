import { BrowserRouter, Routes, Route, useLocation, NavLink } from "react-router-dom";

function App() {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* 侧边栏导航 */}
      <Sidebar />

      {/* 主内容区 */}
      <div style={{ flex: 1, marginLeft: 220 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/shops" element={<ShopsPage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </div>
    </div>
  );
}

function Sidebar() {
  const navItems = [
    { path: "/", icon: "📊", label: "总览" },
    { path: "/shops", icon: "🏪", label: "店铺" },
    { path: "/products", icon: "📦", label: "商品" },
    { path: "/orders", icon: "📋", label: "订单" },
    { path: "/agents", icon: "🤖", label: "Agent" },
    { path: "/settings", icon: "⚙️", label: "设置" },
  ];

  return (
    <div
      style={{
        width: 220,
        background: "#1a1a2e",
        color: "#fff",
        padding: "16px 0",
        position: "fixed",
        height: "100vh",
        overflowY: "auto",
      }}
    >
      <div style={{ padding: "0 16px 16px", fontSize: 16, fontWeight: "bold", borderBottom: "1px solid #333", marginBottom: 8 }}>
        🏪 电商运营中心
      </div>
      {navItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          style={({ isActive }) => ({
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "10px 16px",
            color: isActive ? "#4fc3f7" : "#aaa",
            background: isActive ? "rgba(79,195,247,0.1)" : "transparent",
            textDecoration: "none",
            fontSize: 14,
            cursor: "pointer",
          })}
        >
          <span>{item.icon}</span>
          <span>{item.label}</span>
        </NavLink>
      ))}
    </div>
  );
}

function Dashboard() {
  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ marginBottom: 24 }}>📊 运营总览</h1>

      {/* 汇总统计 */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
        <StatCard title="今日销售" value="¥12,580" trend="+8.5%" />
        <StatCard title="今日订单" value="156" trend="+12.3%" />
        <StatCard title="广告花费" value="¥2,340" trend="-3.2%" />
        <StatCard title="待处理" value="7" trend="" />
      </div>

      {/* 店铺状态矩阵 */}
      <div style={{ background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <h2 style={{ marginBottom: 16 }}>店铺状态矩阵</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
          {[
            { name: "拼多多1店", platform: "pdd", status: "online" },
            { name: "拼多多2店", platform: "pdd", status: "online" },
            { name: "淘宝1店", platform: "taobao", status: "online" },
            { name: "淘宝2店", platform: "taobao", status: "warning" },
            { name: "抖音1店", platform: "douyin", status: "online" },
            { name: "抖音2店", platform: "douyin", status: "online" },
          ].map((shop) => (
            <ShopStatusCard key={shop.name} {...shop} />
          ))}
        </div>
      </div>

      {/* 待处理事项 */}
      <div style={{ background: "#fff", borderRadius: 12, padding: 20, marginTop: 20, boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <h2 style={{ marginBottom: 16 }}>⚡ 待处理事项</h2>
        {[
          { type: "审批", title: "拼多多5店连衣裙改价", desc: "建议降价19%", time: "5分钟前" },
          { type: "告警", title: "淘宝2店验证码", desc: "需要人工处理", time: "10分钟前" },
          { type: "选品", title: "发现3个潜在爆款", desc: "建议上架", time: "30分钟前" },
        ].map((item, i) => (
          <div key={i} style={{ padding: "12px 0", borderBottom: "1px solid #eee" }}>
            <span style={{ display: "inline-block", padding: "2px 8px", borderRadius: 4, fontSize: 12, marginRight: 8, background: item.type === "审批" ? "#e3f2fd" : item.type === "告警" ? "#ffebee" : "#e8f5e9", color: item.type === "审批" ? "#1565c0" : item.type === "告警" ? "#c62828" : "#2e7d32" }}>
              {item.type}
            </span>
            <strong>{item.title}</strong>
            <p style={{ color: "#666", fontSize: 13, margin: "4px 0" }}>{item.desc}</p>
            <span style={{ color: "#999", fontSize: 12 }}>{item.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatCard({ title, value, trend }: { title: string; value: string; trend: string }) {
  return (
    <div style={{ background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
      <div style={{ fontSize: 14, color: "#666" }}>{title}</div>
      <div style={{ fontSize: 28, fontWeight: "bold", marginTop: 4 }}>{value}</div>
      {trend && (
        <div style={{ fontSize: 13, color: trend.startsWith("+") ? "#28a745" : trend.startsWith("-") ? "#dc3545" : "#666", marginTop: 4 }}>
          {trend}
        </div>
      )}
    </div>
  );
}

function ShopStatusCard({ name, platform, status }: { name: string; platform: string; status: string }) {
  const color = status === "online" ? "#28a745" : status === "warning" ? "#ffc107" : "#dc3545";
  const label = status === "online" ? "正常" : status === "warning" ? "异常" : "离线";
  return (
    <div style={{ background: "#fff", borderRadius: 8, padding: 12, borderLeft: `3px solid ${color}`, boxShadow: "0 1px 2px rgba(0,0,0,0.05)" }}>
      <div style={{ fontSize: 13, fontWeight: 600 }}>{name}</div>
      <div style={{ fontSize: 12, color: "#666", marginTop: 4 }}>
        <span style={{ color, fontWeight: "bold" }}>● {label}</span>
      </div>
    </div>
  );
}

function ShopsPage() {
  return (
    <div style={{ padding: 24 }}>
      <h1>🏪 店铺管理</h1>
      <p style={{ color: "#666", marginTop: 8 }}>管理所有电商平台店铺</p>
      <div style={{ background: "#fff", borderRadius: 12, padding: 20, marginTop: 20, boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <p>店铺列表加载中...</p>
      </div>
    </div>
  );
}

function ProductsPage() {
  return (
    <div style={{ padding: 24 }}>
      <h1>📦 商品管理</h1>
      <p style={{ color: "#666", marginTop: 8 }}>管理所有店铺的商品</p>
    </div>
  );
}

function OrdersPage() {
  return (
    <div style={{ padding: 24 }}>
      <h1>📋 订单管理</h1>
      <p style={{ color: "#666", marginTop: 8 }}>查看和处理订单</p>
    </div>
  );
}

function AgentsPage() {
  return (
    <div style={{ padding: 24 }}>
      <h1>🤖 Agent运行日志</h1>
      <div style={{ background: "#1a1a1a", color: "#00ff00", padding: 16, borderRadius: 8, fontFamily: "monospace", marginTop: 20, fontSize: 13, maxHeight: 400, overflow: "auto" }}>
        <p>[14:32:01] [INFO] PricingAgent - 检测到竞品降价</p>
        <p>[14:32:02] [INFO] PricingAgent - 生成改价建议: ¥42.0 → ¥33.9</p>
        <p>[14:32:03] [WARN] PricingAgent - 价格变动19% &gt; 15%, 推送审批</p>
        <p>[14:32:05] [INFO] WebSocket - 审批通知已推送</p>
        <p>[14:30:00] [INFO] SelectionAgent - 开始每日选品巡检</p>
        <p>[14:30:15] [INFO] SelectionAgent - 发现3个潜在爆款</p>
        <p>[14:28:00] [INFO] CustomerServiceAgent - 自动回复12条买家消息</p>
        <p>[14:25:00] [INFO] PricingAgent - 每15分钟价格巡检完成</p>
      </div>
    </div>
  );
}

function SettingsPage() {
  return (
    <div style={{ padding: 24 }}>
      <h1>⚙️ 系统设置</h1>
      <p style={{ color: "#666", marginTop: 8 }}>配置系统参数</p>
    </div>
  );
}

export default App;
