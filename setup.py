from setuptools import setup, find_packages
import os


data_files = [(d, [os.path.join(d, f) for f in files])
              for d, folders, files in os.walk(os.path.join('src', 'config'))]

setup(name='sdm_vault_automation',
      version='1.0',
      description='Framework for SDM Automation and Read and Forward SDM Audit Logs to ElastiSearh',
      author='Adam Pridgen',
      author_email='apridgen@roblox.com',
      packages=find_packages('src'),
      package_dir={'': 'src'},
)