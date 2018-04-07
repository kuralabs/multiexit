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

from time import sleep
from signal import SIGTERM
from os import getpid, kill
from multiprocessing import Process
from logging import StreamHandler, basicConfig, DEBUG

from colorlog import ColoredFormatter

from multiexit import install, register, unregister


COLOR_FORMAT = (
    '  {thin_white}{asctime}{reset} | '
    '{log_color}{levelname:8}{reset} | '
    '{thin_white}{processName}{reset} | '
    '{log_color}{message}{reset}'
)


if __name__ == '__main__':

    # Always call install() on the main process
    install()

    # Setup logging
    formatter = ColoredFormatter(fmt=COLOR_FORMAT, style='{')
    handler = StreamHandler()
    handler.setFormatter(formatter)
    basicConfig(handlers=[handler], level=DEBUG)

    def _subproc1():

        def _subproc2():

            def _subproc3():
                sleep(1000)

            subproc3 = Process(
                name='SubProcess3',
                target=_subproc3,
            )
            subproc3.start()

            @register
            def clean_subproc2():
                print('Terminating subsubchild {}'.format(
                    subproc3.pid,
                ))
                subproc3.terminate()
                subproc3.join()
                print('Subsubchild {} ended with {}'.format(
                    subproc3.pid,
                    subproc3.exitcode,
                ))
            sleep(1000)

        subproc2 = Process(
            name='SubProcess2',
            target=_subproc2,
        )
        subproc2.start()

        @register
        def clean_subproc1():
            print('Terminating subchild {}'.format(
                subproc2.pid,
            ))
            subproc2.terminate()
            subproc2.join()
            print('Subchild {} ended with {}'.format(
                subproc2.pid,
                subproc2.exitcode,
            ))

        sleep(1000)

    subproc1 = Process(
        name='SubProcess1',
        target=_subproc1,
    )
    # proc.daemon = True
    # daemon means that signals (like SIGTERM) will be propagated automatically
    # to children. Set to false (the default), to handle the SIGTERM
    # (process.terminate()) to the children yourself.
    subproc1.start()

    # Register a cleaner using a decorator
    @register
    def clean_main():
        print('Terminating child {}'.format(
            subproc1.pid,
        ))
        subproc1.terminate()
        subproc1.join()
        print('Child {} ended with {}'.format(
            subproc1.pid,
            subproc1.exitcode,
        ))

    # Register / unregister a cleaner using functions
    def not_a_cleaner():
        print('This should never be called')

    register(not_a_cleaner)
    unregister(not_a_cleaner)

    # Wait, and then kill main process
    for count in range(3, 0, -1):
        print('{} ... '.format(count), end='', flush=True)
        sleep(1 / 3)
    print()

    # Suicide
    kill(getpid(), SIGTERM)
