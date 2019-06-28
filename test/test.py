import asyncio
from remotejob import RemoteJob

import test_module

async def main():
    print('1. initialize connection')
    with RemoteJob() as j:
        print('2. pip install remotejob')
        assert 0 == await j.pip_install('remotejob')
        print('3. install local module')
        assert None == await j.send_module_recursive(test_module)
        print('4. som')
        assert 3 == await j.run(test_module.sum, 1, 2)
        print('5. return class instance')
        assert test_module.test_class_init == type(await j.run(test_module.test_class_init))
        print('6. submodule class method')
        d = test_module.sub_module.d.test_class_d()
        assert 'd' == await j.run(d.val)
        print('7. remove container')
    print('done all good')
    
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()