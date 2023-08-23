import json
import sys

import yaml
import os
from pprint import pprint
from pathlib import Path

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

base_dir = Path(__file__).parent.resolve()

SENTRY_MASTER_HOST = os.environ.get('SENTRY_MASTER_HOST')

if not SENTRY_MASTER_HOST:
    print("SENTRY_MASTER_HOST is not set", file=sys.stderr)
    exit(-1)

with open(base_dir / "example.yml", 'r') as f:
    docker_config = yaml.safe_load(f)
    docker_config['x-snuba-defaults']['environment']['CLICKHOUSE_HOST'] = SENTRY_MASTER_HOST
    docker_config['x-snuba-defaults']['environment']['DEFAULT_BROKERS'] = f"{SENTRY_MASTER_HOST}:9092"
    docker_config['x-snuba-defaults']['environment']['REDIS_HOST'] = f"{SENTRY_MASTER_HOST}"
    docker_config['x-snuba-defaults']['environment']['REDIS_PASSWORD'] = '${REDIS_PASSWORD}'
    docker_config['x-snuba-defaults']['environment']['SENTRY_EVENT_RETENTION_DAYS'] = 45

    docker_config['x-sentry-defaults']['environment']['SNUBA'] = f"http://{SENTRY_MASTER_HOST}:1218"
    docker_config['x-sentry-defaults']['environment']['VROOM'] = f"http://{SENTRY_MASTER_HOST}:8085"
    docker_config['x-sentry-defaults']['environment']['SENTRY_EVENT_RETENTION_DAYS'] = 45

    docker_config['services']['kafka']['environment']['KAFKA_ZOOKEEPER_CONNECT'] = f"{SENTRY_MASTER_HOST}:2181"
    docker_config['services']['kafka']['environment']['KAFKA_ADVERTISED_LISTENERS'] = \
        f"PLAINTEXT://{SENTRY_MASTER_HOST}:9092"
    docker_config['services']['kafka']['environment']['KAFKA_LOG4J_LOGGERS'] = \
        "kafka.cluster=WARN,kafka.controller=WARN,kafka.coordinator=WARN,kafka.log=WARN,kafka.server=INFO,kafka.zookeeper=INFO,state.change.logger=WARN"

    del docker_config['services']['geoipupdate']

with open(base_dir / "docker-compose-master.yml", 'w') as new_conf:
    yaml.dump(docker_config, new_conf, default_flow_style=False)

with open(base_dir / "example.json", "w") as f:
    json.dump(docker_config, f, ensure_ascii=False, indent=2)
