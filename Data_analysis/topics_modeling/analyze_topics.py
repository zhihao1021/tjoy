import json
import os
import openai
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from turftopic.vectorizers.chinese import ChineseCountVectorizer
from mockup_data import articles

def get_openai_summary(keywords, api_key):
    """
    Uses OpenAI to summarize a list of keywords into three words.
    """
    openai.api_key = api_key
    prompt = f"Please summarize the following list of Chinese keywords into exactly three general and representative Chinese words. The keywords are: {', '.join(keywords)}. Please provide only the three words, separated by '、'."

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in summarizing topics into keywords."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.2,
        )
        summary = response.choices[0].message.content.strip()
        return summary.split('、')
    except Exception as e:
        print(f"An error occurred with OpenAI API: {e}")
        return keywords # Fallback to original keywords

def analyze_topics():
    # Get OpenAI API Key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Warning: OPENAI_API_KEY environment variable not set. Using default representation.")

    # Pre-calculate embeddings
    embedding_model = SentenceTransformer("uer/sbert-base-chinese-nli")
    embeddings = embedding_model.encode(articles, show_progress_bar=True)

    # UMAP for dimensionality reduction
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)

    # HDBSCAN for clustering
    hdbscan_model = HDBSCAN(min_cluster_size=5, metric='euclidean', cluster_selection_method='eom', prediction_data=True)

    # Vectorizer for Chinese text
    vectorizer_model = ChineseCountVectorizer(stop_words="chinese")

    # BERTopic model
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        language="chinese",
        verbose=True
    )

    topics, probs = topic_model.fit_transform(articles, embeddings)
    topic_info = topic_model.get_topic_info()

    # Format output
    output_topics = []
    for index, row in topic_info.iterrows():
        topic_id = row['Topic']
        if topic_id == -1:
            continue
        
        representation = [word for word, score in topic_model.get_topic(topic_id)]

        if openai_api_key:
            final_representation = get_openai_summary(representation, openai_api_key)
        else:
            final_representation = representation

        output_topics.append({
            "rank": index,
            "count": row['Count'],
            "name": row['Name'],
            "representation": final_representation
        })

    # Write to JSON
    with open('topics.json', 'w', encoding='utf-8') as f:
        json.dump(output_topics, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    analyze_topics()