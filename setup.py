from distutils.core import setup

setup(
    name='pipedream',
    version='0.1.0-alpha',
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
)
