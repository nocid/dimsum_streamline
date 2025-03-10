from setuptools import setup, find_packages

setup(
    name='dimsum_streamline',  # **Required**:  Your package name (what users will use to install, e.g., `pip install my_package`)
    version='0.1.0',   # **Required**:  Start with a version number
    packages=find_packages(),  # **Required**:  Automatically find all packages and subpackages
    install_requires=[os, sys, pandas, numpy, matplotlib, subprocess,argparse,time,getpass
        # List any dependencies your package needs here, e.g., 'requests >= 2.20'
    ],
    python_requires='>=3.6',  # Specify minimum Python version if needed
    description='Automatize the process of running dimsum from local to remote',  # Short, informative description
    long_description=open('README.md').read() if os.path.exists('README.md') else '', # Optional: Long description from README
    long_description_content_type='text/markdown', # If you're using Markdown for README
    author='Romain Pastre',        # Your name
    author_email='rpastre@ibec.barcelona.eu', # Your email
    url='https://github.com/yourusername/my_package', # Link to your GitHub repository (once created)
    license='MIT',          # Choose a license (e.g., MIT, Apache 2.0, GPL)
    classifiers=[
        # Optional: Classifiers help users find your package on PyPI
        'Development Status :: 3 - Alpha', # Or '4 - Beta', '5 - Production/Stable'
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
