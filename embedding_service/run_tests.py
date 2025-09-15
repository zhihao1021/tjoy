#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試執行腳本：可以選擇執行完整測試或簡化測試
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_complete_tests():
    """執行完整測試（需要模型載入）"""
    print("=== 執行完整測試 ===")
    try:
        from test_recommendation import run_tests
        return run_tests()
    except ImportError as e:
        print(f"無法導入完整測試模組: {e}")
        return False
    except Exception as e:
        print(f"完整測試執行失敗: {e}")
        return False

def run_simple_tests():
    """執行簡化測試（不需要模型載入）"""
    print("=== 執行簡化測試 ===")
    try:
        from test_recommendation_simple import run_simple_tests
        return run_simple_tests()
    except ImportError as e:
        print(f"無法導入簡化測試模組: {e}")
        return False
    except Exception as e:
        print(f"簡化測試執行失敗: {e}")
        return False

def main():
    """主程式"""
    print("推薦系統單元測試執行器")
    print("=" * 50)
    print("1. 完整測試（需要模型載入，測試推薦功能）")
    print("2. 簡化測試（不需要模型載入，測試資料結構和方法）")
    print("3. 執行所有測試")
    print("0. 退出")
    print("=" * 50)
    
    while True:
        try:
            choice = input("\n請選擇測試類型 (0-3): ").strip()
            
            if choice == "0":
                print("退出測試")
                break
            elif choice == "1":
                success = run_complete_tests()
                if success:
                    print("\n✅ 完整測試通過！")
                else:
                    print("\n❌ 完整測試失敗！")
            elif choice == "2":
                success = run_simple_tests()
                if success:
                    print("\n✅ 簡化測試通過！")
                else:
                    print("\n❌ 簡化測試失敗！")
            elif choice == "3":
                print("\n執行所有測試...")
                
                # 先執行簡化測試
                simple_success = run_simple_tests()
                
                # 再執行完整測試
                complete_success = run_complete_tests()
                
                if simple_success and complete_success:
                    print("\n✅ 所有測試通過！")
                else:
                    print("\n❌ 部分測試失敗！")
                    if not simple_success:
                        print("  - 簡化測試失敗")
                    if not complete_success:
                        print("  - 完整測試失敗")
            else:
                print("無效選擇，請輸入 0-3")
                
        except KeyboardInterrupt:
            print("\n\n測試被中斷")
            break
        except Exception as e:
            print(f"\n執行測試時發生錯誤: {e}")

if __name__ == "__main__":
    main()
