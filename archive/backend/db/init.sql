-- =============================================================================
-- E-commerce AgentOS Database Initialization Script
-- PostgreSQL 14+
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. shops — 店铺表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    name VARCHAR(100) NOT NULL,
    platform VARCHAR(20) NOT NULL,
    platform_shop_id VARCHAR(100),
    cookies JSONB,
    cookie_expires_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON COLUMN shops.platform IS 'douyin/taobao/pdd/xiaohongshu';
COMMENT ON COLUMN shops.status IS 'active/paused/error';

ALTER TABLE shops ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 2. platform_adapters — 平台适配器版本表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS platform_adapters (
    platform VARCHAR(20) PRIMARY KEY,
    version VARCHAR(20),
    selectors JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON COLUMN platform_adapters.platform IS 'douyin/taobao/pdd/xiaohongshu';

-- ---------------------------------------------------------------------------
-- 3. products — 商品表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    shop_id UUID REFERENCES shops(id),
    platform_product_id VARCHAR(100),
    title VARCHAR(500),
    category VARCHAR(100),
    cost DECIMAL(10,2),
    current_price DECIMAL(10,2),
    stock_quantity INTEGER,
    status VARCHAR(20) DEFAULT 'draft',
    platform_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON COLUMN products.status IS 'on_sale/off_shelf/draft';

-- ---------------------------------------------------------------------------
-- 4. agent_tasks — 任务记录表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    shop_id UUID REFERENCES shops(id),
    agent_type VARCHAR(50) NOT NULL,
    task_type VARCHAR(100),
    input_data JSONB,
    decision JSONB,
    actions JSONB,
    status VARCHAR(20) DEFAULT 'pending_approval',
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    result JSONB,
    screenshot_urls JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

COMMENT ON COLUMN agent_tasks.agent_type IS 'selection/pricing/ads/cs/content/image/video';
COMMENT ON COLUMN agent_tasks.status IS 'pending_approval/approved/executing/done/failed';

-- ---------------------------------------------------------------------------
-- 5. orders — 订单表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    shop_id UUID REFERENCES shops(id),
    platform_order_id VARCHAR(100) UNIQUE,
    product_id UUID REFERENCES products(id),
    quantity INTEGER,
    sale_price DECIMAL(10,2),
    buyer_info JSONB,
    logistics_no VARCHAR(100),
    fulfillment_type VARCHAR(20) DEFAULT '1688_dropship',
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    shipped_at TIMESTAMP
);

COMMENT ON COLUMN orders.fulfillment_type IS '1688_dropship/self_warehouse/supplier';

-- ---------------------------------------------------------------------------
-- 6. competitor_prices — 竞品价格历史表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS competitor_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    platform VARCHAR(20),
    competitor_shop VARCHAR(100),
    price DECIMAL(10,2),
    recorded_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON COLUMN competitor_prices.platform IS 'douyin/taobao/pdd/xiaohongshu';

-- ---------------------------------------------------------------------------
-- 7. approval_tasks — 审批队列表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS approval_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_task_id UUID REFERENCES agent_tasks(id),
    shop_id UUID REFERENCES shops(id),
    priority INTEGER DEFAULT 5,
    title VARCHAR(200),
    description TEXT,
    options JSONB,
    expires_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON COLUMN approval_tasks.priority IS '1最高优先级';
COMMENT ON COLUMN approval_tasks.status IS 'pending/expired/approved/rejected';

-- ---------------------------------------------------------------------------
-- 8. tenants — 租户表（Phase 5预留）
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    phone VARCHAR(20),
    plan VARCHAR(20) NOT NULL DEFAULT 'starter',
    status VARCHAR(20) DEFAULT 'active',
    trial_ends_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON COLUMN tenants.plan IS 'starter/basic/growth/pro/enterprise';
COMMENT ON COLUMN tenants.status IS 'active/trial/suspended/canceled';

