# stdlib
import logging

# project
from checks import AgentCheck
from tests.checks.common import AgentCheckTest
from utils.dockerutil import get_client

# 3rd party
from nose.plugins.attrib import attr

import json

log = logging.getLogger('tests')

CONTAINERS_TO_RUN = [
    "nginx",
    "redis:latest",

]

BASIC_CONT_METRICS = [
    "docker.containers.running",
    "docker.cpu.system",
    "docker.cpu.user",
    "docker.io.read_bytes",
    "docker.io.write_bytes",
    "docker.mem.cache",
    "docker.mem.rss",
    "docker.net.bytes_rcvd",
    "docker.net.bytes_sent",
]

BASIC_IMAGE_METRICS = [
    "docker.image.size",
    "docker.image.virtual_size",
    "docker.images.available",
    "docker.images.intermediate",
]


@attr(requires='docker_daemon')
class TestCheckDockerDaemon(AgentCheckTest):
    CHECK_NAME = 'docker_daemon'

    def setUp(self):
        self.docker_client = get_client()
        for c in CONTAINERS_TO_RUN:
            images = [i["RepoTags"][0] for i in self.docker_client.images(c.split(":")[0]) if i["RepoTags"][0].startswith(c)]
            if len(images) == 0:
                for line in self.docker_client.pull(c, stream=True):
                    print line
            
        self.containers = []
        for c in CONTAINERS_TO_RUN:
            name = "test-new-{0}".format(c.replace(":", "-"))
            cont = self.docker_client.create_container(c, detach=True, name=name)
            self.containers.append(cont)

        for c in self.containers:
            log.info("Starting container: {0}".format(c))
            self.docker_client.start(c)


    def tearDown(self):
        for c in self.containers:
            log.info("Stopping container: {0}".format(c))
            self.docker_client.remove_container(c, force=True)

    def test_basic_config_single(self):
        expected_metrics = [
            ('docker.containers.running', ['docker_image:nginx', 'image_name:nginx']),
            ('docker.containers.running', ['docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.containers.stopped', ['docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.containers.stopped', ['docker_image:nginx', 'image_name:nginx']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.7', 'image_tag:1.7.12']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.1']),
            ('docker.image.size', ['image_name:redis', 'image_tag:latest']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1', 'image_tag:1.9', 'image_tag:1.9.4', 'image_tag:latest']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.0']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.7.11']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.2']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.3']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.1']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.7', 'image_tag:1.7.12']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.0']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.7.11']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1', 'image_tag:1.9', 'image_tag:1.9.4', 'image_tag:latest']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.2']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.3']),
            ('docker.image.virtual_size', ['image_name:redis', 'image_tag:latest']),
            ('docker.images.available', None),
            ('docker.images.intermediate', None),
            ('docker.mem.cache', ['container_name:test-new-nginx', 'docker_image:nginx', 'image_name:nginx']),
            ('docker.mem.cache', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.mem.rss', ['container_name:test-new-nginx', 'docker_image:nginx', 'image_name:nginx']),
            ('docker.mem.rss', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
        ]


        config = {
                "init_config": {
                },
                "instances": [{
                    "url": "unix://var/run/docker.sock",
                   
                },
            ],
        }

        self.run_check(config, force_reload=True)
        for mname, tags in expected_metrics:
            self.assertMetric(mname, tags=tags, count=1, at_least=1)


    def test_basic_config_twice(self):
        expected_metrics = [
            ('docker.containers.running', ['docker_image:nginx', 'image_name:nginx']),
            ('docker.containers.running', ['docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.containers.stopped', ['docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.containers.stopped', ['docker_image:nginx', 'image_name:nginx']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.7', 'image_tag:1.7.12']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.1']),
            ('docker.image.size', ['image_name:redis', 'image_tag:latest']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1', 'image_tag:1.9', 'image_tag:1.9.4', 'image_tag:latest']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.0']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.7.11']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.2']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.3']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.1']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.7', 'image_tag:1.7.12']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.0']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.7.11']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1', 'image_tag:1.9', 'image_tag:1.9.4', 'image_tag:latest']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.2']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.3']),
            ('docker.image.virtual_size', ['image_name:redis', 'image_tag:latest']),
            ('docker.images.available', None),
            ('docker.images.intermediate', None),
            ('docker.cpu.system', ['container_name:test-new-nginx', 'docker_image:nginx', 'image_name:nginx']),
            ('docker.cpu.system', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.cpu.user', ['container_name:test-new-nginx', 'docker_image:nginx', 'image_name:nginx']),
            ('docker.cpu.user', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.io.read_bytes', ['container_name:test-new-nginx', 'docker_image:nginx', 'image_name:nginx']),
            ('docker.io.read_bytes', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.io.write_bytes', ['container_name:test-new-nginx', 'docker_image:nginx', 'image_name:nginx']),
            ('docker.io.write_bytes', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.mem.cache', ['container_name:test-new-nginx', 'docker_image:nginx', 'image_name:nginx']),
            ('docker.mem.cache', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.mem.rss', ['container_name:test-new-nginx', 'docker_image:nginx', 'image_name:nginx']),
            ('docker.mem.rss', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.net.bytes_rcvd', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.net.bytes_rcvd', ['container_name:test-new-nginx', 'docker_image:nginx', 'image_name:nginx']),
            ('docker.net.bytes_sent', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.net.bytes_sent', ['container_name:test-new-nginx', 'docker_image:nginx', 'image_name:nginx'])

        ]

        custom_tags = ["extra_tag", "env:testing"]
        config = {
                "init_config": {
                },
                "instances": [{
                    "url": "unix://var/run/docker.sock",
                    "tags": custom_tags,
                   
                },
            ],
        }

        self.run_check_twice(config, force_reload=True)
        for mname, tags in expected_metrics:
            expected_tags = list(custom_tags)
            if tags is not None:
                expected_tags += tags
            self.assertMetric(mname, tags=expected_tags, count=1, at_least=1)

    def test_exclude_filter(self):
        expected_metrics = [
            ('docker.containers.running', ['docker_image:nginx', 'image_name:nginx']),
            ('docker.containers.running', ['docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.containers.stopped', ['docker_image:nginx', 'image_name:nginx']),
            ('docker.containers.stopped', ['docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.cpu.system', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.cpu.user', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.7', 'image_tag:1.7.12']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.1']),
            ('docker.image.size', ['image_name:redis', 'image_tag:latest']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1', 'image_tag:latest', 'image_tag:1.9', 'image_tag:1.9.4']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.0']),
            ('docker.image.size', ['image_name:buildpack-deps', 'image_tag:precise']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.7.11']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.2']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.3']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.1']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.7', 'image_tag:1.7.12']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.0']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.7.11']),
            ('docker.image.virtual_size', ['image_name:buildpack-deps', 'image_tag:precise']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1', 'image_tag:latest', 'image_tag:1.9', 'image_tag:1.9.4']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.2']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.3']),
            ('docker.image.virtual_size', ['image_name:redis', 'image_tag:latest']),
            ('docker.images.available', None),
            ('docker.images.intermediate', None),
            ('docker.io.read_bytes', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.io.write_bytes', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.mem.cache', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.mem.rss', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.net.bytes_rcvd', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.net.bytes_sent', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest'])
        ]
        config = {
                "init_config": {
                },
                "instances": [{
                    "url": "unix://var/run/docker.sock",
                    "exclude": ["docker_image:nginx"]
                },
            ],
        }


        self.run_check_twice(config, force_reload=True)

        for mname, tags in expected_metrics:
            self.assertMetric(mname, tags=tags, count=1, at_least=1)

    def test_include_filter(self):
        expected_metrics = [
            ('docker.containers.running', ['docker_image:nginx', 'image_name:nginx']),
            ('docker.containers.running', ['docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.containers.stopped', ['docker_image:nginx', 'image_name:nginx']),
            ('docker.containers.stopped', ['docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.cpu.system', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.cpu.user', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.7', 'image_tag:1.7.12']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.1']),
            ('docker.image.size', ['image_name:redis', 'image_tag:latest']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1', 'image_tag:latest', 'image_tag:1.9', 'image_tag:1.9.4']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.0']),
            ('docker.image.size', ['image_name:buildpack-deps', 'image_tag:precise']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.7.11']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.2']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.3']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.1']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.7', 'image_tag:1.7.12']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.0']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.7.11']),
            ('docker.image.virtual_size', ['image_name:buildpack-deps', 'image_tag:precise']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1', 'image_tag:latest', 'image_tag:1.9', 'image_tag:1.9.4']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.2']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.3']),
            ('docker.image.virtual_size', ['image_name:redis', 'image_tag:latest']),
            ('docker.images.available', None),
            ('docker.images.intermediate', None),
            ('docker.io.read_bytes', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.io.write_bytes', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.mem.cache', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.mem.rss', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.net.bytes_rcvd', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest']),
            ('docker.net.bytes_sent', ['container_name:test-new-redis-latest', 'docker_image:redis:latest', 'image_name:redis', 'image_tag:latest'])
        ]
        config = {
                "init_config": {
                },
                "instances": [{
                    "url": "unix://var/run/docker.sock",
                    "include": ["image_name:redis"],
                    "exclude": [".*"]
                },
            ],
        }


        self.run_check_twice(config, force_reload=True)

        for mname, tags in expected_metrics:
            self.assertMetric(mname, tags=tags, count=1, at_least=1)

    def test_tags_options(self):
        expected_metrics = [
            ('docker.containers.running', ["container_command:nginx -g 'daemon off;'"]),
            ('docker.containers.running', ['container_command:/entrypoint.sh redis-server']),
            ('docker.containers.stopped', ["container_command:nginx -g 'daemon off;'"]),
            ('docker.containers.stopped', ['container_command:/entrypoint.sh redis-server']),
            ('docker.cpu.system', ["container_command:nginx -g 'daemon off;'"]),
            ('docker.cpu.system', ['container_command:/entrypoint.sh redis-server']),
            ('docker.cpu.user', ['container_command:/entrypoint.sh redis-server']),
            ('docker.cpu.user', ["container_command:nginx -g 'daemon off;'"]),
            ('docker.image.size', ['image_name:<none>', 'image_tag:<none>']),
            ('docker.image.size', ['image_name:ubuntu', 'image_tag:14.04']),
            ('docker.image.size', ['image_name:ruby', 'image_tag:2.2']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.7', 'image_tag:1.7.12']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.1']),
            ('docker.image.size', ['image_name:redis', 'image_tag:latest']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1', 'image_tag:1.9.4', 'image_tag:1.9', 'image_tag:latest']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.0']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.7.11']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.2']),
            ('docker.image.size', ['image_name:nginx', 'image_tag:1.9.3']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.1']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.7', 'image_tag:1.7.12']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.0']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.7.11']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1', 'image_tag:1.9.4', 'image_tag:1.9', 'image_tag:latest']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.2']),
            ('docker.image.virtual_size', ['image_name:nginx', 'image_tag:1.9.3']),
            ('docker.image.virtual_size', ['image_name:redis', 'image_tag:latest']),
            ('docker.images.available', None),
            ('docker.images.intermediate', None),
            ('docker.io.read_bytes', ["container_command:nginx -g 'daemon off;'"]),
            ('docker.io.read_bytes', ['container_command:/entrypoint.sh redis-server']),
            ('docker.io.write_bytes', ['container_command:/entrypoint.sh redis-server']),
            ('docker.io.write_bytes', ["container_command:nginx -g 'daemon off;'"]),
            ('docker.mem.cache', ["container_command:nginx -g 'daemon off;'"]),
            ('docker.mem.cache', ['container_command:/entrypoint.sh redis-server']),
            ('docker.mem.rss', ['container_command:/entrypoint.sh redis-server']),
            ('docker.mem.rss', ["container_command:nginx -g 'daemon off;'"]),
            ('docker.net.bytes_rcvd', ['container_command:/entrypoint.sh redis-server']),
            ('docker.net.bytes_rcvd', ["container_command:nginx -g 'daemon off;'"]),
            ('docker.net.bytes_sent', ["container_command:nginx -g 'daemon off;'"]),
            ('docker.net.bytes_sent', ['container_command:/entrypoint.sh redis-server'])
        ]
        config = {
                "init_config": {
                },
                "instances": [{
                    "url": "unix://var/run/docker.sock",
                    "performance_tags": ["container_command"],
                    "container_tags": ["container_command"]
                },
            ],
        }


        self.run_check_twice(config, force_reload=True)
        for mname, tags in expected_metrics:
            self.assertMetric(mname, tags=tags, count=1, at_least=1)
