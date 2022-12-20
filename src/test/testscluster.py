from sentence_transformers import SentenceTransformer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd 
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


conn = sqlite3.connect("./database.sqlite")
keyword = 'indonesia'
query = f"""SELECT title FROM scrapping_data where title like '%{keyword}%'"""
df = pd.read_sql_query(query, conn)

tempArr = []
for line in df['title']:
    tempArr.append(line.lower())

# print(tempArr)
# print(len(tempArr))
# print(type(tempArr))
tempArr = tempArr[0:1000]

model = SentenceTransformer('distilbert-base-multilingual-cased')
corpus_embeddings = model.encode(tempArr)

if len(tempArr) < 5:
    num = len(tempArr)
else:
    num = 5
num_clusters = num
clustering_model = KMeans(n_clusters=num_clusters,init="k-means++",max_iter=100,n_init=1)
clustering_model.fit(corpus_embeddings)
cluster_assignment = clustering_model.labels_

clustered_sentences = [[] for i in range(num_clusters)]
for sentence_id, cluster_id in enumerate(cluster_assignment):
    clustered_sentences[cluster_id].append(tempArr[sentence_id])

for i, cluster in enumerate(clustered_sentences):
    print("Cluster ", i+1)
    print(cluster)
    print("")

def word_cloud(pred_df,label):
    wc = ' '.join([text for text in pred_df['corpus'][pred_df['cluster'] == label]])
    wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(wc)
    fig7 = plt.figure(figsize=(10, 7))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.savefig('./assets/images/clustering.png')

cluster_df = pd.DataFrame(tempArr, columns = ['corpus'])
cluster_df['cluster'] = cluster_assignment
cluster_df.head()

print(cluster_df.head())

word_cloud(cluster_df,0)

# df.columns = ['sentiment']
# df.shape
# df.head()

# corpus = list(df['sentiment'])
# corpus = corpus[0:1000]

# embedder = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')
# embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# corpus_embeddings = embedder.encode(corpus)

# tempArr = []
# for line in df['title']:
#     tempArr.append(line)

# # tempArr = tempArr[0:1000]

# vectorizer = TfidfVectorizer(stop_words='english',decode_error="strict")
# X = vectorizer.fit_transform(tempArr)

# true_k = 5
# model = KMeans(n_clusters=true_k, n_init=1)
# model.fit(X)
# cluster_assignment = model.labels_

# # print(cluster_assignment)

# clustered_sentences = [[] for i in range(true_k)]
# for sentence_id, cluster_id in enumerate(cluster_assignment):
#     clustered_sentences[cluster_id].append(tempArr[sentence_id])

# for i, cluster in enumerate(clustered_sentences):
#     print("Cluster ", i+1)
#     print(cluster)
#     print("")

# def word_cloud(pred_df,label):
#     wc = ' '.join([text for text in pred_df['corpus'][pred_df['cluster'] == label]])
#     wordcloud = WordCloud(width=800, height=500,
#     random_state=21, max_font_size=110).generate(wc)
#     fig7 = plt.figure(figsize=(10, 7))
#     plt.imshow(wordcloud, interpolation="bilinear")
#     plt.axis('off')
#     plt.savefig('clustering.png')

# cluster_df = pd.DataFrame(tempArr, columns = ['corpus'])
# cluster_df['cluster'] = cluster_assignment
# cluster_df.head()

# # print(cluster_df.head())

# word_cloud(cluster_df,0)