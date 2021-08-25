import os

if 'MY_VAR' not in os.environ:
    print('MY_VAR not in enviroment')
else:
    print(os.environ['MY_VAR'])

