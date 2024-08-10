from setuptools import setup, find_packages

setup(
    name='context_curse',
    version='0.0.2',
    description='A CLI tool for managing files and directories before feeding them into an LLM.',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'context_curse=context_curse.main:main',
        ],
    },

    python_requires='>=3.6',
    install_requires=[
        'windows-curses;platform_system=="Windows"',
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/bin2ai/context_curse',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

)
