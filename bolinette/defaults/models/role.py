from bolinette import mapping, types, data
from bolinette.decorators import model


@model('role')
class Role(data.Model):
    id = types.Column(types.Integer, primary_key=True)
    name = types.Column(types.String, unique=True, nullable=False)

    @classmethod
    def payloads(cls):
        yield [
            mapping.Column(cls.name, required=True)
        ]

    @classmethod
    def responses(cls):
        yield [
            mapping.Column(cls.name)
        ]
        yield 'complete', [
            mapping.Column(cls.name),
            mapping.List(mapping.Definition('user'), key='users')
        ]