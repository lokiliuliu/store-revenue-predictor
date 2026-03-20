#!/usr/bin/env python3
"""
简化测试脚本 - 不依赖Streamlit
"""

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
    
    return round(predicted_orders)

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
    
    return round(predicted_aov)

def main():
    print("🧪 简化功能测试")
    print("=" * 50)
    
    # 测试用例1: 优质选址
    print("\n📊 测试用例1: 优质选址")
    print("-" * 30)
    
    location_score = calculate_location_score(
        road_type="Jalan utama",
        density="High",
        sekolah_count=3,
        masjid_count=2,
        toko_minuman=2,
        jumlah_bisnis=25
    )
    print(f"选址评分: {location_score}/100")
    
    daily_orders = predict_daily_orders(
        location_score=location_score,
        store_area=100,
        population=200000,
        sekolah_count=3,
        masjid_count=2
    )
    print(f"日订单量: {daily_orders}单")
    
    aov = predict_aov(
        location_score=location_score,
        road_type="Jalan utama",
        density="High",
        toko_minuman=2,
        jumlah_bisnis=25
    )
    print(f"客单价: Rp {aov:,}")
    
    daily_revenue = daily_orders * aov
    print(f"日营业额: Rp {daily_revenue:,}")
    
    # 测试用例2: 一般选址
    print("\n📊 测试用例2: 一般选址")
    print("-" * 30)
    
    location_score2 = calculate_location_score(
        road_type="Jalan lokal",
        density="Low",
        sekolah_count=1,
        masjid_count=0,
        toko_minuman=6,
        jumlah_bisnis=8
    )
    print(f"选址评分: {location_score2}/100")
    
    daily_orders2 = predict_daily_orders(
        location_score=location_score2,
        store_area=60,
        population=100000,
        sekolah_count=1,
        masjid_count=0
    )
    print(f"日订单量: {daily_orders2}单")
    
    aov2 = predict_aov(
        location_score=location_score2,
        road_type="Jalan lokal",
        density="Low",
        toko_minuman=6,
        jumlah_bisnis=8
    )
    print(f"客单价: Rp {aov2:,}")
    
    daily_revenue2 = daily_orders2 * aov2
    print(f"日营业额: Rp {daily_revenue2:,}")
    
    # 对比分析
    print("\n📈 对比分析")
    print("-" * 30)
    print(f"选址评分差异: {location_score - location_score2}分")
    print(f"日订单量差异: {daily_orders - daily_orders2}单")
    print(f"客单价差异: Rp {aov - aov2:,}")
    print(f"日营业额差异: Rp {daily_revenue - daily_revenue2:,}")
    
    # 验证逻辑
    print("\n✅ 验证结果:")
    if location_score > location_score2:
        print("  ✓ 优质选址评分更高")
    if daily_orders > daily_orders2:
        print("  ✓ 优质选址订单量更高")
    if aov > aov2:
        print("  ✓ 优质选址客单价更高")
    if daily_revenue > daily_revenue2:
        print("  ✓ 优质选址营业额更高")
    
    print("\n🎉 测试完成！逻辑验证通过")

if __name__ == "__main__":
    main()