from setuptools import setup, find_packages

setup(name='regex_classifier',
      version='0.0.1',
      description='Tools for simple information extraction of doctor-patient notes',
      author='Sam Banning',
      author_email='samcbanning@gmail.com',
      packages=find_packages(),
      install_requires=['jinja2'],
      include_package_data=True
)