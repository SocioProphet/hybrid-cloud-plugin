#!/usr/bin/env python

import time
import subprocess
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError

DOCKER_BOOTSTRAP_COMMAND = 'docker daemon -H ' \
                           'unix:///var/run/docker-bootstrap.sock ' \
                           '-p /var/run/docker-bootstrap.pid ' \
                           '--iptables=false --ip-masq=false ' \
                           '--bridge=none ' \
                           '--graph=/var/lib/docker-bootstrap 2> ' \
                           '/var/log/docker-bootstrap.log 1> /dev/null &'
SUCCESS_PROCESS = 'pgrep -f \'docker daemon -H unix:///var/run/docker-bootstrap.sock\''


def docker_bootstrap():

    process = subprocess.Popen(
        ['sudo', 'sh', '-c', DOCKER_BOOTSTRAP_COMMAND],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if process.returncode:
        output, error = process.communicate()
        raise NonRecoverableError(
            'Failed to start Docker bootstrap. '
            'Output: {0}'
            'Error: {1}'.format(output, error)
        )

    return

if __name__ == '__main__':

    ctx.logger.info('Starting Docker bootstrap.')

    docker_bootstrap()

    time.sleep(5)

    timeout = time.time() + 5
    success = False
    for x in range(0,30):
        success_process = subprocess.Popen(
            SUCCESS_PROCESS.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(.5)
        if not success_process.returncode:
            success = True
            break
    if not success:
        raise NonRecoverableError(
            'Failed to start Docker bootstrap '
            'That\'s life.')
