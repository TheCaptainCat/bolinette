from bolinette.testing import bolitest
# noinspection PyUnresolvedReferences
from bolinette.testing.fixture import client
from tests import utils
# noinspection PyUnresolvedReferences
import example.models


@bolitest(before=utils.book.set_up)
async def test_get_person(client):
    person1 = client.mock(1, 'person')

    rv = await client.get(f'/person/{person1["uid"]}')
    person1_res = person1.to_response()
    assert rv['code'] == 200
    assert rv['data']['first_name'] == person1_res['first_name']
    assert rv['data']['last_name'] == person1_res['last_name']
    assert rv['data']['full_name'] == person1_res['full_name']
    assert len(rv['data']['books']) == 2
