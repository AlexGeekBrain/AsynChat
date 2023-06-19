from setuptools import setup, find_packages

setup(name='server_chat_dz_geekbrain',
      version='0.1',
      description='server_packet',
      packages=find_packages(),
      author_email='aleksey@mail.ru',
      author='Aleksey Sobolev',
      install_requeres=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
