
**To do **
- [x] create`apiQueryPatentView.py` to query data from [PatentView](http://www.patentsview.org/api/query-language.html#query_string_format)
  - DoneTemplate for API Query: https://www.dataquest.io/blog/python-api-tutorial/
  - Template for JSON: https://www.dataquest.io/blog/python-json-tutorial/
- [ ] Do a comprehensive query on gene editing companies and create bag-of-words histogram
  - Problem 1: [brf_sum_text](http://www.patentsview.org/download/) is way too large computer. Tried loading in chunks but the encoding is mysterious so all of it is gibberish. 
    - [X] Reach out to contact@patentsview.org to find out encoding. *No REPOSNSE!*
    - [ ] Open up cluster account at NU? 
  - Problem 2: [claim](http://www.patentsview.org/download/) probably too large, can't be addressed until address problem 1. 
  - Only text data accessible as of now
    - `govint_raw_statement`: The full government interest statement as reported on a given patent. 
    - `patent_abstract`: Abstract of the patent. (START HERE)
    - `patent_title`: (Most likely useless)
        


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


