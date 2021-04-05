from setuptools import setup, find_packages
import os

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as fs:
    long_description = fs.read()

setup(
    name='Reddify',
    version='0.0.14',
    description='Creates and Updates a Spotify Playlist from Youtube Submissions on a Music Subreddit.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ibbeyo/Reddify',
    author='Ibbeyo',
    license='MIT',
    entry_points={
        "console_scripts": [
            "reddify = pyreddify.cli:main"
        ]
    },
    classifiers=classifiers,
    keywords=['reddit', 'spotify', 'music', 'playlist'],
    packages=find_packages(),
    install_requires=[
        'certifi==2020.12.5',
        'chardet==4.0.0',
        'click==7.1.2',
        'idna==2.10',
        'psaw==0.1.0',
        'python-dotenv==0.16.0',
        'requests==2.25.1',
        'six==1.15.0',
        'spotipy==2.17.1',
        'urllib3==1.26.4'
    ]
)