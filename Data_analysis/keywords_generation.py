import os
import openai
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
from bertopic.representation import OpenAI
from fake_data import articles

# This script performs topic modeling on Chinese text data using BERTopic,
# following best practices and using OpenAI for topic representation.

# 1. Data
# The data is a list of Chinese documents related to TSMC.
docs = articles

# 2. Pre-calculate Embeddings
# We use a multilingual model suitable for Chinese text.
print("Embedding documents...")
embedding_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
embeddings = embedding_model.encode(docs, show_progress_bar=True)

# 3. UMAP for dimensionality reduction
# Using a fixed random_state for reproducibility.
umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)

# 4. HDBSCAN for clustering
# min_cluster_size is adjusted for the small dataset size to generate a reasonable number of topics.
hdbscan_model = HDBSCAN(min_cluster_size=3, metric='euclidean', cluster_selection_method='eom', prediction_data=True)

# 5. CountVectorizer for default c-TF-IDF representation
vectorizer_model = CountVectorizer(ngram_range=(1, 2))

# 6. OpenAI for Topic Representation
# The user must set the OPENAI_API_KEY environment variable.
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY environment variable not set. OpenAI representation will not work.")
    print("Please set it and re-run the script to get OpenAI-based topic labels.")
    representation_model = None
else:
    client = openai.OpenAI(api_key=api_key)
    # Prompt for generating topic labels in Chinese.
    prompt = '''
I have a topic that contains the following documents:
[DOCUMENTS]
The topic is described by the following keywords: [KEYWORDS]

Based on the information above, extract a short but highly descriptive topic label of at most 5 words. Make sure it is in Chinese and in the following format:
topic: <topic label>
'''
    openai_model = OpenAI(client, model="gpt-3.5-turbo", exponential_backoff=True, chat=True, prompt=prompt)
    representation_model = {"OpenAI": openai_model}


# 7. Initialize and train BERTopic model
print("Training BERTopic model...")
topic_model = BERTopic(
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    vectorizer_model=vectorizer_model,
    representation_model=representation_model,
    top_n_words=10,
    verbose=True,
    language="multilingual" # Specify multilingual for better default processing
)

topics, probs = topic_model.fit_transform(docs, embeddings)

# 8. Print and view topics
print("BERTopic model training complete.")
print("Topic Info:")
print(topic_model.get_topic_info())

# Set custom labels from OpenAI representation
if representation_model and "OpenAI" in topic_model.topic_aspects_:
    print("\nSetting custom topic labels from OpenAI...")
    # Create custom labels
    chatgpt_labels = {topic: " | ".join(list(zip(*values))[0]) for topic, values in topic_model.topic_aspects_["OpenAI"].items()}
    # Manually set outlier topic label
    chatgpt_labels[-1] = "Outliers"
    topic_model.set_topic_labels(chatgpt_labels)
    print("Topic Info with custom OpenAI labels:")
    print(topic_model.get_topic_info())
