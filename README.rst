=========
multiexit
=========

A better, saner and more useful atexit_ replacement for Python 3 that supports
multiprocessing_.

Inspired by the following StackOverflow question and experience on building
multiprocess daemons:

https://stackoverflow.com/q/2546276

.. _atexit: https://docs.python.org/3/library/atexit.html
.. _multiprocessing: https://docs.python.org/3/library/multiprocessing.html

``multiexit`` will install a handler for the SIGTERM signal and execute the
registered exit functions in *LIFO* order (Last In First Out). ``multiexit``
will only execute exit functions that are owned by the process shutting down.


Install
=======

``multiexit`` is available for Python 3 from PyPI_.

.. _PyPI: https://pypi.python.org/pypi/multiexit/

.. code-block:: sh

    pip3 install multiexit


Usage
=====

.. code-block:: python

    from time import sleep
    from signal import SIGTERM
    from os import kill, getpid
    from multiprocessing import Process

    from multiexit import install, register, unregister


    if __name__ == '__main__':

        # Always call install() on the main process before creating any
        # subprocess
        #
        # This will install a required handler for SIGTERM. Subprocesses must
        # inherit this handler. Plus it assigns a pid as the master process
        # for exit or os._exit call.
        install()

        def _subproc1():

            @register
            def subproc1_clean():
                print('Subprocess clean!')

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

        # Wait, and then kill main process
        sleep(3)

        # Suicide
        kill(getpid(), SIGTERM)

For a more extensive example check out ``example.py``.


License
=======

::

   Copyright (C) 2018 KuraLabs S.R.L

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.
