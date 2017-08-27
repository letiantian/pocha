"""
pocha test discovery module responsible for creating a dictionary containing the
testing hierarchy as represented by the underlying tests.

"""
import os
import imp
import sys

from collections import OrderedDict

from pocha import common


def __load_modules(path):
    modules = []

    if os.path.isfile(path) and path.endswith('.py'):
        modules.append(path)

    elif os.path.isdir(path):
        # we do recursively attempt to find tests in a directory that contains
        # the pocha.ignore file in it
        if os.path.exists(os.path.join(path, 'pocha.ignore')):
            return modules

        for filename in os.listdir(path):
            modules += __load_modules(os.path.join(path, filename))

    return modules

class FalseyDict(dict):

    def __init__(self, dictionary):
        self.dict = dictionary

    def __getitem__(self, key):

        if key in self.dict.keys():
            return self.dict[key]

        else:
            # by returning False the evaluation can happen for tags that
            # are not defined
            return False


def filter_tests(tests, expression):
    filtered_tests = OrderedDict()

    for (key, thing) in tests.items():
        if thing.only:
            return OrderedDict({
                thing.name: thing
            })

        if thing.type == 'test':
            if expression is None:
                filtered_tests[key] = thing
                continue

            global_tags = FalseyDict(thing.tags)

            if eval(expression, global_tags):
                filtered_tests[key] = thing

        elif thing.type == 'suite':
            thing.tests = filter_tests(thing.tests, expression)
                
            if len(thing.tests) != 0:
                filtered_tests[key] = thing

    return filtered_tests


def search(path, expression):
    modules = __load_modules(path)

    # load each module and then we'll have a complete list of the tests
    # to run
    for module in modules:
        cur_dir = os.getcwdu()
        module = module.replace('/', os.path.sep).replace('\\', os.path.sep)
        abs_path = os.path.abspath(os.path.join(cur_dir, module)).replace('/', os.path.sep).replace('\\', os.path.sep)
        abs_dir = os.path.dirname(abs_path)
        file_name = os.path.basename(abs_path)
        module_name = file_name.replace('.py', '').replace('.pyc', '').replace('.pyo', '')
        path_list = abs_path.split(os.path.sep)
        if len(path_list) < 1 or not path_list[-1].endswith('.py') or len(path_list[-1]) < 4:
            continue
        path_list[-1] = path_list[-1][:-3]
        # print '** ', path_list
        for pos in xrange(len(path_list)-1, -1, -1):
            
            _path = os.path.sep.join(path_list[0:pos+1])
            _real_module = '.'.join(path_list[pos+1:])
            if _path == '' or _path is None:
                _path = os.path.sep
            if _real_module == '' or _real_module is None:
                continue
            print '## path: {}, module: {}'.format(_path, _real_module)
            try:
                if _real_module in sys.modules:
                    del sys.modules[_real_module] 
                sys.path.insert(0, _path)
                __import__(_real_module)
                break
            except ImportError as e:
                raise e
            except Exception as e:
                raise e
            finally:
                sys.path.remove(_path)
        
        # print '--module: ', module, os.getcwdu(), abs_dir, file_name, module_name, expression, path_list
        # foo = imp.load_source('foo', module)
    print common.TESTS
    # print  '--lala: ', filter_tests(common.TESTS, expression)
    return filter_tests(common.TESTS, expression)