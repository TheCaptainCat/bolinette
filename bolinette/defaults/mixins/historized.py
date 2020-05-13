from bolinette import mapping, types, data
from bolinette.decorators import mixin


@mixin('historized')
class Historized(data.Mixin):
    @staticmethod
    def columns():
        return {
            'created_on': types.Column(types.Date),
            'updated_on': types.Column(types.Date),
            'created_by_id': types.Column(types.Integer, reference=types.Reference('user', 'id')),
            'updated_by_id': types.Column(types.Integer, reference=types.Reference('user', 'id'))
        }

    @staticmethod
    def relationships(model_cls):
        return {
            'created_by': types.Relationship('user', foreign_key=model_cls.created_by_id, lazy=False),
            'updated_by': types.Relationship('user', foreign_key=model_cls.updated_by_id, lazy=False)
        }

    @staticmethod
    def response(model_cls):
        return [
            mapping.Column(model_cls.created_on),
            mapping.Column(model_cls.updated_on),
            mapping.Reference(model_cls.created_by),
            mapping.Reference(model_cls.updated_by),
        ]