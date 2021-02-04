from setuptools import setup, find_packages

setup(
    long_description=open("README.md", "r").read(),
    name="torsniffui",
    version="0.42",
    description="put results of torsniff into a database and search via a web ui",
    author="Pascal Eberlein",
    author_email="pascal@eberlein.io",
    url="https://github.com/nbdy/torsniffui",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords="torsniff p2p crawler ui web",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'torsniffui = torsniffui.__main__:main'
        ]
    },
    package_data={
        "torsniffui": ["templates/*.html"]
    },
    install_requires=open("requirements.txt").readlines()
)
