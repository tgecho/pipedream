=========
Pipedream
=========
Flow based programming library
==============================

Pipedream is a lightweight library that helps organize Python software around concepts inspired by flow based programming. It allows you to define the dependencies between a number of loosely related resources declaratively and then uses this information to coordinate the control flow.

Apart from being an interesting and productive way to structure a program, this can also greatly simplify concurrency, testing and modularity.

Installing
----------
Run ``pip install pipedream`` to install it quickly, or you can checkout the source at
``http://github.com/tgecho/pipedream/``

Quickstart
----------
With Pipedream, you define a dispatcher object to keep track of the resources you want to use:

.. code-block:: python

    from pipedream import Dispatcher
    dispatcher = Dispatcher()

You can add functions to the dispatcher with a simple decorator:

.. code-block:: python

    @dispatcher.add
    def who():
        return 'World'

You define dependencies by specifying the name of the function you need as an argument:

.. code-block:: python

    @dispatcher.add
    def greet(who):
        return 'Hello {0}!'.format(who)

You can then ask the dispatcher to run any of its functions by name:

.. code-block:: python

    assert dispatcher.call('greet') == 'Hello World!'

You can also specify keyword arguments at call time. These will be used even if the dispatcher has a function available that matches that name:

.. code-block:: python

    assert dispatcher.call('greet', who='Everyone') == 'Hello Everyone!'


Concurrency
-----------
In a typical web application, a view function will make a number of database queries or other remote API calls and return the results rendered in a template. All of this work is usually done in a serial fashion, resulting in a lot of time spent waiting on network latency.

Since many of these steps are often independent of each other, doing work concurrently can cut the total response time dramatically. Coordinating this manually can get complicated very quickly, especially when certain steps depend on the results of other steps.

Once the dispatcher knows about the dependencies between various parts of a
program, it is able to use an optional async back end to automatically coordinate
the flow and make as concurrent as possible.

Currently the only async back end supported is powered by gevent_. To use it, you will need to install the ``gevent`` <https://pypi.python.org/pypi/gevent> and ``ProxyTypes`` <https://pypi.python.org/pypi/ProxyTypes> libraries and then use the following code to setup your dispatcher:

.. code-block:: python

    from pipedream import Dispatcher
    from pipedream.async.gevent import GeventPool
    dispatcher = Dispatcher(async_pool=GeventPool())

All functions will automatically run in separate greenlets and the dispatcher will take care of coordinating their progress.

Advanced Decorating
-------------------
There are a few more flexible options available in addition to the simple form of function decorating. If you want to manually specify the name of a function, you can do so as the first argument of the decorator:

.. code-block:: python

    @dispatcher.add('foo')
    def bar():
        return 'A Bar named Foo.'

If you want to specify the dependencies and use different names within the function, you can also do so in the decorator. The function will receive them in the order specified:

.. code-block:: python

    @dispatcher.add(requires=['a_really_long_name'])
    def medium(long):
        return '{0} is really big!'.format(long)

.. _gevent: http://www.gevent.org/
.. _ProxyTypes: https://pypi.python.org/pypi/ProxyTypes