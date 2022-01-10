FROM python:3.6

RUN pip3 install pipenv

ENV PROJECT_DIR ~/elasticsearch-ltr-demo/deploy/judgements

WORKDIR ${PROJECT_DIR}

COPY ./Pipfile ./Pipfile.lock ${PROJECT_DIR}

RUN pipenv install --system --deploy

CMD ["python3", "generate.py"]
