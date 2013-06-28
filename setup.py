import sys
from distutils.core import setup

extra = {}
if not sys.version_info >= (2, 7):
    extra['install_requires'] = ['ordereddict']

setup(
    name='pipedream',
    version='0.1.1-alpha',
    packages=[
        'pipedream',
        'pipedream.async'
    ],
    license='BSD',
    description='Flow based programming library for Python',
    long_description=open('README.rst').read(),
    author='Erik Simmler',
    author_email='tgecho@gmail.com',
    url='http://github.com/tgecho/pipedream/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
    **extra
)
