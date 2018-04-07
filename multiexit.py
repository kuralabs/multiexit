# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 KuraLabs S.R.L
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
atexit replacement that supports multiprocessing.
"""

import os
import sys
import signal
from logging import getLogger
from collections import OrderedDict
from multiprocessing import current_process


__version__ = '1.0.0'


log = getLogger(__name__)


_MAIN_PROC = None
_REGISTRY = OrderedDict()


def _header():
    pid = os.getpid()
    path = list(_REGISTRY.keys())

    if not path or path[-1] != pid:
        path.append(pid)

    return 'Process "{}" (pid: {}, path: {})'.format(
        current_process().name,
        pid,
        ', '.join(map(str, path)),
    )


def _handler(signum, frame):
    log.debug('{} got signal {}'.format(
        _header(),
        signal.Signals(signum).name),
    )

    owned = _REGISTRY.get(os.getpid())
    if owned:
        for func in owned:
            func()

    if _MAIN_PROC == os.getpid():
        log.debug('{} system exit'.format(
            _header(),
        ))
        sys.exit(0)

    log.debug('{} subprocess exit'.format(
        _header(),
    ))
    os._exit(0)


def install():
    global _MAIN_PROC

    if _MAIN_PROC is None:
        _MAIN_PROC = os.getpid()
        log.debug('{} set as main process'.format(
            _header(),
            _MAIN_PROC,
        ))

    signal.signal(signal.SIGTERM, _handler)
    log.debug('{} installed SIGTERM signal handler'.format(
        _header(),
    ))


def register(func):
    assert callable(func)
    install()

    process_registry = _REGISTRY.setdefault(os.getpid(), [])
    if func not in process_registry:
        process_registry.append(func)
        log.debug('{} added exit callable {}'.format(
            _header(),
            func,
        ))

    return func


def unregister(func):
    assert callable(func)
    install()

    process_registry = _REGISTRY.get(os.getpid(), None)
    if process_registry is not None:
        if func in process_registry:
            process_registry.remove(func)
            log.debug('{} removed exit callable {}'.format(
                _header(),
                func,
            ))
            return True

    return False


__all__ = [
    'install',
    'register',
    'unregister',
]
