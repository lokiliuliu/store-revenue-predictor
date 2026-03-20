#!/usr/bin/env python3
"""
Streamlit应用测试脚本
用于验证应用的基本功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用中的函数
from app import calculate_location_score, predict_daily_orders, predict_aov

def test_calculate_location_score():
    """测试选址评分函数"""
    print("🧪 测试选址评分函数...")
    
    # 测试用例1: 优质选址
    score1 = calculate_location_score(
        road_type="Jalan utama",
        density="High",
        sekolah_count=3,
        masjid_count=2,
        toko_minuman=2,
        jumlah_bisnis=25
    )
    print(f"  优质选址评分: {score1}/100 (预期: 85-95)")
    
    # 测试用例2: 一般选址
    score2 = calculate_location_score(
        road_type="Jalan lokal",
        density="Low",
        sekolah_count=1,
        masjid_count=0,
        toko_minuman=6,
        jumlah_bisnis=8
    )
    print(f"  一般选址评分: {score2}/100 (预期: 55-65)")
    
    # 测试用例3: 良好选址
    score3 = calculate_location_score(
        road_type="Jalan antar kota",
        density="Medium",
        sekolah_count=2,
        masjid_count=1,
        toko_minuman=4,
        jumlah_bisnis=15
    )
    print(f"  良好选址评分: {score3}/100 (预期: 70-80)")
    
    # 验证评分范围
    assert 0 <= score1 <= 100, f"评分超出范围: {score1}"
    assert 0 <= score2 <= 100, f"评分超出范围: {score2}"
    assert 0 <= score3 <= 100, f"评分超出范围: {score3}"
    
    print("  ✅ 选址评分测试通过")

def test_predict_daily_orders():
    """测试日订单量预测函数"""
    print("🧪 测试日订单量预测函数...")
    
    # 测试用例
    orders1 = predict_daily_orders(
        location_score=90,
        store_area=100,
        population=200000,
        sekolah_count=3,
        masjid_count=2
    )
    print(f"  优质选址日订单量: {orders1}单 (预期: 150-250)")
    
    orders2 = predict_daily_orders(
        location_score=60,
        store_area=60,
        population=100000,
        sekolah_count=1,
        masjid_count=0
    )
    print(f"  一般选址日订单量: {orders2}单 (预期: 50-100)")
    
    # 验证合理性
    assert orders1 > 0, f"订单量应为正数: {orders1}"
    assert orders2 > 0, f"订单量应为正数: {orders2}"
    assert orders1 > orders2, f"优质选址应比一般选址订单量高"
    
    print("  ✅ 日订单量预测测试通过")

def test_predict_aov():
    """测试客单价预测函数"""
    print("🧪 测试客单价预测函数...")
    
    # 测试用例
    aov1 = predict_aov(
        location_score=90,
        road_type="Jalan utama",
        density="High",
        toko_minuman=2,
        jumlah_bisnis=25
    )
    print(f"  优质选址客单价: Rp {aov1:,} (预期: 35,000-45,000)")
    
    aov2 = predict_aov(
        location_score=60,
        road_type="Jalan lokal",
        density="Low",
        toko_minuman=6,
        jumlah_bisnis=8
    )
    print(f"  一般选址客单价: Rp {aov2:,} (预期: 25,000-35,000)")
    
    # 验证合理性
    assert aov1 > 0, f"客单价应为正数: {aov1}"
    assert aov2 > 0, f"客单价应为正数: {aov2}"
    assert aov1 > aov2, f"优质选址应比一般选址客单价高"
    
    print("  ✅ 客单价预测测试通过")

def test_integration():
    """测试集成预测"""
    print("🧪 测试集成预测...")
    
    # 完整预测流程
    location_score = calculate_location_score(
        road_type="Jalan utama",
        density="High",
        sekolah_count=3,
        masjid_count=2,
        toko_minuman=2,
        jumlah_bisnis=25
    )
    
    daily_orders = predict_daily_orders(
        location_score=location_score,
        store_area=100,
        population=200000,
        sekolah_count=3,
        masjid_count=2
    )
    
    aov = predict_aov(
        location_score=location_score,
        road_type="Jalan utama",
        density="High",
        toko_minuman=2,
        jumlah_bisnis=25
    )
    
    daily_revenue = daily_orders * aov
    
    print(f"  选址评分: {location_score}/100")
    print(f"  日订单量: {daily_orders:,}单")
    print(f"  客单价: Rp {aov:,}")
    print(f"  日营业额: Rp {daily_revenue:,}")
    
    # 验证营业额合理性
    assert daily_revenue > 0, f"营业额应为正数: {daily_revenue}"
    assert daily_revenue > 1000000, f"营业额应大于100万印尼盾"
    
    print("  ✅ 集成预测测试通过")

def main():
    """运行所有测试"""
    print("🚀 开始测试Streamlit应用功能")
    print("=" * 50)
    
    try:
        test_calculate_location_score()
        print()
        
        test_predict_daily_orders()
        print()
        
        test_predict_aov()
        print()
        
        test_integration()
        print()
        
        print("=" * 50)
        print("🎉 所有测试通过！应用功能正常")
        
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()