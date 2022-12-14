import io
from setuptools import find_packages, setup

# Read in the README for the long description on PyPI
def long_description():
    with io.open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()
    return readme

# Read requirements dependencies
def requirements():
    with open('requirements.txt') as f:
        required = f.read().splitlines()
    return required

setup(name='yarn log collector',
      version='1.0',
      description='made by AWS Proserve korea AID Practice',
      long_description=long_description(),
      url='https://gitlab.aws.dev/proserve-kr-dna/hadoop-migration-assessment.git',
      author='aws-korea-proserve-aid',
      author_email='aws-korea-proserve-aid@amazon.com',
      packages=find_packages(),
      install_requires=requirements(),
      python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
      zip_safe=False)
