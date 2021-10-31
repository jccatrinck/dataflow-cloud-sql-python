import setuptools

PACKAGE_NAME = 'dataflow_cloud_sql_python'
PACKAGE_VERSION = '0.0.1'

setuptools.setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description='Dataflow Cloud SQL Python',
    author="Jessé Catrinck",
    author_email="jccatrinck@gmail.com",
    packages=setuptools.find_packages()
)