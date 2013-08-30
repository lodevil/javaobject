from .field import BaseField
from collections import OrderedDict
from . import consts


class JavaClassMeta(type):
    def __prepare__(name, bases):
        return OrderedDict()

    def __new__(self, name, bases, clsdict):
        if '__javaclass__' not in clsdict:
            raise TypeError('missing __javaclass__')

        fields = OrderedDict()
        for key, field in clsdict.items():
            if isinstance(field, BaseField):
                fields[key] = field
                clsdict[key] = field.default
        clsdict['__fields__'] = fields
        if '__suid__' not in clsdict:
            clsdict['__suid__'] = 0

        if '__classflag__' in clsdict and clsdict['__classflag__'] > 0xFF:
            raise TypeError('invalid class flag: 0x%X' % clsdict['__classflag__'])

        cls = type.__new__(self, name, bases, clsdict)
        cls._classes[clsdict['__javaclass__']] = cls
        return cls


class JavaClass(metaclass=JavaClassMeta):
    _classes = {}
    __javaclass__ = 'Java'

    class InvalidClass(Exception):
        pass

    @classmethod
    def resolve(cls, name):
        if name[0] == 'L' and name[-1] == ';':
            name = name[1:-1]
            if name.find('.') == -1:
                name = name.replace('/', '.')
        rst = cls._classes.get(name, None)
        if rst is None:
            raise cls.InvalidClass('can\'t find %r' % name)
        return rst

    @classmethod
    def signature(cls):
        return 'L%s;' % cls.__javaclass__.replace('.', '/')