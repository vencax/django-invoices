import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install


class MyInstall(install):
    def run(self):
        projpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'invoices')
        print 'Generating MO files in %s' % projpath
        subprocess.call(['django-admin.py', 'compilemessages'],
                        cwd=projpath)
        install.run(self)

setup(
    name='django-invoices',
    version='0.2',
    description='Simple Django invoices application',
    author='Vaclav Klecanda',
    author_email='vencax77@gmail.com',
    url='www.vxk.cz',
    packages=find_packages(),
    include_package_data=True,
    cmdclass={'install': MyInstall},
)
