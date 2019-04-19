from pathlib import Path
import subprocess
import sys

import Pyro4
Pyro4.config.SERIALIZERS_ACCEPTED.add('dill')

daemon = Pyro4.Daemon(host='0.0.0.0' ,port=8000)

@Pyro4.expose
class Slave():
    def pip_install(self, *args):
        return subprocess.call([sys.executable, '-m', 'pip', 'install', *args])

    def create_module(self, name, source, is_pkg):
        path = name.split('.')
        if is_pkg:
            path.append('__init__.py')
        else:
            path[-1] += '.py'

        path = Path(*path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as h:
            h.write(source)
        
        return path

    def run(self, fn, *args, **arg_dict):
        return fn(*args, **arg_dict)

uri = daemon.register(Slave)
print(uri)
daemon.requestLoop()
