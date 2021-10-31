# dataflow-cloud-sql-python
Connecting to Cloud SQL from Dataflow in Python

---
### Summary

- [Explanation](#explanation)
- [Quick-start](#quick-start)
- [Structure](#structure)
- [Example](#example)
---
### Explanation

To make Cloud SQL available to the Dataflow pipeline we use a [custom container image](https://cloud.google.com/dataflow/docs/guides/using-custom-containers) and [instantiate Cloud SQL Proxy using Unix Sockets](https://cloud.google.com/sql/docs/postgres/connect-admin-proxy#unix-sockets) to connect to a production database instance without need for a public insecure IP or deal with SSL certificates.

---
### Quick-start

The only configuration needed is to create the `.env` file.

There is a `.env-example` that is ready to use, you can just rename it.

First use `make docker-push` to build and push a [custom container](https://cloud.google.com/dataflow/docs/guides/using-custom-containers) image to GCP.

Later use `make deploy` to deploy the pipeline to a dataflow template in Cloud Storage:

```shell
> make docker-push
> make deploy
```

To see all commands available:

```shell
> make help
```
---
### Structure
```
├── devops          // Custom container and entrypoint script
├── sql             // Postgres SQL static files
├── transformations // Apache Beam PTransform and DoFn
├── main.py         // The pipeline itself
├── Makefile        // Commands to deploy the pipeline to GCP
└── setup.py        // Python package for Dataflow remote workers (--setup_file option)
```

The `entrypoint.sh` script was build following these instructions [Run multiple services in a container](https://docs.docker.com/config/containers/multi-service_container/) using [Modifying the container entrypoint](https://cloud.google.com/dataflow/docs/guides/using-custom-containers#custom-entrypoint) as boilerplate

---
### Example

This pipeline in Dataflow:

![image](https://user-images.githubusercontent.com/7607939/139589543-2e3ad63c-be88-46bd-ae2f-d4c4f2360cb8.png)

---
