from elasticsearch import Elasticsearch

import json
# Realized that not all documents have to be clicked, need to incorporate that 
# in future judgement lists. Currently every document is a clicked document.

# Next step: get scores from explain, get url depth and body length
# Lost step: need to figure out how storing features work (_ltr)
# need to get scores from features not manual like below
es = Elasticsearch(['http://localhost:9200/'], verify_certs=True)

body = {
  "query": {
    "match": {
      "title": "New Employment Cost Index release: continued very low compensation growth | The Conference Board"
    }
  }
}

res = es.explain("tcb-20210826", 3842168, body, doc_type="_doc")

print(res)


