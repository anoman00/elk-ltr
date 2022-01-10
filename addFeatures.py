from elasticsearch import Elasticsearch

import json


es = Elasticsearch(['http://localhost:9200/'], verify_certs=True)

j_txt_nof = open("clean_judgements_wf_zeros.txt", "w+")

c_file_r = open('clicks.json', 'r')
c_data = json.load(c_file_r)
c_file_r.close()

for i in c_data:

    if (i["c_id"] is not None) and (i["doc_id"] is not None): # c_id is the click ID
        score = i["score"] # 0
        qid = i["d_id"] # 1
        doc_id = i["doc_id"] # 4
        s_term = i["s_term"] # 5
        print(qid, doc_id)
        query = {
            "_source": {
                "includes": [
                "title",
                "description"
                ]
            },
            "query": {
                "bool": {
                "filter": [
                    {
                    "terms": {
                        "_id": [str(doc_id)]
                    }
                    },
                    {
                    "sltr": {
                        "_name": "logged_featureset",
                        "featureset": "testing_features",
                        "params": {
                        "keywords": s_term # keyword
                        }
                    }
                    }
                ]
                }
            },
            "ext": {
                "ltr_log": {
                "log_specs": {
                    "name": "log_entry1",
                    "named_query": "logged_featureset"
                }
                }
            }
        }
        res = es.search(index="tcb-20210826", body=query)

        try:
            title_score = res['hits']['hits'][0]['fields']['_ltrlog'][0]['log_entry1'][0]['value'] # 3
        except KeyError:
            title_score = 0.0
        try:
            description_score = res['hits']['hits'][0]['fields']['_ltrlog'][0]['log_entry1'][1]['value'] # 4
        except KeyError:
            description_score = 0.0
        j_txt_nof.write("{0} qid:{1} 1:{2} 2:{3} # {4}   {5}\n".format(score, qid, title_score, description_score, doc_id, s_term))
    else:
        pass

j_txt_nof.close()

with open("clean_judgements_wf_zeros.txt", "r") as f:
    unique_lines = list(dict.fromkeys(f.readlines()))
    # unique_lines = set(f.readlines())
with open("test1.txt", "w") as g:
    g.writelines(unique_lines)
