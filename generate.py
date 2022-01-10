from elasticsearch import Elasticsearch

import json
# Realized that not all documents have to be clicked, need to incorporate that 
# in future judgement lists. Currently every document is a clicked document.

# Next step: get scores from explain, get url depth and body length
# Lost step: need to figure out how storing features work (_ltr)
# need to get scores from features not manual like below
es = Elasticsearch(['http://localhost:9200/'], verify_certs=True)

c_file_r = open('clicks.json', 'r')
c_data = json.load(c_file_r)
c_file_r.close()

for click in c_data:
    clicked_url = click["url_raw"]
    if clicked_url is not None:
        search_params = {
        "query":{
            "match": {
                "url_raw": clicked_url
                }
            }
        }
        # generates document id
        res = es.search(index="tcb-20210826", body=search_params)
        if res['hits']['hits'] == []:
            click["doc_id"] = None

            continue
        res_id = res['hits']['hits'][0]['_id']
        # res_title = res['hits']['hits'][0]['_source']['title']
        # res_description = res['hits']['hits'][0]['_source']['description']
        # fill in the data
        click["doc_id"] = res_id

    else:
        click["doc_id"] = None

c_file_w = open("clicks.json", "w")
json.dump(c_data, c_file_w)
c_file_w.close()

# create judgement list from the new jsons with no features
j_txt_nof = open("clean_judgements_nof.txt", "w+")

c_file_r = open('clicks.json', 'r')
c_data = json.load(c_file_r)
c_file_r.close()

for i in c_data:
    if (i["c_id"] is not None):
        score = i["score"]
        qid = i["d_id"]
        doc_id = i["doc_id"]
        s_term = i["s_term"]
        j_txt_nof.write("{0} qid:{1} # {2}   {3}\n".format(score, qid, doc_id, s_term))
    else:
        pass

j_txt_nof.close()



