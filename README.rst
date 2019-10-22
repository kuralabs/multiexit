=========
multiexit
=========

A better, saner and more useful atexit_ replacement for Python 3 that supports
multiprocessing_.

Inspired by the following StackOverflow question and experience on building
multiprocessing daemons:

https://stackoverflow.com/q/2546276

.. _atexit: https://docs.python.org/3/library/atexit.html
.. _multiprocessing: https://docs.python.org/3/library/multiprocessing.html

``multiexit`` will install a handler for the SIGTERM and SIGINT signals and
execute the registered exit functions in *LIFO* order (Last In First Out).

Exit functions can be registered so that only the calling process will call
them (the default), or as *shared* exit functions that will be called by the
calling process and all the children subprocesses that inherit it.


Install
=======

``multiexit`` is available for Python 3 from PyPI_.

.. _PyPI: https://pypi.python.org/pypi/multiexit/

.. code-block:: sh

    pip3 install multiexit


API
===

On the main process, before forking or creating any subprocess, call
``multiexit.install``:

.. code-block:: python

    def install(
        signals=(signal.SIGTERM, signal.SIGINT),
        except_hook=True,
    )

:signals:
 Signals to install handler. Usually only ``SIGTERM`` and ``SIGINT`` are
 required.

:except_hook:
 Also install a `sys.excepthook`_ that will call the exit functions in case of
 an unexpected exception.

.. _`sys.excepthook`: https://docs.python.org/3/library/sys.html#sys.excepthook

Then, for each exit function, on any subprocess, call ``multiexit.register``:

.. code-block:: python

    register(func, shared=False)

:func:
 Exit function to register. Any callable without arguments.

:shared:
 If ``shared``, the exit function will be called by the calling process but
 also by all the children subprocesses that inherit it (thus the ones
 created after registering it).
 If ``shared`` is ``False``, the default, only the calling process will execute
 the exit function.


Example
=======

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
        # This installs a handler for SIGTERM and SIGINT. Subprocesses will
        # inherit this handler. It also assigns the current PID as the master
        # process, which will allow to choose between exit or os._exit calls
        # when quitting.
        install()

        def _subproc1():

            @register
            def subproc1_clean():
                print('Subprocess clean!')

            sleep(1000)

        # Register shared exit function so all subprocess call this
        def shared_exit():
            print('Shared exit being called by {} ...'.format(getpid()))

        register(shared_exit, shared=True)

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


Changes
=======

1.5.0
-----

A ``SIGINT`` handler is now installed by default to handle Ctrl+C. This
means that Python's ``signal.default_int_handler`` is overridden, thus
Ctrl+C no longer raises ``KeyboardInterrupt``. If this behavior is
undesired, pass ``signals=(signal.SIGTERM)`` when calling ``install()``.

Ctrl+C sends ``SIGINT`` to all processes in the terminal's foreground
process group, so in order to behave like a ``SIGTERM`` shutdown flow, which
is sent only on the parent process, the handler will ignore ``SIGINT`` on
the children to allow the parent to decide what to do with the subprocesses
and their corresponding shutdown sequence.

This fixes issue #3


License
=======

::

   Copyright (C) 2018-2019 KuraLabs S.R.L

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
