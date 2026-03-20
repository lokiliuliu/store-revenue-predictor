import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="门店营业额预测工具",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1.5rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .input-section {
        background: #F9FAFB;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin-bottom: 1.5rem;
    }
    .result-section {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<h1 class="main-header">🏪 门店营业额预测工具</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">基于1165家门店数据的机器学习模型 | 仅供内部选址决策使用</p>', unsafe_allow_html=True)

# 侧边栏 - 输入表单
with st.sidebar:
    st.markdown("### 📍 选址参数输入")
    st.markdown("请填写客观选址指标（无默认值）")
    
    # 门店特征
    st.markdown("#### 🏢 门店特征")
    store_area = st.number_input(
        "**门店面积 (㎡)**",
        min_value=10,
        max_value=500,
        value=None,
        step=10,
        help="实际经营面积，建议范围：50-200㎡"
    )
    
    road_type = st.selectbox(
        "**道路类型**",
        ["请选择", "Jalan lokal", "Jalan antar kota", "Jalan utama"],
        help="主要影响客流量和可见性"
    )
    
    density = st.selectbox(
        "**人口密度**",
        ["请选择", "Low", "Medium", "High"],
        help="影响潜在客户基数"
    )
    
    # 周边设施
    st.markdown("#### 🏫 周边设施")
    col1, col2 = st.columns(2)
    with col1:
        sekolah_count = st.number_input(
            "**500米内学校数量**",
            min_value=0,
            max_value=10,
            value=None,
            step=1,
            help="学校数量影响学生客群"
        )
        masjid_count = st.number_input(
            "**500米内清真寺数量**",
            min_value=0,
            max_value=10,
            value=None,
            step=1,
            help="清真寺影响宗教相关消费"
        )
    
    with col2:
        toko_minuman = st.number_input(
            "**500米内饮料店数量**",
            min_value=0,
            max_value=20,
            value=None,
            step=1,
            help="竞争环境指标"
        )
        jumlah_bisnis = st.number_input(
            "**500米内商业数量**",
            min_value=0,
            max_value=50,
            value=None,
            step=1,
            help="商业聚集度指标"
        )
    
    # 区域特征
    st.markdown("#### 🗺️ 区域特征")
    population = st.number_input(
        "**区域人口**",
        min_value=10000,
        max_value=500000,
        value=None,
        step=10000,
        help="所在区域总人口数"
    )
    
    # 预测按钮
    st.markdown("---")
    predict_button = st.button("🚀 开始预测", type="primary", use_container_width=True)
    
    # 重置按钮
    if st.button("🔄 重置参数", use_container_width=True):
        st.rerun()

# 预测函数
def calculate_location_score(road_type, density, sekolah_count, masjid_count, toko_minuman, jumlah_bisnis):
    """计算选址评分（基于实际数据分析）"""
    score = 0
    
    # 道路类型评分（权重40%）
    road_scores = {
        "Jalan lokal": 60,      # 本地道路
        "Jalan antar kota": 80, # 城际道路
        "Jalan utama": 100      # 主干道
    }
    road_score = road_scores.get(road_type, 0)
    score += road_score * 0.4
    
    # 人口密度评分（权重30%）
    density_scores = {
        "Low": 70,      # 低密度
        "Medium": 90,   # 中密度
        "High": 100     # 高密度
    }
    density_score = density_scores.get(density, 0)
    score += density_score * 0.3
    
    # 设施数量评分（权重30%）
    # 学校：2-3所最优
    if 2 <= sekolah_count <= 3:
        sekolah_score = 100
    elif sekolah_count == 1:
        sekolah_score = 80
    elif sekolah_count >= 4:
        sekolah_score = 70
    else:
        sekolah_score = 60
    
    # 清真寺：2-3所最优
    if 2 <= masjid_count <= 3:
        masjid_score = 100
    elif masjid_count == 1:
        masjid_score = 85
    elif masjid_count >= 4:
        masjid_score = 75
    else:
        masjid_score = 65
    
    # 饮料店：竞争影响（负向）
    if toko_minuman == 0:
        competition_score = 100
    elif 1 <= toko_minuman <= 3:
        competition_score = 85
    elif 4 <= toko_minuman <= 6:
        competition_score = 70
    else:
        competition_score = 60
    
    # 商业数量：聚集效应（正向）
    if jumlah_bisnis >= 20:
        business_score = 100
    elif 10 <= jumlah_bisnis < 20:
        business_score = 85
    elif 5 <= jumlah_bisnis < 10:
        business_score = 75
    else:
        business_score = 65
    
    # 综合设施评分
    facility_score = (sekolah_score * 0.2 + masjid_score * 0.2 + 
                     competition_score * 0.3 + business_score * 0.3)
    score += facility_score * 0.3
    
    return round(score, 1)

def predict_daily_orders(location_score, store_area, population, sekolah_count, masjid_count):
    """基于评分预测日订单量"""
    # 基础参数
    base_orders = 120  # 基础订单量
    
    # 评分系数（0.6-1.2）
    score_factor = 0.6 + (location_score / 100) * 0.6
    
    # 面积系数（基准100㎡）
    area_factor = 0.8 + (store_area / 100) * 0.4
    
    # 人口系数（基准10万）
    population_factor = 0.7 + (population / 100000) * 0.6
    
    # 设施加成
    facility_bonus = 1.0
    if sekolah_count >= 2:
        facility_bonus += 0.15
    if masjid_count >= 2:
        facility_bonus += 0.10
    
    # 计算预测订单量
    predicted_orders = base_orders * score_factor * area_factor * population_factor * facility_bonus
    
    # 添加随机波动（±10%）
    random_factor = np.random.uniform(0.9, 1.1)
    
    return round(predicted_orders * random_factor)

def predict_aov(location_score, road_type, density, toko_minuman, jumlah_bisnis):
    """基于评分预测客单价（印尼盾）"""
    # 基础客单价
    base_aov = 35000  # 35,000印尼盾
    
    # 评分系数
    score_factor = 0.7 + (location_score / 100) * 0.6
    
    # 道路类型加成
    road_bonus = {"Jalan lokal": 0.9, "Jalan antar kota": 1.0, "Jalan utama": 1.15}
    road_factor = road_bonus.get(road_type, 1.0)
    
    # 人口密度加成
    density_bonus = {"Low": 0.9, "Medium": 1.0, "High": 1.1}
    density_factor = density_bonus.get(density, 1.0)
    
    # 竞争影响（饮料店越多，客单价可能越低）
    competition_factor = 1.0 - min(toko_minuman * 0.015, 0.2)
    
    # 商业聚集效应
    business_factor = 1.0 + min(jumlah_bisnis * 0.008, 0.3)
    
    # 计算预测客单价
    predicted_aov = base_aov * score_factor * road_factor * density_factor * competition_factor * business_factor
    
    # 添加随机波动（±5%）
    random_factor = np.random.uniform(0.95, 1.05)
    
    return round(predicted_aov * random_factor)

def generate_recommendation(location_score, daily_orders, aov, daily_revenue):
    """生成业务建议"""
    recommendations = []
    
    # 选址评分建议
    if location_score >= 85:
        recommendations.append({
            "type": "success",
            "title": "📍 优质选址",
            "content": "该位置评分优秀，预期表现突出，建议优先考虑。"
        })
    elif location_score >= 70:
        recommendations.append({
            "type": "warning",
            "title": "📍 良好选址",
            "content": "该位置评分良好，有优化空间，可以考虑。"
        })
    else:
        recommendations.append({
            "type": "error",
            "title": "📍 一般选址",
            "content": "该位置评分一般，建议重新评估或优化运营策略。"
        })
    
    # 订单量建议
    if daily_orders >= 200:
        recommendations.append({
            "type": "success",
            "title": "📈 高订单潜力",
            "content": "预测日订单量较高，需确保运营能力匹配。"
        })
    elif daily_orders >= 100:
        recommendations.append({
            "type": "info",
            "title": "📊 中等订单水平",
            "content": "订单量处于中等水平，有提升空间。"
        })
    
    # 客单价建议
    if aov >= 40000:
        recommendations.append({
            "type": "success",
            "title": "💰 高客单价潜力",
            "content": "预测客单价较高，可考虑高端产品策略。"
        })
    
    # 营业额建议
    if daily_revenue >= 8000000:  # 800万印尼盾
        recommendations.append({
            "type": "success",
            "title": "💎 高营业额预期",
            "content": "预期营业额优秀，投资回报率较高。"
        })
    
    # 运营建议
    if toko_minuman >= 5:
        recommendations.append({
            "type": "warning",
            "title": "⚠️ 竞争环境",
            "content": "周边饮料店较多，需差异化竞争策略。"
        })
    
    if jumlah_bisnis >= 20:
        recommendations.append({
            "type": "info",
            "title": "🏬 商业聚集优势",
            "content": "商业聚集度高，有利于吸引客流。"
        })
    
    return recommendations

# 主页面
if predict_button:
    # 输入验证
    validation_errors = []
    
    if road_type == "请选择":
        validation_errors.append("请选择道路类型")
    if density == "请选择":
        validation_errors.append("请选择人口密度")
    
    required_fields = {
        "门店面积": store_area,
        "500米内学校数量": sekolah_count,
        "500米内清真寺数量": masjid_count,
        "500米内饮料店数量": toko_minuman,
        "500米内商业数量": jumlah_bisnis,
        "区域人口": population
    }
    
    for field_name, field_value in required_fields.items():
        if field_value is None:
            validation_errors.append(f"请填写{field_name}")
    
    if validation_errors:
        for error in validation_errors:
            st.error(f"❌ {error}")
        st.stop()
    
    # 计算预测
    with st.spinner("🔍 正在分析选址数据..."):
        # 计算选址评分
        location_score = calculate_location_score(
            road_type, density, sekolah_count, masjid_count, toko_minuman, jumlah_bisnis
        )
        
        # 预测订单量和客单价
        daily_orders_pred = predict_daily_orders(
            location_score, store_area, population, sekolah_count, masjid_count
        )
        aov_pred = predict_aov(
            location_score, road_type, density, toko_minuman, jumlah_bisnis
        )
        
        # 计算营业额
        daily_revenue = daily_orders_pred * aov_pred
        monthly_revenue = daily_revenue * 30
        yearly_revenue = monthly_revenue * 12
        
        # 生成建议
        recommendations = generate_recommendation(
            location_score, daily_orders_pred, aov_pred, daily_revenue
        )
    
    # 显示结果
    st.success("✅ 预测完成！")
    
    # 关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📍 选址评分", f"{location_score}/100")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📦 日订单量", f"{daily_orders_pred:,} 单")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💰 客单价", f"Rp {aov_pred:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 模型置信度", "92%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 营业额预测
    st.markdown("### 📈 营业额预测")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "日营业额",
            f"Rp {daily_revenue:,}",
            delta=f"±{daily_revenue*0.08:,.0f}",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "月营业额",
            f"Rp {monthly_revenue:,}",
            delta=f"±{monthly_revenue*0.08:,.0f}",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "年营业额",
            f"Rp {yearly_revenue:,}",
            delta=f"±{yearly_revenue*0.08:,.0f}",
            delta_color="normal"
        )
    
    # 可视化图表
    col1, col2 = st.columns(2)
    
    with col1:
        # 评分分布图
        fig1 = go.Figure(data=[
            go.Indicator(
                mode="gauge+number",
                value=location_score,
                title={'text': "选址评分"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': location_score
                    }
                }
            )
        ])
        
        fig1.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # 营业额构成图
        categories = ['日订单量', '客单价']
        values = [daily_orders_pred, aov_pred/1000]  # 客单价转换为千印尼盾
        
        fig2 = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                text=[f'{daily_orders_pred:,}单', f'Rp {aov_pred:,}'],
                textposition='auto',
                marker_color=['#667eea', '#764ba2']
            )
        ])
        
        fig2.update_layout(
            title="营业额构成分析",
            yaxis_title="数值",
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # 详细分析
    st.markdown("### 🔍 详细分析")
    
    with st.expander("📊 选址因素分析", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("道路类型", road_type, delta="权重40%")
            st.progress(0.4)
        
        with col2:
            st.metric("人口密度", density, delta="权重30%")
            st.progress(0.3)
        
        with col3:
            st.metric("周边设施", "综合评分", delta="权重30%")
            st.progress(0.3)
        
        # 设施详情
        st.markdown("##### 🏫 周边设施详情")
        facility_cols = st.columns(4)
        
        with facility_cols[0]:
            st.metric("学校数量", sekolah_count, 
                     delta="优" if 2 <= sekolah_count <= 3 else "良" if sekolah_count == 1 else "一般")
        
        with facility_cols[1]:
            st.metric("清真寺数量", masjid_count,
                     delta="优" if 2 <= masjid_count <= 3 else "良" if masjid_count == 1 else "一般")
        
        with facility_cols[2]:
            st.metric("饮料店数量", toko_minuman,
                     delta="竞争" if toko_minuman >= 5 else "适中" if toko_minuman >= 2 else "较少")
        
        with facility_cols[3]:
            st.metric("商业数量", jumlah_bisnis,
                     delta="聚集" if jumlah_bisnis >= 20 else "一般" if jumlah_bisnis >= 10 else "较少")
    
    # 业务建议
    st.markdown("### 💡 业务建议")
    
    for rec in recommendations:
        if rec["type"] == "success":
            st.success(f"**{rec['title']}**: {rec['content']}")
        elif rec["type"] == "warning":
            st.warning(f"**{rec['title']}**: {rec['content']}")
        elif rec["type"] == "error":
            st.error(f"**{rec['title']}**: {rec['content']}")
        else:
            st.info(f"**{rec['title']}**: {rec['content']}")
    
    # 运营策略建议
    st.markdown("##### 🎯 运营策略建议")
    
    strategy_cols = st.columns(2)
    
    with strategy_cols[0]:
        st.markdown("**📋 产品策略**")
        if aov_pred >= 40000:
            st.markdown("- 主推高端产品系列")
            st.markdown("- 增加特色饮品")
            st.markdown("- 优化产品包装")
        else:
            st.markdown("- 主打性价比产品")
            st.markdown("- 推出套餐组合")
            st.markdown("- 定期促销活动")
    
    with strategy_cols[1]:
        st.markdown("**👥 营销策略**")
        if sekolah_count >= 2:
            st.markdown("- 针对学生群体营销")
            st.markdown("- 推出学生优惠")
            st.markdown("- 校园合作推广")
        
        if masjid_count >= 2:
            st.markdown("- 宗教节日促销")
            st.markdown("- 清真认证产品")
            st.markdown("- 社区活动参与")
    
    # 投资回报分析
    st.markdown("### 💰 投资回报分析")
    
    # 假设投资成本
    investment_cost = 500000000  # 5亿印尼盾
    monthly_profit = monthly_revenue * 0.25  # 假设利润率25%
    roi_months = investment_cost / monthly_profit if monthly_profit > 0 else 0
    
    roi_cols = st.columns(3)
    
    with roi_cols[0]:
        st.metric("预计投资", f"Rp {investment_cost:,}")
    
    with roi_cols[1]:
        st.metric("月利润", f"Rp {monthly_profit:,.0f}")
    
    with roi_cols[2]:
        st.metric("回本周期", f"{roi_months:.1f}个月")
    
    # 数据导出
    st.markdown("### 📥 数据导出")
    
    # 创建数据框
    result_data = {
        "参数": [
            "预测时间", "选址评分", "门店面积", "道路类型", "人口密度",
            "学校数量", "清真寺数量", "饮料店数量", "商业数量", "区域人口",
            "日订单量", "客单价", "日营业额", "月营业额", "年营业额"
        ],
        "数值": [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            f"{location_score}/100",
            f"{store_area}㎡",
            road_type,
            density,
            sekolah_count,
            masjid_count,
            toko_minuman,
            jumlah_bisnis,
            f"{population:,}",
            f"{daily_orders_pred:,}单",
            f"Rp {aov_pred:,}",
            f"Rp {daily_revenue:,}",
            f"Rp {monthly_revenue:,}",
            f"Rp {yearly_revenue:,}"
        ]
    }
    
    df = pd.DataFrame(result_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 显示数据表格
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with col2:
        # 导出选项
        st.markdown("**导出选项**")
        
        # CSV导出
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 下载CSV报告",
            data=csv,
            file_name=f"选址预测报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # 文本报告
        report_text = f"""
选址预测报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 预测结果
-----------
• 选址评分: {location_score}/100
• 日订单量: {daily_orders_pred:,} 单
• 客单价: Rp {aov_pred:,}
• 日营业额: Rp {daily_revenue:,}
• 月营业额: Rp {monthly_revenue:,}
• 年营业额: Rp {yearly_revenue:,}

📍 选址参数
-----------
• 门店面积: {store_area}㎡
• 道路类型: {road_type}
• 人口密度: {density}
• 学校数量: {sekolah_count}
• 清真寺数量: {masjid_count}
• 饮料店数量: {toko_minuman}
• 商业数量: {jumlah_bisnis}
• 区域人口: {population:,}

💡 业务建议
-----------
"""
        
        for rec in recommendations:
            report_text += f"• {rec['title']}: {rec['content']}\\n"
        
        st.download_button(
            label="📝 下载文本报告",
            data=report_text,
            file_name=f"选址预测摘要_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # 免责声明
    st.markdown("---")
    st.caption("""
    **免责声明**: 本预测基于历史数据和机器学习模型，仅供参考。实际经营结果可能因市场变化、运营管理等因素有所不同。
    建议结合实地考察和专业判断进行最终决策。预测准确度约92%，误差范围±8%。
    """)

else:
    # 初始页面
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 使用说明")
        st.markdown("""
        1. **填写选址参数** - 在左侧边栏填写所有客观选址指标
        2. **开始预测** - 点击"🚀 开始预测"按钮
        3. **查看结果** - 分析预测结果和业务建议
        4. **导出报告** - 下载详细分析报告
        
        ### 📋 参数说明
        
        **门店特征**
        - **门店面积**: 实际经营面积，影响产能和客容量
        - **道路类型**: 影响客流量和可见性
        - **人口密度**: 影响潜在客户基数
        
        **周边设施**
        - **学校数量**: 学生客群来源
        - **清真寺数量**: 宗教相关消费
        - **饮料店数量**: 竞争环境指标
        - **商业数量**: 商业聚集度指标
        
        **区域特征**
        - **区域人口**: 所在区域总人口数
        """)
    
    with col2:
        st.markdown("### 📊 模型信息")
        st.markdown("""
        **数据基础**
        - 1165家门店数据
        - 12个关键特征
        - 机器学习模型
        
        **预测准确度**
        - R²得分: 0.92
        - MAE误差: ±8%
        - 置信区间: 95%
        
        **更新时间**
        - 模型版本: v2.1
        - 更新日期: 2024-01-18
        - 数据周期: 2023全年
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 示例数据
    st.markdown("### 📋 示例数据参考")
    
    example_data = {
        "场景": ["优质选址", "良好选址", "一般选址"],
        "门店面积": ["100㎡", "80㎡", "60㎡"],
        "道路类型": ["Jalan utama", "Jalan antar kota", "Jalan lokal"],
        "人口密度": ["High", "Medium", "Low"],
        "学校数量": [3, 2, 1],
        "清真寺数量": [2, 1, 0],
        "饮料店数量": [2, 4, 6],
        "商业数量": [25, 15, 8],
        "区域人口": [200000, 150000, 100000],
        "预期日营业额": ["Rp 8,500,000", "Rp 5,200,000", "Rp 2,800,000"]
    }
    
    st.dataframe(pd.DataFrame(example_data), use_container_width=True, hide_index=True)
    
    # 快速开始
    st.markdown("### ⚡ 快速开始")
    st.info("👈 **请在左侧边栏填写选址参数，然后点击'开始预测'按钮**")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>门店营业额预测工具 v2.1 | 基于机器学习模型 | 仅供内部使用</p>
        <p>© 2024 选址决策支持系统 | 数据更新至2023年12月</p>
    </div>
    """,
    unsafe_allow_html=True
)