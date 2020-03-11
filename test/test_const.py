import importlib.machinery
import os

filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '_const_demo.py')

loader = importlib.machinery.SourceFileLoader('const_demo', filename)
const_demo = loader.load_module()


def test_const():
    # 变量只能被赋值一次
    const_demo.B = 2
    try:
        const_demo.B = 3
    except const_demo.ConstError:
        pass
    else:
        raise Exception('ConstError is expected')

    # module中赋值的变量能够被自动加载
    assert const_demo.A == 2
    try:
        const_demo.A = 2
    except const_demo.ConstError:
        pass
    else:
        raise Exception('ConstError is expected')
    assert not hasattr(const_demo, 'b')