-- ---------------------------------------------------------------------------
-- 9. tenant_configs — 租户配置表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tenant_configs (
    tenant_id UUID PRIMARY KEY REFERENCES tenants(id),
    max_shops INTEGER NOT NULL,
    max_monthly_images INTEGER,
    max_monthly_videos INTEGER,
    features_enabled JSONB DEFAULT '{}'::jsonb,
    celery_queue VARCHAR(50),
    api_rate_limit INTEGER DEFAULT 100,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 10. subscriptions — 订阅记录表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    plan VARCHAR(20) NOT NULL,
    price_monthly DECIMAL(10,2),
    price_paid DECIMAL(10,2),
    billing_cycle VARCHAR(10),
    starts_at TIMESTAMP NOT NULL,
    ends_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    payment_method VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON COLUMN subscriptions.status IS 'active/cancelled/expired/trial';

-- ---------------------------------------------------------------------------
-- 11. usage_records — 用量记录表
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    resource_type VARCHAR(50) NOT NULL,
    quantity INTEGER DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON COLUMN usage_records.resource_type IS 'images/videos/api_calls/rpa_operations';


-- ============================================================================
-- INDEXES
-- ============================================================================

-- shops indexes
CREATE INDEX IF NOT EXISTS idx_shops_tenant_id ON shops(tenant_id);
CREATE INDEX IF NOT EXISTS idx_shops_platform ON shops(platform);
CREATE INDEX IF NOT EXISTS idx_shops_status ON shops(status);
CREATE INDEX IF NOT EXISTS idx_shops_name ON shops(name);

-- products indexes
CREATE INDEX IF NOT EXISTS idx_products_tenant_id ON products(tenant_id);
CREATE INDEX IF NOT EXISTS idx_products_shop_id ON products(shop_id);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- agent_tasks indexes
CREATE INDEX IF NOT EXISTS idx_agent_tasks_tenant_id ON agent_tasks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_shop_id ON agent_tasks(shop_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent_type ON agent_tasks(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_created_at ON agent_tasks(created_at);

-- orders indexes
CREATE INDEX IF NOT EXISTS idx_orders_tenant_id ON orders(tenant_id);
CREATE INDEX IF NOT EXISTS idx_orders_shop_id ON orders(shop_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_product_id ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);

-- competitor_prices indexes
CREATE INDEX IF NOT EXISTS idx_competitor_prices_product_id ON competitor_prices(product_id);
CREATE INDEX IF NOT EXISTS idx_competitor_prices_platform ON competitor_prices(platform);
CREATE INDEX IF NOT EXISTS idx_competitor_prices_recorded_at ON competitor_prices(recorded_at);

-- approval_tasks indexes
CREATE INDEX IF NOT EXISTS idx_approval_tasks_status ON approval_tasks(status);
CREATE INDEX IF NOT EXISTS idx_approval_tasks_shop_id ON approval_tasks(shop_id);
CREATE INDEX IF NOT EXISTS idx_approval_tasks_priority ON approval_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_approval_tasks_agent_task_id ON approval_tasks(agent_task_id);

-- subscriptions indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant_id ON subscriptions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

-- usage_records indexes
CREATE INDEX IF NOT EXISTS idx_usage_records_tenant_id ON usage_records(tenant_id);
CREATE INDEX IF NOT EXISTS idx_usage_records_resource_type ON usage_records(resource_type);
CREATE INDEX IF NOT EXISTS idx_usage_records_recorded_at ON usage_records(recorded_at);


-- ============================================================================
-- RLS POLICIES — shops
-- ============================================================================

-- Allow tenants to see only their own shops
CREATE POLICY shops_tenant_isolation_policy ON shops
    FOR ALL
    USING (tenant_id IS NULL OR tenant_id IN (
        SELECT id FROM tenants WHERE id = current_setting('app.current_tenant_id', TRUE)::UUID
    ));

-- ---------------------------------------------------------------------------
-- Helper function to update updated_at timestamps
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach triggers to tables with updated_at columns
CREATE TRIGGER update_shops_updated_at BEFORE UPDATE ON shops
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_adapters_updated_at BEFORE UPDATE ON platform_adapters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tenant_configs_updated_at BEFORE UPDATE ON tenant_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


COMMIT;
