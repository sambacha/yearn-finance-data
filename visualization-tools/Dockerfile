FROM python:3.7.6-stretch

RUN apt-get update \
  && apt-get install -y --no-install-recommends inotify-tools \
  && rm -rf /var/lib/apt/lists/*

# Add Tini
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

WORKDIR /app

# installing dependencies for plotting
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# dependencies for awscli login
RUN pip install awscli --upgrade --user

COPY . .
ENTRYPOINT ["/tini", "--"]
CMD bash