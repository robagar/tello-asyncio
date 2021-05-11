from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='tello_asyncio',
      version='1.4.0',
      description='Asyncio-based control library for the Tello drone',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/robagar/tello-asyncio',
      project_urls={
            'Documentation': 'https://tello-asyncio.readthedocs.io/en/latest/'
      },
      author='Rob Agar',
      author_email='tello_asyncio@fastmail.net',
      license='LGPL',
      packages=['tello_asyncio'],
      zip_safe=False,
      python_requires=">=3.7")