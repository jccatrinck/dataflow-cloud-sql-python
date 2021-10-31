FROM apache/beam_python3.8_sdk:2.33.0

RUN apt-get -y update
RUN apt-get -y install postgresql-client

# GCP Service Account with Cloud SQL Client role
ARG CREDENTIAL_FILE
COPY ${CREDENTIAL_FILE} /service-account/file.json

RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /bin/cloud_sql_proxy
RUN chmod +x /bin/cloud_sql_proxy
RUN mkdir /cloudsql
RUN chmod 777 /cloudsql

RUN apt-get -y update && apt-get -y upgrade make
RUN python -m pip install --upgrade pip

# Install dependencies
COPY ./Makefile Makefile
RUN make install-dependencies

# Run multiple services container: Apache Beam + Cloud SQL Proxy
# https://docs.docker.com/config/containers/multi-service_container/
ARG CLOUD_SQL_INSTANCES
ENV CLOUD_SQL_PROXY_INSTANCES=${CLOUD_SQL_INSTANCES}
ENV CLOUD_SQL_PROXY_CREDENTIAL_FILE=/service-account/file.json
COPY ./devops/entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh
ENTRYPOINT [ "/scripts/entrypoint.sh" ]