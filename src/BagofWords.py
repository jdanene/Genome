import re, string
from nltk.util import ngrams
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import csr_matrix
from scipy.sparse import vstack
from nltk import pos_tag
from string import digits


class BagOfWords:
    """ 
    This is a class to get n-gram BagOfWords model. 

    Definitions:
        text-document: Is a string of sentences, phrases, words... basically this thing represent textual data. 
        
        corpus: A corpus is  a [list-of text-document]

        N-grams: is a contiguous sequence of n items from a given text-document

        BagOfWords model: an orderless document representation—only that counts (or encodes) the words that matter in a corpus
        
        N-grams BagOfWords model: parse corpus' text-documents into a set of unique N-grams units called the vocabulary of the corpus,
                                  and then for each of the corpus' text-document record the frequency N-grams units in [text-document] and [vocabulary] into a matrix. 

        Tfidf: Is a method to assign weights to a n-gram unit, `t`, within a text-document, d, in our corpus. 
            - highest when `t` occurs many times within a small number of documents (thus lending high discriminating power to those documents);
            - lower when the `t` occurs fewer times in a document, or occurs in many documents (thus offering a less pronounced relevance signal);
            - lowest when the term occurs in virtually all documents
        
        stemming: a preprocessing step where related words with a common stem or root are reduced to and then represented by their common root. 
        (e.g. stem("learn") = stem("learning") = stem("learned") = stem("learner") = "learn")

    Attributes: 
        reduce_inflec (function): The stemming function that reduces inflection in a given word (e.g living -> livi). Used in preprocessing
        
        n (int): represents contiguous sequences of `n`-items in a given document. 
        
        translator (str): regex patten so we can get rid of puncutuation (eg he's -> he). Used in preprocessing
        
        stop_words ({set-of string}): Words used frequently in a sentence that we want to ignore. Used in preprocessing
        
        vocab ({list-of string}): All the unique N-grams units that appear in a corpus of textual documents
        
        pos_method (bool): Whether to do part of speech (POS) contextual tagging instead of N-Gram stemming. True -> POS is implemented. 
        
        numbers (bool) : Indicator if include numbers in parsed text or not

        X (scipy sparse csr_matrix<np.int>): Matrix of counts of number of occurrences of words in vocab for the corpus. Rows represent a specfic
        textual document w/in the corpus. 
        X_norm_l1 (scipy sparse csr_matrix<np.float>): Matrix in which the rows in `X` are normalized by the L1 norm of the row.
        X_norm_l2 (scipy sparse csr_matrix<np.float>): Matrix in which the rows in `X` are normalized by the L2 (Euclidian) norm of the row.
        X_idf (scipy sparse csr_matrix<np.float>): Matrix that holds Tfidf weights 
        X_idf_subl (scipy sparse csr_matrix<np.float>): Matrix that holds variation of Tdidf weights (see https://nlp.stanford.edu/IR-book/html/htmledition/sublinear-tf-scaling-1.html)
    """
    def __init__(self, n =1, pos_method = False, numbers = False):
        #The stemmer. There are multiple put the porter stemmer seems to be the best. 
        self.reduce_inflec = PorterStemmer()
        
        #N-gram, the n-word sequence of words to process and also form our vocabulary. 
        self.n = n
        #Reduces the puncuation of a word. 
        if numbers==True:
            self.translator = str.maketrans('', '', string.punctuation+digits)
        else:
            self.translator = str.maketrans('', '', string.punctuation)

        #Ignore words that are used frequently in sentences and have little meaning. 
        self.stop_words= set(stopwords.words('english'))

        #Vocabulary of corpus
        self.vocab = set("")

        #Part of speech context tagger?
        self.pos_method = pos_method

        # Various matrices that encode relevant information of corpus
        self.X= csr_matrix((0, 0), dtype=int)
        self.X_norm_l1 = csr_matrix((0, 0), dtype=float)
        self.X_norm_l2 = csr_matrix((0, 0), dtype=float)
        self.X_idf = csr_matrix((0, 0), dtype=float)
        self.X_idf_subl = csr_matrix((0, 0), dtype=float)

        #Boolean to tell if remove digits or not
        self.numbers = numbers


    def extract_ngrams(self, doc_string):
        """ 
        Processes a document by stemming the words, removing punctuation, reducing the case to lower, 
        filtering out stop words, and finally grouping consecutive words into size `self.n` n-gram pairs. 
        
        Input: 
        doc_string (string): Raw string document
      
        Returns: 
        [list-of string]: processed and tokenized string document.
        
        Examples:  
        >> extract_words('String with "punctuation" inside of it! Does this work? I hope so.')
            ['string','punctuat', 'insid','doe','work','i','hope']

        """

        #Removes puncuation from word 
        words = doc_string.translate(self.translator)

        #Tokenize words into a vector
        words = words.split()
        clean_and_purify = lambda w: ''.join([i for i in self.reduce_inflec.stem(w.lower()) if i.isalpha()])
        
        #Removes `ignore_words` from vector,reduces the case to lower, and stems words
        tokens = [clean_and_purify(w) for w in words if w not in self.stop_words]
        tokens = ' '.join(tokens).split()

        if self.pos_method == False:
            # Concatentate the tokens into ngrams and return
            _ngrams = ngrams(x, 1)
            return [" ".join(ng) for ng in _ngrams]

        else:
            return pos_tag(tokens)

    def get_vocabulary(self, corpus):
        '''
        Gets the vocabulary given a list of documents otherwise called a corpus.a

        Input:
        corpus ([list-of strings]): List of raw strings documents to process, 
        
        Returns:
        self.vocabulary: Set of all the processed strings in the `corpus`

        '''
        vocabulary = set()
        for doc_string in corpus:
            w = set(self.extract_ngrams(doc_string))
            vocabulary = vocabulary.union(w)
            
        vocabulary = sorted(list(set(vocabulary)))
        return vocabulary

    def set_varient_matrices(self):
        '''
        If the dataset is very large this is useful. Have a base BagofWords class and keep updating on chunks call when
        finished updating X. Or call immediately doesn't matter
        '''

        #Normalized arrays
        self.X_norm_l1 = normalize(self.X, norm='l1', axis=1)
        self.X_norm_l2 = normalize(self.X, norm='l2', axis=1)

        #TF-IDF arrays
        transformer = TfidfTransformer()
        transformer.smooth_idf = False
        self.X_tfidf = transformer.fit_transform(self.X)
        transformer.sublinear_tf = True
        self. X_tfidf_subl = transformer.fit_transform(self.X)

    def update_X_matrix(self,newX):
        '''
        If the dataset is very large this is useful. Have a base BagofWords class and keep updating on chunks
        '''
        self.X = vstack([self.X,newX])

    def update_vocab(self,new_corpus):
        '''
        If the dataset is very large this is useful. Have a base BagofWords class and keep updating on chunks
        '''
        self.vocab = self.vocab.union(self.get_vocabulary(new_corpus))

    def get_bagofwords(self, corpus):
        '''
        Gets the matrix representation of all textual documents in corpus. 

        Parameters:
            self.vocab({set-of strings}): Vocabulary of corpus
            self.n (int): Length of N-gram units in corpus. 
            extract_ngrams(string -> [list-of string]): Analyzer function which processes/cleans textual document into token
        
        Returns:
            self.X (scipy sparse matrix<np.int>)  
            self.X_norm_l1(scipy sparse matrix<np.float>) 
            self.X_norm_l2(scipy sparse matrix<np.float>)
            self.X_tfidf(scipy sparse matrix<np.float>)
            self.X_tfidf_subl(scipy sparse matrix<np.float>)

        Note: See class doc-string for function return definitions. 
        '''
        if self.vocab == set(""):
            self.vocab = self.get_vocabulary(corpus)

        vectorizer = CountVectorizer(vocabulary = self.vocab, 
                                    analyzer = self.extract_ngrams)
        self.X = vectorizer.fit_transform(corpus)
        pass





#senrtences = ["Machine learning is great",
        # "Natural Language Processing is a complex field",
        # "Natural Language Processing is used in machine learning",
        # 'String with "punctuation" inside of it! Does this work? I hope so.']
#bow = BagOfWords(n=2)
#bow.get_bagofwords(senrtences)
#xx = bow.X

#bow.update_X_matrix(xx)
#bow.get_varient_matrices()




