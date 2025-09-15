#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化單元測試：不依賴模型載入的測試
主要測試資料結構和方法邏輯
"""

import unittest
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embedding_service.embedding import ActivityRecommendationSystemGemma
from model.user import UserModel
from model.article import ArticleModel
from model.category import CategoryModel


class TestRecommendationSystemSimple(unittest.TestCase):
    """推薦系統簡化單元測試（不依賴模型載入）"""
    
    def setUp(self):
        """測試前的設置"""
        self.recommendation_system = ActivityRecommendationSystemGemma()
        
        # 創建測試資料
        self.categories = self._create_categories()
        self.users = self._create_users()
        self.events = self._create_events()
    
    def _create_categories(self):
        """創建測試類別"""
        categories = []
        
        category_data = [
            {"id": 1, "name": "程式設計"},
            {"id": 2, "name": "音樂"},
            {"id": 3, "name": "運動"},
            {"id": 4, "name": "藝術"},
            {"id": 5, "name": "美食"}
        ]
        
        for data in category_data:
            category = CategoryModel()
            category.id = data["id"]
            category.name = data["name"]
            categories.append(category)
        
        return categories
    
    def _create_users(self):
        """創建測試使用者"""
        users = []
        
        user_data = [
            {
                "id": 1, "username": "alice", "display_name": "愛麗絲",
                "department": "資訊工程系", "gender": "女"
            },
            {
                "id": 2, "username": "bob", "display_name": "鮑伯",
                "department": "音樂系", "gender": "男"
            },
            {
                "id": 3, "username": "charlie", "display_name": "查理",
                "department": "體育系", "gender": "男"
            },
            {
                "id": 4, "username": "diana", "display_name": "黛安娜",
                "department": "美術系", "gender": "女"
            },
            {
                "id": 5, "username": "eve", "display_name": "夏娃",
                "department": "餐飲系", "gender": "女"
            }
        ]
        
        for data in user_data:
            user = UserModel()
            user.id = data["id"]
            user.username = data["username"]
            user.display_name = data["display_name"]
            user.department = data["department"]
            user.gender = data["gender"]
            user.password_hash = "hashed_password"
            
            # 初始化關聯資料
            user.interest_articles = []
            user.follow_categories = []
            user.article_histories = []
            user.search_histories = []
            user.join_events = []
            
            users.append(user)
        
        return users
    
    def _create_events(self):
        """創建測試活動"""
        events = []
        
        event_data = [
            {
                "id": 1, "title": "Python 程式設計工作坊",
                "content": "學習 Python 基礎語法和應用開發，適合初學者",
                "tags": "程式設計,Python,教學",
                "category": "程式設計"
            },
            {
                "id": 2, "title": "古典音樂演奏會",
                "content": "貝多芬第九交響曲演奏會，由知名交響樂團演出",
                "tags": "音樂,古典,演奏",
                "category": "音樂"
            },
            {
                "id": 3, "title": "籃球友誼賽",
                "content": "系際籃球友誼賽，歡迎各系同學參加",
                "tags": "運動,籃球,比賽",
                "category": "運動"
            },
            {
                "id": 4, "title": "水彩畫展覽",
                "content": "學生水彩畫作品展覽，展示創意與技巧",
                "tags": "藝術,繪畫,展覽",
                "category": "藝術"
            },
            {
                "id": 5, "title": "法式料理課程",
                "content": "學習製作經典法式料理，從基礎到進階",
                "tags": "美食,烹飪,法式",
                "category": "美食"
            },
            {
                "id": 6, "title": "機器學習研討會",
                "content": "深度學習與人工智慧最新發展研討會",
                "tags": "程式設計,機器學習,AI",
                "category": "程式設計"
            },
            {
                "id": 7, "title": "爵士樂即興演奏",
                "content": "爵士樂即興演奏工作坊，體驗音樂的無限可能",
                "tags": "音樂,爵士,即興",
                "category": "音樂"
            },
            {
                "id": 8, "title": "瑜珈課程",
                "content": "初級瑜珈課程，放鬆身心，提升柔軟度",
                "tags": "運動,瑜珈,健康",
                "category": "運動"
            },
            {
                "id": 9, "title": "攝影技巧講座",
                "content": "專業攝影技巧講座，學習構圖與光影運用",
                "tags": "藝術,攝影,技巧",
                "category": "藝術"
            },
            {
                "id": 10, "title": "日式料理體驗",
                "content": "學習製作壽司和日式料理，體驗日本飲食文化",
                "tags": "美食,日式,壽司",
                "category": "美食"
            }
        ]
        
        for data in event_data:
            event = ArticleModel()
            event.id = data["id"]
            event.title = data["title"]
            event.content = data["content"]
            event.tags = data["tags"]
            event.is_event = True
            event.is_public = True
            event.author = self.users[0]  # 使用第一個使用者作為作者
            
            # 設定類別
            for category in self.categories:
                if category.name == data["category"]:
                    event.category = category
                    break
            
            events.append(event)
        
        return events
    
    def test_initialization(self):
        """測試初始化"""
        self.assertIsNone(self.recommendation_system.user_data)
        self.assertEqual(len(self.recommendation_system.events_data), 0)
        self.assertIsNone(self.recommendation_system.user_embedding)
        self.assertEqual(len(self.recommendation_system.event_embeddings), 0)
    
    def test_set_user(self):
        """測試設定使用者"""
        user = self.users[0]
        self.recommendation_system.set_user(user)
        
        self.assertEqual(self.recommendation_system.user_data, user)
        self.assertIsNone(self.recommendation_system.user_embedding)
    
    def test_add_event_data(self):
        """測試新增活動資料"""
        event = self.events[0]
        self.recommendation_system.add_event_data("event_1", event)
        
        self.assertEqual(self.recommendation_system.events_data["event_1"], event)
        self.assertEqual(len(self.recommendation_system.events_data), 1)
    
    def test_add_event_data_invalid(self):
        """測試新增非活動資料（應該拋出錯誤）"""
        # 創建一個非活動的文章
        article = ArticleModel()
        article.id = 999
        article.title = "普通文章"
        article.content = "這不是活動"
        article.is_event = False  # 不是活動
        article.is_public = True
        
        with self.assertRaises(ValueError):
            self.recommendation_system.add_event_data("invalid_event", article)
    
    def test_recommend_events_no_user(self):
        """測試未設定使用者時推薦（應該拋出錯誤）"""
        # 新增一些活動
        for i, event in enumerate(self.events[:3]):
            self.recommendation_system.add_event_data(f"event_{i}", event)
        
        with self.assertRaises(ValueError):
            self.recommendation_system.recommend_events()
    
    def test_recommend_events_no_events(self):
        """測試沒有活動時推薦（應該拋出錯誤）"""
        # 設定使用者但沒有活動
        self.recommendation_system.set_user(self.users[0])
        
        with self.assertRaises(ValueError):
            self.recommendation_system.recommend_events()
    
    def test_create_user_profile_embedding_no_user(self):
        """測試未設定使用者時創建嵌入向量（應該拋出錯誤）"""
        with self.assertRaises(ValueError):
            self.recommendation_system.create_user_profile_embedding()
    
    def test_create_event_embedding_no_event(self):
        """測試不存在活動時創建嵌入向量（應該拋出錯誤）"""
        with self.assertRaises(ValueError):
            self.recommendation_system.create_event_embedding("nonexistent_event")
    
    def test_calculate_tag_similarity(self):
        """測試標籤相似度計算"""
        # 設定使用者和活動
        user = self.users[0]  # 愛麗絲
        event = self.events[0]  # Python 工作坊
        
        self.recommendation_system.set_user(user)
        self.recommendation_system.add_event_data("event_1", event)
        
        # 計算標籤相似度
        similarity = self.recommendation_system.calculate_tag_similarity("event_1")
        
        # 驗證結果
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
    
    def test_calculate_board_similarity(self):
        """測試類別相似度計算"""
        # 設定使用者和活動
        user = self.users[0]  # 愛麗絲
        event = self.events[0]  # Python 工作坊
        
        self.recommendation_system.set_user(user)
        self.recommendation_system.add_event_data("event_1", event)
        
        # 計算類別相似度
        similarity = self.recommendation_system.calculate_board_similarity("event_1")
        
        # 驗證結果
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
    
    def test_calculate_behavioral_similarity(self):
        """測試行為相似度計算"""
        # 設定使用者和活動
        user = self.users[0]  # 愛麗絲
        event = self.events[0]  # Python 工作坊
        
        self.recommendation_system.set_user(user)
        self.recommendation_system.add_event_data("event_1", event)
        
        # 計算行為相似度
        similarity = self.recommendation_system.calculate_behavioral_similarity("event_1")
        
        # 驗證結果
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
    
    def test_calculate_search_relevance(self):
        """測試搜尋相關性計算"""
        # 設定使用者和活動
        user = self.users[0]  # 愛麗絲
        event = self.events[0]  # Python 工作坊
        
        self.recommendation_system.set_user(user)
        self.recommendation_system.add_event_data("event_1", event)
        
        # 計算搜尋相關性
        relevance = self.recommendation_system.calculate_search_relevance("event_1")
        
        # 驗證結果
        self.assertIsInstance(relevance, float)
        self.assertGreaterEqual(relevance, 0.0)
        self.assertLessEqual(relevance, 1.0)
    
    def test_calculate_comprehensive_score(self):
        """測試綜合分數計算"""
        # 設定使用者和活動
        user = self.users[0]  # 愛麗絲
        event = self.events[0]  # Python 工作坊
        
        self.recommendation_system.set_user(user)
        self.recommendation_system.add_event_data("event_1", event)
        
        # 計算綜合分數
        scores = self.recommendation_system.calculate_comprehensive_score("event_1")
        
        # 驗證分數結構
        expected_keys = ['content_similarity', 'tag_similarity', 'board_similarity', 
                        'behavioral_similarity', 'search_relevance', 'total_score']
        for key in expected_keys:
            self.assertIn(key, scores)
            self.assertIsInstance(scores[key], float)
            self.assertGreaterEqual(scores[key], 0.0)
            self.assertLessEqual(scores[key], 1.0)
    
    def test_data_creation(self):
        """測試資料創建"""
        # 驗證使用者資料
        self.assertEqual(len(self.users), 5)
        self.assertEqual(self.users[0].display_name, "愛麗絲")
        self.assertEqual(self.users[1].display_name, "鮑伯")
        self.assertEqual(self.users[2].display_name, "查理")
        self.assertEqual(self.users[3].display_name, "黛安娜")
        self.assertEqual(self.users[4].display_name, "夏娃")
        
        # 驗證活動資料
        self.assertEqual(len(self.events), 10)
        self.assertEqual(self.events[0].title, "Python 程式設計工作坊")
        self.assertEqual(self.events[1].title, "古典音樂演奏會")
        self.assertEqual(self.events[2].title, "籃球友誼賽")
        
        # 驗證類別資料
        self.assertEqual(len(self.categories), 5)
        category_names = [cat.name for cat in self.categories]
        expected_categories = ["程式設計", "音樂", "運動", "藝術", "美食"]
        self.assertEqual(category_names, expected_categories)


def run_simple_tests():
    """執行簡化測試"""
    # 創建測試套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRecommendationSystemSimple)
    
    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回測試結果
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=== 推薦系統簡化單元測試 ===")
    print("創建 5 個使用者和 10 個活動進行測試（不依賴模型載入）...")
    print()
    
    success = run_simple_tests()
    
    if success:
        print("\n✅ 所有測試通過！")
    else:
        print("\n❌ 部分測試失敗！")
    
    print("\n測試完成！")
