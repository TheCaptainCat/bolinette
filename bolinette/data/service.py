from datetime import datetime

from bolinette import core, data, utils
from bolinette.exceptions import EntityNotFoundError


class Service:
    def __init__(self, name, context: 'core.BolinetteContext'):
        self.name = name
        self.context = context
        self.repo: data.Repository = context.repo(name)

    def __repr__(self):
        return f'<Service {self.name}>'

    async def get(self, identifier, *, safe=False, **_):
        entity = await self.repo.get(identifier)
        if entity is None and not safe:
            raise EntityNotFoundError(model=self.name, key='id', value=identifier)
        return entity

    async def get_by(self, key, value, **_):
        return await self.repo.get_by(key, value)

    async def get_first_by(self, key, value, *, safe=False, **_):
        entity = await self.repo.get_first_by(key, value)
        if entity is None and not safe:
            raise EntityNotFoundError(model=self.name, key=key, value=value)
        return entity

    async def get_all(self, pagination=None, order_by=None, **_):
        if order_by is None:
            order_by = []
        query = self.repo.query
        if len(order_by) > 0:
            query = await self._build_order_by(self.model, query, order_by)
        if pagination is not None:
            return await self._paginate(query, pagination)
        return query.all()

    async def create(self, values, **_):
        return await self.repo.create(values)

    async def update(self, entity, values, **_):
        return await self.repo.update(entity, values)

    async def patch(self, entity, values, **_):
        return await self.repo.patch(entity, values)

    async def delete(self, entity, **_):
        return await self.repo.delete(entity)

    @staticmethod
    async def _build_order_by(model, query, params):
        order_by_query = []
        for col_name, way in params:
            if hasattr(model, col_name):
                column = getattr(model, col_name)
                if way:
                    order_by_query.append(column)
                else:
                    order_by_query.append(data.functions.desc(column))
        return query.order_by(*order_by_query)

    @staticmethod
    async def _paginate(query, pagination):
        page = pagination['page']
        per_page = pagination['per_page']
        total = query.count()
        items = query.offset(page * per_page).limit(per_page).all()
        return utils.Pagination(items, page, per_page, total)


class HistorizedService(Service):
    def __init__(self, name, context: 'core.BolinetteContext'):
        super().__init__(name, context)

    async def create(self, values, *, current_user=None, **_):
        if current_user:
            now = datetime.utcnow()
            values['created_on'] = now
            values['created_by_id'] = current_user.id
            values['updated_on'] = now
            values['updated_by_id'] = current_user.id
        return await super().create(values, **_)

    async def update(self, entity, values, *, current_user=None, **_):
        if current_user:
            now = datetime.utcnow()
            values['created_on'] = entity.created_on
            values['created_by_id'] = entity.created_by_id
            values['updated_on'] = now
            values['updated_by_id'] = current_user.id
        return await super().update(entity, values, **_)

    async def patch(self, entity, values, *, current_user=None, **_):
        if current_user:
            now = datetime.utcnow()
            values['updated_on'] = now
            values['updated_by_id'] = current_user.id
        return await super().patch(entity, values, **_)