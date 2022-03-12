import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='synochat',
    version='1.0.2',
    author='Mikael Schultz',
    author_email='mikael@bitcanon.com',
    description='A library for the Synology Chat API written in Python 3.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bitcanon/synochat',
    packages=setuptools.find_packages(),
    install_requires=['requests', 'flask'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)