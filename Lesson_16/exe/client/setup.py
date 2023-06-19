import sys
from cx_Freeze import setup, Executable


build_exe_options = {
    'packages': ['client', 'common', 'doc', 'logs'], 
}

setup(name='client_chat',
      version='0.1',
      description='client_packet',
      options={
          'build_exe': build_exe_options
      },
      executables=[Executable('client.py',
                              target_name='client.exe',
                              )]
      )
