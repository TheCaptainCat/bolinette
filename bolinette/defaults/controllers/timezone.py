from bolinette import data
from bolinette.decorators import controller, get
from bolinette.defaults.services import TimezoneService
from bolinette.utils import response


@controller('tz', '/tz')
class TimezoneController(data.Controller):
    @property
    def tz_service(self) -> TimezoneService:
        return self.context.service('tz')

    @get('')
    async def all_timezones(self, **_):
        return response.ok('OK', await self.tz_service.get_all())
