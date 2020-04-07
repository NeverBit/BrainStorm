from setuptools import setup, find_packages


setup(
    name = 'BrainStorm',
    version = '1.0.0',
    author = 'Shai Shapira',
    description = 'A snapshots collection system.',
    packages = find_packages(),
    install_requires = ['bson', 'Click', 'Flask', 'furl', 'grpcio-tools',
                        'protobuf', 'matplotlib', 'numpy', 'Pillow', 'pika',
                        'psycopg2', 'requests', 'SQLAlchemy'],
    tests_require = ['codecov', 'pytest', 'pytest-cov'],
)
