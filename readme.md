# LTR Documentation and Notes of APIs

```bash
git clone https://github.com/anoman00/elk-ltr.git
cd elk-ltr
pipenv shell
pipenv install
wget https://repo1.maven.org/maven2/com/o19s/RankyMcRankFace/0.2.0/RankyMcRankFace-0.2.0.jar
```

The *generate.py* script requires a *clicks.json* file to run. It attaches a document ID to the JSON from the search index to each data point in the json file. The json file is generated using the following SQL queries. The final SQL query result is imported into the json file. The SQL queries were run in 11-156

- The create table query for *scoretable*:
    
    ```sql
    CREATE TABLE "public".scoretable AS
    SELECT
    	C_id,
    	CASE WHEN click_time IS NOT NULL
    		AND(bounce_seconds IS NULL
    			OR bounce_seconds > 20) THEN
    		TRUE
    	ELSE
    		FALSE
    	END AS successes_flag,
    	click_time,
    	bounce_seconds,
    	S_id,
    	rank,
    	url AS url_clicked,
    	browser_time,
    	fingerprint,
    	S_term,
    	DENSE_RANK() OVER (ORDER BY S_term),
    	true_count,
    	term_count,
    	success_rate,
    	CASE WHEN success_rate >= 70 THEN
    		4
    	WHEN (70 > success_rate
    		AND success_rate >= 50) THEN
    		3
    	WHEN (50 > success_rate
    		AND success_rate >= 40) THEN
    		2
    	WHEN (40 > success_rate
    		AND success_rate >= 20) THEN
    		1
    		-- 	WHEN(bounce_seconds < 20
    		-- 		AND "rank" < 6) THEN
    		-- 		1
    	ELSE
    		0
    	END AS score
    FROM (
    	SELECT
    		C.id AS C_id,
    		S.id AS S_id,
    		LOWER( TRIM( REPLACE( S.term, '+', ' '))) AS S_term,
    		*
    	FROM
    		"clicks" C
    		INNER JOIN "results" R ON C.result_id = R.id
    		FULL OUTER JOIN "session" S ON R.session_id = S.id
    		FULL OUTER JOIN "successrate" SR ON S.term = SR.term
    	WHERE
    		S.browser_time >= '01-25-2021'
    		AND S.browser_time < '02-25-2022'
    		AND S.api_account_id = 101) A WHERE A.C_id is NOT NULL;
    ```
    
- The create table query for *scoreaggtable*:
    
    ```sql
    CREATE TABLE "public".scoreaggtable AS
    SELECT
    	dense_rank,
    	s_term,
    	COUNT(DISTINCT score)
    FROM
    	"public".scoretable
    GROUP BY
    	s_term, dense_rank;
    ```
    
- The final query to create *clicks.json* file that uses scoretable and scoreaggtable. As well as only collecting where click count is larger than 2:
    
    ```sql
    SELECT
    	A.*,
    	DENSE_RANK() OVER (ORDER BY A.s_term) as d_id,
    	REPLACE( A.url_clicked, 'https://conference-board.org', 'https://www.conference-board.org') AS url_raw,
    	B.count AS score_type_count
    FROM
    	scoretable A
    	FULL OUTER JOIN scoreaggtable B ON A. "dense_rank" = B. "dense_rank"
    WHERE
    	B.count >= 3;
    ```
    
- Copy the json file into the repo folder. If it is necessary to delete the json file, it is best to delete via the following command. Deleting it through IDE may cause severe lags:
    
    ```bash
    rm clicks.json
    ```
    

```bash
#. attaches document ID from index onto each data point in clicks.json
  #. I marked all lines with a comment "# <-- INSERT CLICKS DATA JSON" 
  #. where the JSON file would be inputted.

  #. I added a comment "# <-- INSERT INDEX NAME"  where you can change the 
  #. index name, currently it is tcb1
python3 generate.py

#. creates a judgement list along with feature values.
  #. I marked all lines with a comment "# <-- INSERT CLICKS DATA JSON" 
  #. where the JSON file would be inputted.

  #. I added a comment "# <-- INSERT INDEX NAME"  where you can change the 
  #. index name, currently it is tcb1

  #. I marked the line with a comment "# <-- INSERT NAME OF FINAL JUDGEMENT TEXT FILE WITH FEATURES" 
  #. where the judgement list file name would be inputted, currently it 
  #. is named cleaned_judgements.txt
python3 addFeatures.py

#. trains the model using the cleaned judgement list that was generated in
#. the last step.
  #. I marked the line with a comment "# <-- INSERT NAME OF FINAL JUDGEMENT TEXT FILE WITH FEATURES" 
  #. where the judgement list file name would be inputted, currently it 
  #. is named cleaned_judgements.txt

  #. I marked the last two lines with "# <-- INSERT NAME OF LTR MODEL FILE" to 
  #. show where to add the model file name. This model file name is what will be used 
  #. in the final ES query to apply LTR modeling. Currently it is named
  #. model_ltr.txt
python3 train.py
```

Note: You can create a folder named dump inside the repo to keep all unnecessary text or json files in. The dump folder and all its content is gitignored.

Model file name is not the same as the model name that ES uses to call in the rescore function. The model name is usually the scriptName, which is defined in the last line of code in train.py. For example, below the model name is **test_randomforest_8.**

```python
saveModel(esHost='http://localhost:9200', **scriptName="test_randomforest_8"**, featureSet='testing_features_w_scores', modelFname='model_ltr.txt') # <-- INSERT NAME OF LTR MODEL FILE AND SCRIPTNAME
```

Below is a snippet of where the model comes in play in the querybuilder:
```python
if solorank:
        rescore = {
            "window_size": 1000,
            'query': {
                "score_mode": "total",
                'rescore_query': {
                    'sltr': {
                        'params': {
                            'keywords': q
                        },
                        'model': '<MODEL NAME>' # <-- YOU WOULD INSERT test_randomforest_8
                    }
                },
                "query_weight" : 1,
                  "rescore_query_weight" : 1
            }
        }
        body['rescore'] = rescore
```