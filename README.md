# A simple method to scale sentry across multiple machines

## Motivation

[Sentry](https://github.com/getsentry/sentry) is a great open source application
to track bugs in development and production environments. It has a very easy-to-deploy
[installer](https://github.com/getsentry/self-hosted), which is great for small teams.
However, the single node deployment will quickly reach processing bottlenecks
as the number of users grows rapidly. When you want to scale it,
you need to do some extra work.

This repository is a reproducible guide that can be used to scale sentry across machines.
Based on this project, you can create a cluster of sentry instances and can be upgraded
with the upstream in the future.

If you're familiar with k8s, please refer to the
[helm chart project](https://github.com/sentry-kubernetes/charts).

## Workload Analysis

According to my observation on our original single-node deployment, the main bottleneck
is the worker node consumes too much cpu resource.

On the 8C16G single-node deployment, the typical cpu usage is like this:

| node                               | cpu  | mem    |
|------------------------------------|------|--------|
| sentry_onpremise_worker_1          | 651% | 16.86% |
| sentry_onpremise_redis_1           | 41%  | 3.05%  |
| sentry_onpremise_ingest-consumer_1 | 32%  | 1.14%  |
| sentry_onpremise_postgres_1        | 17%  | 1.83%  |
| sentry_onpremise_relay_1           | 17%  | 6.08%  |
| sentry_onpremise_kafka_1           | 4%   | 12.70% |
| sentry_onpremise_clickhouse_1      | 2%   | 8.57%  |
| sentry_onpremise_memcached_1       | 1%   | 0.42%  |
| ...                                | ...  | ...    |

Obviously, the worker node consumes most of the cpu resource. If we can deploy worker on the separate machine,
the sentry throughput will be largely improved.

And, another thing I considered that is the simplicity of the deployment. If I need to
deploy each sentry service across machine and need to maintain a dedicate subnet for them,
it's better to deploy sentry on k8s. But, I don't want to make the deployment too complex,
because deploying and managing Kubernetes itself is already a complicated task with a high learning curve.

So, my simple(naive) solution to this problem is divide sentry into 2 parts:

- Multiple **Stateless Node**, named as **Web Node**
    - Web
    - Relay
    - Worker
- One **Stateful Center Node**, named as **Center Node**
    - Database (postgres, clickhouse & snuba)
    - Message Queue & Cache (redis, kafka)
    - Other services (cron, smtp, symbolicator, etc.)

This is the starting point of scalable sentry deployment:

- When worker nodes are not enough, deploy more **web node**.
- When the resource consumption of sub-services on the **center node** reaches its limit,
  the corresponding service will be split-out and deployed on a separate machine.

## Deploy manual

- Assume you have three 4C8G machines with **Ubuntu 22.04**:
    - 10.150.20.1 as **Center Node**
    - 10.150.20.2 as **Web Node 01**
    - 10.150.20.3 as **Web Node 02**
- _You may need a 4C8G machine as **Database Backup Node** for backup database._


### Deploy Center Node

_working in progress..._

