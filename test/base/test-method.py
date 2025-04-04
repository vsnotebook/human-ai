# class Web1(object):
#     # 静态变量（类变量）
#     name = "Python_Web"
#
#     @staticmethod
#     def foo_staticmethod():
#         """静态方法"""
#         # 引用静态变量
#         # print(name)
#         print(Web1.name)
#
#

class Web(object):
    # 静态变量（类变量）
    name = "Python_Web"

    # 类方法
    @classmethod
    def foo_classmethod_other(cls):
        print('类方法被调用！')

    # 另外一个静态方法
    @staticmethod
    def foo_staticmethod_other():
        print('另外一个静态方法被调用！')

    @staticmethod
    def foo_staticmethod():
        """静态方法"""
        # 调用其他静态方法
        print(Web.foo_staticmethod_other())

        # 调用类方法
        print(Web.foo_classmethod_other())


if __name__ == '__main__':
    # 直接使用类名+方法名调用
    Web.foo_staticmethod()
    # 实例化一个对象
    instance = Web()

    # 使用实例对象去调用静态方法（不建议）
    instance.foo_staticmethod()

    print(Web.name)

