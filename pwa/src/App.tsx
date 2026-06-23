import { Routes, Route, useLocation } from "react-router-dom";

function App() {
  const location = useLocation();
  const hideTabBar = location.pathname === "/command";

  return (
    <div style={{ minHeight: "100vh", background: "#f5f5f5", maxWidth: 480, margin: "0 auto" }}>
      <Routes>
        <Route path="/" element={<NotificationCenter />} />
        <Route path="/shops" element={<ShopOverview />} />
        <Route path="/logs" element={<OperationLogs />} />
        <Route path="/command" element={<CommandInput />} />
      </Routes>

      {!hideTabBar && (
        <div className="tab-bar">
          <TabItem path="/" icon="🔔" label="通知" />
          <TabItem path="/shops" icon="🏪" label="店铺" />
          <TabItem path="/logs" icon="📋" label="日志" />
          <TabItem path="/command" icon="💬" label="指令" />
        </div>
      )}
    </div>
  );
}

function TabItem({ path, icon, label }: { path: string; icon: string; label: string }) {
  const location = useLocation();
  const isActive = location.pathname === path;
  return (
    <a href={path} className={`tab-item ${isActive ? "active" : ""}`}>
      <span className="tab-icon">{icon}</span>
      {label}
    </a>
  );
}

function NotificationCenter() {
  return (
    <>
      <div className="nav-header">🔔 通知中心</div>
      <div className="content">
        <div className="card">
          <div className="card-title">🏷️ 定价决策审批</div>
          <div className="card-body">
            <p>拼多多5店 · 连衣裙爆款款</p>
            <p>竞品：¥39.9 → ¥31.9 (-20%)</p>
            <p>建议：¥42.0 → ¥33.9 (-19%)</p>
            <p style={{ color: "#666", fontSize: 12, marginTop: 4 }}>预估影响：+15%点击，+8%转化</p>
          </div>
          <div className="btn-group">
            <button className="btn btn-primary">✅ 同意</button>
            <button className="btn btn-outline">✏️ 修改</button>
            <button className="btn btn-danger">❌ 拒绝</button>
          </div>
        </div>
        <div className="card" style={{ borderLeft: "3px solid #dc3545" }}>
          <div className="card-title">⚠️ 异常告警</div>
          <div className="card-body">
            <p>淘宝2店 · 需要人工处理验证码</p>
            <p style={{ color: "#666", fontSize: 12 }}>10分钟前</p>
          </div>
        </div>
        <div className="card" style={{ borderLeft: "3px solid #ffc107" }}>
          <div className="card-title">🔑 Cookie即将过期</div>
          <div className="card-body">
            <p>拼多多3店 · 预计2小时后过期</p>
            <p style={{ color: "#666", fontSize: 12 }}>30分钟前</p>
          </div>
        </div>
      </div>
    </>
  );
}

function ShopOverview() {
  return (
    <>
      <div className="nav-header">🏪 店铺概览</div>
      <div className="content">
        <div className="stat-grid">
          <div className="stat-item">
            <div className="stat-value">¥12,580</div>
            <div className="stat-label">今日销售</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">156</div>
            <div className="stat-label">今日订单</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">¥2,340</div>
            <div className="stat-label">广告花费</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">23</div>
            <div className="stat-label">在线商品</div>
          </div>
        </div>
        <div className="card" style={{ marginTop: 16 }}>
          <div className="card-title">店铺状态</div>
          {[
            { name: "拼多多1店", status: "online" },
            { name: "拼多多2店", status: "online" },
            { name: "淘宝1店", status: "online" },
            { name: "淘宝2店", status: "warning" },
            { name: "抖音1店", status: "online" },
          ].map((shop) => (
            <div key={shop.name} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #eee" }}>
              <span>{shop.name}</span>
              <span style={{ color: shop.status === "online" ? "#28a745" : "#ffc107", fontSize: 12 }}>
                ● {shop.status === "online" ? "正常" : "异常"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function OperationLogs() {
  return (
    <>
      <div className="nav-header">📋 操作日志</div>
      <div className="content">
        <div className="card">
          <div className="card-title">🤖 Agent运行日志</div>
          <div className="card-body" style={{ fontFamily: "monospace", fontSize: 12, background: "#1a1a1a", color: "#00ff00", padding: 12, borderRadius: 8, marginTop: 8 }}>
            <p>[14:32:01] [INFO] PricingAgent - 检测到竞品降价</p>
            <p>[14:32:02] [INFO] PricingAgent - 生成改价建议: ¥42.0 → ¥33.9</p>
            <p>[14:32:03] [WARN] PricingAgent - 价格变动19% &gt; 15%, 推送审批</p>
            <p>[14:32:05] [INFO] WebSocket - 审批通知已推送</p>
            <p>[14:30:00] [INFO] SelectionAgent - 开始每日选品巡检</p>
            <p>[14:30:15] [INFO] SelectionAgent - 发现3个潜在爆款</p>
          </div>
        </div>
      </div>
    </>
  );
}

function CommandInput() {
  return (
    <>
      <div className="nav-header">💬 自然语言指令</div>
      <div className="content">
        <div className="card">
          <div className="card-title">输入指令</div>
          <textarea
            placeholder='例如："把所有拼多多店的连衣裙降价5%"'
            style={{ width: "100%", minHeight: 100, padding: 12, borderRadius: 8, border: "1px solid #ddd", fontSize: 14, resize: "vertical", fontFamily: "inherit" }}
          />
          <button className="btn btn-primary" style={{ marginTop: 12, width: "100%" }}>发送指令</button>
        </div>
        <div className="card">
          <div className="card-title">快捷指令</div>
          {["帮我检查所有店铺库存", "分析今天各平台销售数据", "生成本周选品报告", "检查广告ROI异常情况"].map((cmd) => (
            <div key={cmd} style={{ padding: "8px 0", borderBottom: "1px solid #eee", fontSize: 13, color: "#1a73e8", cursor: "pointer" }}>
              {cmd}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default App;
