import numpy as np
from transformers import AutoModel, AutoTokenizer
import torch
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Set
import time
from model.user import UserModel
from model.article import ArticleModel

class ActivityRecommendationSystemGemma:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2', device='auto'):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self.user_data = None  # 單一使用者資料
        self.events_data = {}
        self.user_embedding = None
        self.event_embeddings = {}
        
        # 權重設定
        self.weights = {
            'interest_tags': 0.3,
            'subscribed_boards': 0.2,
            'browsing_history': 0.2,
            'engagement_history': 0.2,
            'search_keywords': 0.1
        }
        
    def load_model(self):
        """Loading EmbeddingGemma model"""
        try:
            print("Loading EmbeddingGemma model...")
            start_time = time.time()
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            self.model = AutoModel.from_pretrained(self.model_name)
            
            if self.device == 'auto':
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            
            self.model = self.model.to(self.device)
            self.model.eval() 
            
        except Exception as e:
            print(f"Model loading failed: {e}")
            raise
    
    def get_embedding(self, text: str) -> np.ndarray:

        if not self.model or not self.tokenizer:
            raise ValueError("Model not loaded, please call load_model()")
        
        start_time = time.time()
        
        try:
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1)
                embedding = embedding.cpu().numpy().flatten()
            
            encoding_time = time.time() - start_time
            
            return embedding
            
        except Exception as e:
            print(f"Error：{e}")
            raise
    
    def set_user(self, user_model: UserModel):
        """
        設定使用者資料
        
        Args:
            user_model: UserModel 實例
        """
        self.user_data = user_model
        self.user_embedding = None  # 重置使用者嵌入向量
        
    def add_event_data(self, event_id: str, article_model: ArticleModel):
        """
        新增活動資料
        
        Args:
            event_id: 活動ID
            article_model: ArticleModel 實例 (is_event=True)
        """
        if not article_model.is_event:
            raise ValueError("ArticleModel 必須是活動 (is_event=True)")
        self.events_data[event_id] = article_model
    
    def create_user_profile_embedding(self) -> np.ndarray:
        """
        為使用者創建綜合檔案向量
        
        Returns:
            使用者的綜合向量表示
        """
        if self.user_data is None:
            raise ValueError("使用者資料尚未設定，請先調用 set_user()")
        
        # 如果已經計算過，直接回傳快取的結果
        if self.user_embedding is not None:
            return self.user_embedding
        
        user_model = self.user_data
        
        # Collect all text data
        text_parts = []
        
        # 1. Basic data
        text_parts.append(user_model.display_name)
        if user_model.department:
            text_parts.append(user_model.department)
        
        # 2. Interest article tags
        if user_model.interest_articles:
            interest_tags = []
            for article in user_model.interest_articles:
                if article.tags:
                    interest_tags.extend(article.tags.split(','))
            if interest_tags:
                text_parts.append(" ".join(interest_tags))
        
        # 3. Followed categories
        if user_model.follow_categories:
            category_names = [cat.name for cat in user_model.follow_categories]
            text_parts.append(" ".join(category_names))
        
        # 4. Browsing history (article title)
        if user_model.article_histories:
            history_titles = [article.title for article in user_model.article_histories]
            text_parts.append(" ".join(history_titles))
        
        # 5. Search history
        if user_model.search_histories:
            search_queries = [history.query for history in user_model.search_histories]
            text_parts.append(" ".join(search_queries))
        
        # 6. Joined events
        if user_model.join_events:
            event_titles = [event.title for event in user_model.join_events]
            text_parts.append(" ".join(event_titles))
        
        # Merge all text
        combined_text = " ".join(text_parts)
        
        # Convert to vector
        embedding = self.get_embedding(combined_text)
        
        # 快取結果
        self.user_embedding = embedding
        return embedding
    
    def create_event_embedding(self, event_id: str) -> np.ndarray:
        """
        Create vector representation for event
        
        Args:
            event_id: Event ID
            
        Returns:
            Event vector representation
        """
        if event_id not in self.events_data:
            raise ValueError(f"Event {event_id} does not exist")
        
        article_model = self.events_data[event_id]
        
        # Merge event title, content and tags
        text_parts = []
        
        # 1. Event title
        text_parts.append(article_model.title)
        
        # 2. Event content
        text_parts.append(article_model.content)
        
        # 3. Event tags
        if article_model.tags:
            text_parts.append(article_model.tags)
        
        # 4. Event category
        if article_model.category:
            text_parts.append(article_model.category.name)
        
        # 5. Author information
        if article_model.author:
            text_parts.append(article_model.author.display_name)
            if article_model.author.department:
                text_parts.append(article_model.author.department)
        
        combined_text = " ".join(text_parts)
        
        # Convert to vector
        embedding = self.get_embedding(combined_text)
        return embedding
    
    def calculate_content_similarity(self, event_id: str) -> float:
        start_time = time.time()
        
        user_embedding = self.create_user_profile_embedding()
        event_embedding = self.create_event_embedding(event_id)
        
        similarity = cosine_similarity([user_embedding], [event_embedding])[0][0]
        
        return float(similarity)
    
    def calculate_tag_similarity(self, event_id: str) -> float:

        user_model = self.user_data
        article_model = self.events_data[event_id]
        
        # Collect user interest tags
        user_tags = set()
        if user_model.interest_articles:
            for article in user_model.interest_articles:
                if article.tags:
                    user_tags.update(article.tags.split(','))
        
        # Collect event tags
        event_tags = set()
        if article_model.tags:
            event_tags.update(article_model.tags.split(','))
        
        if not user_tags or not event_tags:
            return 0.0
        
        intersection = len(user_tags.intersection(event_tags))
        union = len(user_tags.union(event_tags))
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_board_similarity(self, event_id: str) -> float:

        user_model = self.user_data
        article_model = self.events_data[event_id]
        
        # Collect user followed categories
        user_categories = set()
        if user_model.follow_categories:
            user_categories = {cat.name for cat in user_model.follow_categories}
        
        # Event category
        event_category = article_model.category.name if article_model.category else ''
        
        if not user_categories or not event_category:
            return 0.0
        
        return 1.0 if event_category in user_categories else 0.0
    
    def calculate_behavioral_similarity(self, event_id: str) -> float:

        user_model = self.user_data
        
        # Collect user historical behavior text
        behavioral_texts = []
        
        # Browsing history (article title)
        if user_model.article_histories:
            behavioral_texts.extend([article.title for article in user_model.article_histories])
        
        # Search history
        if user_model.search_histories:
            behavioral_texts.extend([history.query for history in user_model.search_histories])
        
        # Joined events
        if user_model.join_events:
            behavioral_texts.extend([event.title for event in user_model.join_events])
        
        if not behavioral_texts:
            return 0.0
        
        # Convert historical behavior to vector
        behavioral_embeddings = []
        for text in behavioral_texts:
            embedding = self.get_embedding(text)
            behavioral_embeddings.append(embedding)
        
        behavioral_embeddings = np.array(behavioral_embeddings)
        
        # Convert event to vector
        event_embedding = self.create_event_embedding(event_id)
        
        # Calculate average similarity with historical behavior
        similarities = cosine_similarity(behavioral_embeddings, [event_embedding])
        avg_similarity = np.mean(similarities)
        
        return float(avg_similarity)
    
    def calculate_search_relevance(self, event_id: str) -> float:

        user_model = self.user_data
        
        # Collect search history
        search_queries = []
        if user_model.search_histories:
            search_queries = [history.query for history in user_model.search_histories]
        
        if not search_queries:
            return 0.0
        
        # Convert search keywords to vector
        search_embeddings = []
        for query in search_queries:
            embedding = self.get_embedding(query)
            search_embeddings.append(embedding)
        
        search_embeddings = np.array(search_embeddings)
        
        # Convert event to vector
        event_embedding = self.create_event_embedding(event_id)
        
        # Calculate average similarity with search keywords
        similarities = cosine_similarity(search_embeddings, [event_embedding])
        avg_similarity = np.mean(similarities)
        
        return float(avg_similarity)
    
    def calculate_comprehensive_score(self, event_id: str) -> Dict[str, float]:

        scores = {}
        
        # Calculate each score
        scores['content_similarity'] = self.calculate_content_similarity(event_id)
        scores['tag_similarity'] = self.calculate_tag_similarity(event_id)
        scores['board_similarity'] = self.calculate_board_similarity(event_id)
        scores['behavioral_similarity'] = self.calculate_behavioral_similarity(event_id)
        scores['search_relevance'] = self.calculate_search_relevance(event_id)
        
        # Calculate weighted total score
        total_score = (
            scores['content_similarity'] * self.weights['interest_tags'] +
            scores['tag_similarity'] * self.weights['interest_tags'] +
            scores['board_similarity'] * self.weights['subscribed_boards'] +
            scores['behavioral_similarity'] * self.weights['browsing_history'] +
            scores['search_relevance'] * self.weights['search_keywords']
        )
        
        scores['total_score'] = total_score
        
        return scores
    
    def recommend_events(self, top_k: int = 5) -> List[str]:
        """
        推薦活動，回傳活動 ID 列表
        
        Args:
            top_k: 回傳前 k 個推薦活動
            
        Returns:
            活動 ID 列表，按推薦分數排序
        """
        if self.user_data is None:
            raise ValueError("使用者資料尚未設定，請先調用 set_user()")
        
        if not self.events_data:
            raise ValueError("沒有可推薦的活動資料")
        
        recommendations = []
        
        for event_id in self.events_data.keys():
            scores = self.calculate_comprehensive_score(event_id)
            recommendations.append((event_id, scores['total_score']))
        
        # Sort by total score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        # 回傳活動 ID 列表
        return [event_id for event_id, _ in recommendations[:top_k]]

def main():
    """Main program - Demonstrate EmbeddingGemma recommendation system usage"""
    
    # 創建推薦系統實例
    recommendation_system = ActivityRecommendationSystemGemma()
    
    # 載入模型
    recommendation_system.load_model()
    
    print("\n=== EmbeddingGemma 活動推薦系統示範 ===\n")
    print("請使用 set_user() 和 add_event_data() 方法設定使用者和活動資料")
    print("範例:")
    print("  recommendation_system.set_user(user_model_instance)")
    print("  recommendation_system.add_event_data('event_1', article_model_instance)")
    print("  event_ids = recommendation_system.recommend_events(top_k=5)")
    print("  # event_ids 會是活動 ID 的列表，例如: ['event_1', 'event_3', 'event_2']")
    
    print("\n推薦系統已準備就緒！")


if __name__ == "__main__":
    main()
