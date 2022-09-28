import os
from jParsers import judgmentsFromFile, judgmentsByQid, duplicateJudgmentsByWeight

# training = ''
# testing = ''
FULL = 'judgements/cleaned_judgements_new.txt' # <-- INSERT NAME OF FINAL JUDGEMENT TEXT FILE WITH FEATURES

def trainModel(trainingData, modelOutput, whichModel=8):
    # java -jar RankLib-2.6.jar  -metric2t NDCG@4 -ranker 6 -kcv -train osc_judgments_wfeatures_train.txt -test osc_judgments_wfeatures_test.txt -save model.txt

    # Ranking Algorithms: 
    #   0: MART (gradient boosted regression tree)
    #   1: RankNet
    #   2: RankBoost
    #   3: AdaRank
    #   4: Coordinate Ascent
    #   6: LambdaMART
    #   7: ListNet
    #   8: Random Forests

    # For random forest
    # - bags of LambdaMART models
    #  - each is trained against a proportion of the training data (-srate)
    #  - each is trained using a subset of the features (-frate)
    #  - each can be either a MART or LambdaMART model (-rtype 6 lambda mart)
    cmd = "java -jar RankyMcRankFace-0.2.0.jar -metric2t NDCG@10 -bag 10 -srate 0.6 -frate 0.6 -rtype 6 -shrinkage 0.1 -tree 80 -ranker %s -train %s -save %s" % (whichModel, trainingData, modelOutput)
    print("*********************************************************************")
    print("*********************************************************************")
    print("Running %s" % cmd)
    os.system(cmd)
    pass

def partitionJudgments(judgments, testProportion=0.1):
    testJudgments = {}
    trainJudgments = {}
    from random import random
    for qid, judgment in judgments.items(): # judgements here is a dictionary
        draw = random()
        if draw <= testProportion:
            testJudgments[qid] = judgment
        else:
            trainJudgments[qid] = judgment

    return (trainJudgments, testJudgments)


def saveModel(esHost, scriptName, featureSet, modelFname):
    """ Save the ranklib model in Elasticsearch """
    import requests
    import json
    from urllib.parse import urljoin
    modelPayload = {
        "model": {
            "name": scriptName,
            "model": {
                "type": "model/ranklib",
                "definition": {
                }
            }
        }
    }

    # Force the model cache to rebuild
    path = "_ltr/_clearcache"
    headers = {'content-type': 'application/json'}
    fullPath = urljoin(esHost, path)
    print("POST %s" % fullPath)
    print(esHost, fullPath)
    resp = requests.post(fullPath, headers=headers)
    if (resp.status_code >= 300):
        print(resp.text)

    with open(modelFname) as modelFile:
        modelContent = modelFile.read()
        path = "_ltr/_featureset/%s/_createmodel" % featureSet
        fullPath = urljoin(esHost, path)
        modelPayload['model']['model']['definition'] = modelContent
        print("POST %s" % fullPath)
        resp = requests.post(fullPath, json.dumps(modelPayload), headers=headers)
        print(resp.status_code)
        if (resp.status_code >= 300):
            print(resp.text)

# parse judgements
# fullJudgements = judgmentsByQid(judgmentsFromFile(filename=FULL))
# fullJudgements = duplicateJudgmentsByWeight(fullJudgements)
# trainJudgements, testJudgements = partitionJudgments(fullJudgements, testProportion=0.0)


trainModel(FULL, 'models/model_ltr_v2.txt', 8) # <-- INSERT NAME OF LTR MODEL
saveModel(esHost='http://elk-latest:9200', scriptName="randomforest_8_v2", featureSet='features_w_age', modelFname='models/model_ltr_v2.txt') # <-- INSERT NAME OF LTR MODEL