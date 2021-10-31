#!/bin/bash
  
# turn on bash's job control
set -m

# Cloud SQL Proxy for one or multiple instances
if [ -n "${CLOUD_SQL_PROXY_INSTANCES}" ]; then
    cloud_sql_proxy -dir=/cloudsql -instances=${CLOUD_SQL_PROXY_INSTANCES} -credential_file=${CLOUD_SQL_PROXY_CREDENTIAL_FILE} &
    # Wait for all instances
    for instance in ${CLOUD_SQL_PROXY_INSTANCES//,/ } ; do
        while ! pg_isready -h /cloudsql/${instance}; do
            echo "Waiting for instance ${instance} to be online"
            sleep 0.100
        done
    done
fi

# Pass command arguments to the default boot script.
/opt/apache/beam/boot "$@"