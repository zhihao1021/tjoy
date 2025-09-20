from .embedding import ActivityRecommendationSystemGemma
activity_recommender = ActivityRecommendationSystemGemma()

if not activity_recommender.model:
    print("Initializing global recommendation system model...")
    activity_recommender.load_model()
    print("Global recommendation system model loaded successfully")