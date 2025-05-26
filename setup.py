from setuptools import setup, find_packages

setup(
    name='dimsum_streamline',  
    version='0.1.0',   
    packages=find_packages(),  
    install_requires=[os, sys, pandas, numpy, matplotlib, subprocess,argparse,time,getpass
        
    ],
    python_requires='>=3.6',  
    description='Automatize the process of running dimsum from local to remote',  
    long_description=open('README.md').read() if os.path.exists('README.md') else '', 
    long_description_content_type='text/markdown', 
    author='Romain Pastre',     
    author_email='rpastre@ibec.barcelona.eu',
    url='https://github.com/nocid/dimsum_streamline', 
    license='MIT',        
    classifiers=[
       
        'Development Status :: 3 - Alpha', 
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
