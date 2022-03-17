from elasticsearch import Elasticsearch

import json


es = Elasticsearch(['http://localhost:9200/'], verify_certs=True)

j_txt_nof = open("uncleaned_judgements.txt", "w+")

c_file_r = open('clicks.json', 'r') # <-- INSERT CLICKS DATA JSON
c_data = json.load(c_file_r)
c_file_r.close()

# Use featureset to generate the feature values inside the judgement text file
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
                        "featureset": "testing_features_w_scores",
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
        res = es.search(index="tcb1", body=query) # <-- INSERT INDEX NAME

        try:
            title_score = res['hits']['hits'][0]['fields']['_ltrlog'][0]['log_entry1'][0]['value'] # 3
        except KeyError:
            title_score = 0.0
        try:
            description_score = res['hits']['hits'][0]['fields']['_ltrlog'][0]['log_entry1'][1]['value'] # 4
        except KeyError:
            description_score = 0.0
        try:
            url_depth_score = res['hits']['hits'][0]['fields']['_ltrlog'][0]['log_entry1'][2]['value'] # 5
        except KeyError:
            url_depth_score = 0.0
        j_txt_nof.write("{0} qid:{1} 1:{2} 2:{3} 3:{4} # {5}   {6}\n".format(score, qid, title_score, description_score, url_depth_score, doc_id, s_term))
    else:
        pass

j_txt_nof.close()

with open("uncleaned_judgements.txt", "r") as f:
    unique_lines = list(dict.fromkeys(f.readlines()))
with open("cleaned_judgements.txt", "w") as g: # <-- INSERT NAME OF FINAL JUDGEMENT TEXT FILE WITH FEATURES
    g.writelines(unique_lines)
