from gensim.models.word2vec import Word2Vec
import pandas as pd
from pathlib import Path

directory = Path('./erudit')
number_words = 1000


def create_doc_dict_count(n_rows=100):
    path = Path('{}/doc_parse.csv'.format(directory))
    df = pd.read_csv(path, encoding='utf-8', sep=';', nrows=n_rows,
                     usecols=['author', 'title', 'titrerev', 'annee', 'idproprio', 'lemma'])
    df = df[df['lemma'].notna()]
    df.reset_index(inplace=True)
    corpus = df.lemma

    text = [s.split(' ') for s in corpus]

    model = Word2Vec(sentences=text,
                     # sg=1,
                     # vector_size=300,
                     # window=10,
                     min_count=2,
                     workers=11,
                     max_vocab_size=20000,
                     epochs=5
                     )

    model.build_vocab(text)
    model.train(corpus_iterable=text,
                total_examples=model.corpus_count, epochs=model.epochs)
    wv_model = model.wv

    wrd,cnt = [],[]
    for index, word in enumerate(wv_model.index_to_key):
        if index==number_words:
            break
        wrd.append(word)
        cnt.append(wv_model.get_vecattr(word,'count'))
        
    word_counts = pd.DataFrame(data=[pd.Series(wrd,name='word'),pd.Series(cnt,name='count')]).T
    path = Path('{}/doc_countvectors/doc_dict_counts.csv'.format(directory))
    word_counts.to_csv(path,encoding='utf-8',sep=';')