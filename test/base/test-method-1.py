class Web(object):
    def __init__(self):
        self.desc = "实例属性，不共享"

    def norm_method(self):
        """普通方法"""
        print('普通方法被调用！')

    @staticmethod
    def foo_staticmethod():
        """静态方法"""
        instance = Web()

        # 获取实例属性
        print(instance.desc)

        # 调用普通方法
        instance.norm_method()


if __name__ == '__main__':
    # 直接使用类名+方法名调用
    Web.foo_staticmethod()
    # 实例化一个对象
    instance = Web()

    # 使用实例对象去调用静态方法（不建议）
    instance.foo_staticmethod()

    # print(Web.name)


