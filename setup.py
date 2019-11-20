from setuptools import setup, find_packages

setup(
    name='text-db',
    version='0.1.0',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=True,
    python_requires='>= 3.6',
)
