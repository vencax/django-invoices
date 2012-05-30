from setuptools import setup, find_packages

print find_packages()

setup(
    name='django-invoices',
    version='0.1',
    description='Simple Django invoices application.',
    author='Vaclav Klecanda',
    author_email='vencax77@gmail.com',
    url='https://github.com/applecat/django-simple-poll',
    packages=find_packages(),
    include_package_data=True,
)
