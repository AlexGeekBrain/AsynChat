import sys
from cx_Freeze import setup, Executable


build_exe_options = {
    'packages': ['server', 'common', 'doc', 'logs'], 
}

setup(name='server_chat',
      version='0.1',
      description='server_packet',
      options={
          'build_exe': build_exe_options
      },
      executables=[Executable('server.py',
                              target_name='server.exe',
                              )]
      )
