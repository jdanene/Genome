
**To do**
- [x] create`apiQueryPatentView.py` to query data from [PatentView](http://www.patentsview.org/api/query-language.html#query_string_format)
  - Template for API Query: https://www.dataquest.io/blog/python-api-tutorial/
  - Template for JSON: https://www.dataquest.io/blog/python-json-tutorial/
- [x] Bag-of-Words and Regex
  - Regex Resources
    - [Regex Cheat Sheet](https://scotch.io/tutorials/an-introduction-to-regex-in-python)
    - [Regex Cheat Sheet](https://stackabuse.com/introduction-to-regular-expressions-in-python/)
  - [Bag of Words](http://www.insightsbot.com/blog/R8fu5/bag-of-words-algorithm-in-python-introduction)
    - http://resources.mpi-inf.mpg.de/d5/teaching/ws11_12/irdm/slides/irdm-3-2.pdf
- [x] Do a comprehensive query on gene editing companies & set up a function to run `BagofWords` on this query. 
  - [brf_sum_text](http://www.patentsview.org/download/)
  - [claim](http://www.patentsview.org/download/) 
  - `govint_raw_statement`: The full government interest statement as reported on a given patent. 
  - `patent_abstract`: Abstract of the patent. (START HERE)
  - `patent_title`: (Most likely useless)
- [x] Clustering: Cluster the BagofWords vectors and other feasture vectors using some clustering algo. 
   - Optimal amount of clusters: http://www.sthda.com/english/wiki/print.php?id=239
   - http://brandonrose.org/clustering
   - https://pythonprogramminglanguage.com/kmeans-elbow-method/
   - Use PCA and K-Means for now but later look into more [complex matrix factorization techniques](https://scikit-learn.org/stable/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html) 
- [ ] Fuzzy match the parameter `assignee_organization` with a stock data set. Merge on fuzzymatch and date
  - Question? When are patents applications usually released? May need to add 1 day to patent data before match to reflect the information being observed by market
  - [How to map cusip to ticker](https://formthirteen.com/blog/how-to-map-cusip-to-ticker). 
  - Or just use crosswalk on CUSIP's from [NBER Cusip to PatentView Map](http://www.nber.org/patents/match.txt)
- [ ] Implement more general ML algos

        
## Bag-of-Words
**Get unique words occuring in all text in our corpus and design a vocabulary.**

The vocabulary will be a vector<int> of size the length(of unique words in corpus). Each document will be described by a vector w/ entiries equal to the number of occurrence of words in vocabulary. 
  
**Problems**
  
    -[ ] The vector can be big and sparse so use scipy-sparse vector to represent (which one?)
    -[ ] text cleaning techniques to reduce vocab
        - Ignoring case
        - Ignoring punctuation
        - Ignoring frequent words that don’t contain much information, called stop words, like “a,” “of,” etc.
        - Stemming: words to their stem (e.g. “play” from “playing”) using stemming algorithms
        - Fixing misspelled words.
**Enhancement**

Generalize to bag-of-bigrams model.

`*An N-gram is an N-token sequence of words: a 2-gram (more commonly called a bigram) is a two-word sequence of words like “please turn”, “turn your”, or “your homework”, and a 3-gram (more commonly called a trigram) is a three-word sequence of words like “please turn your”, or “turn your homework”... n-gram*`

**Notes**

    - Take a document as the input.
    - Read the document line by line
    - Tokenize the line (put into a vector)
    - Process woords. 
    - https://en.wikipedia.org/wiki/Tf%E2%80%93idf
    - https://s3.amazonaws.com/assets.datacamp.com/production/course_5064/slides/chapter2.pdf
    - https://medium.com/@aakashtandel/the-basics-of-natural-language-programming-a-big-bag-of-words-2f2ac06638ea
** Patent Background **
- http://www.bpmlegal.com/howtopat5.html
## Break throughs before Gene Therapy
- Stem cell therapy (1970s)
- Immunotherapy (1970s)

## 9-Types of Molecular Scissor (probably more) 
- Cas9 (RNA)
- TALE (Protein) 
- Group II intron (RNA)
- Meganuclease (Protein) 
- Recombinase (Protien) 
- TtAgo (DNA) 
- </sub>&lambda;<sub>-beta/exo MAGE (DNA)
- RecACage (DNA)
- ZnF (Protein) 
## 4-Main Types
  - [meganucleases](https://en.wikipedia.org/wiki/Meganucleasem)
  - zinc finger nucleases  [ZFNs](https://en.wikipedia.org/wiki/Zinc_finger_nuclease)
  - Transcription activator-like effector-based nucleases  [TALEN](https://en.wikipedia.org/wiki/Transcription_activator-like_effector_nucleasem)
  - Clustered regularly interspaced short palindromic repeats [Cas9/Crispr](https://www.google.com)
## Websites
- Allows to find CPC Patent code by keyword: https://worldwide.espacenet.com/classification?locale=en_EP#!/CPC=C12N15/00
- Data
    - Query Search: http://www.patentsview.org/query/
    - API: http://www.patentsview.org/api/doc.html
    - http://www.patentsview.org/querydev/query/data_dictionary.html
    - https://www.upcounsel.com/patent-classification-search
    - https://www.upcounsel.com/patent-search-firm


