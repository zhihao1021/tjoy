
import json
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from turftopic.vectorizers.chinese import ChineseCountVectorizer
from mockup_data import articles

def analyze_topics():
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

        output_topics.append({
            "rank": index,
            "count": row['Count'],
            "name": row['Name'],
            "representation": representation
        })

    # Write to JSON
    with open('topics.json', 'w', encoding='utf-8') as f:
        json.dump(output_topics, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    analyze_topics()
