FROM python:3.9-slim
# FROM continuumio/miniconda

WORKDIR /app

COPY ["requirements.txt", "environment.yml", "./"]

# RUN conda env create -f environment.yml
RUN pip install -r requirements.txt
# RUN pipenv install --system --deploy
# SHELL ["conda", "run", "-n", "ml_capstone", "/bin/bash", "-c"]

COPY ["predict.py", "rfc.bin", "dv.bin", "./"]

EXPOSE 9696

ENTRYPOINT [ "gunicorn","--bind=0.0.0.0:9696","predict:app" ]