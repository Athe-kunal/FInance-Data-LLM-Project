FROM python:3.11-slim-bullseye

COPY ./requirements.txt .

# RUN apt-get update && apt-get install -y 
RUN pip3 install --upgrade pip

RUN pip3 --no-cache-dir install -r requirements.txt

WORKDIR /src
COPY . /src
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# ENTRYPOINT ["uvicorn", "server:app","--host", "0.0.0.0", "--port", "8000"]
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "Intro.py", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false", "--server.address", "0.0.0.0"]