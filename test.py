import asyncio

from remotejob import RemoteJob
from testmod import b, c
import testmod

async def main():
    with RemoteJob() as j:
        print('initialized connection')
        await j.pip_install('sklearn')
        print('pip installed sk')
        await j.send_module_recursive(testmod)
        print('installed local module')
        ab = j.run(c, 'a', 'b')
        print('-')
        obj = j.run(b)
        print('running')
        print(await ab)
        print(await obj)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()