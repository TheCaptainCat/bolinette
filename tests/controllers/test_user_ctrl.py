from bolinette import blnt
from bolinette.testing import client, bolitest, Mock, Mocked
from tests import utils


def _fix_mocked_user(user: Mocked):
    user.fields.timezone = 'Europe/Paris'


async def set_up(_, mock: Mock):
    utils.user.salt_password(mock(1, 'user')).insert()


async def admin_set_up(context: blnt.BolinetteContext, mock: Mock):
    admin = Mocked.insert_entity(context, 'role', {'name': 'admin'})
    user1 = utils.user.salt_password(mock(1, 'user')).insert()
    user1.roles.append(admin)
    utils.user.salt_password(mock(2, 'user')).insert()
    mock(1, 'role').insert()


async def root_set_up(context: blnt.BolinetteContext, mock: Mock):
    root = Mocked.insert_entity(context, 'role', {'name': 'root'})
    admin = Mocked.insert_entity(context, 'role', {'name': 'admin'})
    user1 = utils.user.salt_password(mock(1, 'user')).insert()
    user1.roles.append(root)
    user1.roles.append(admin)


@bolitest(before=set_up)
async def test_login_failed(client):
    user1 = client.mock(1, 'user')

    rv = await client.post('/user/login', {'username': user1.fields.username,
                                           'password': user1.fields.password[:-1]})
    assert rv['code'] == 401
    assert 'user.login.wrong_credentials' in rv['messages']

    rv = await client.post('/user/login', {'username': user1.fields.username + "2",
                                           'password': user1.fields.password})
    assert rv['code'] == 401
    assert 'user.login.wrong_credentials' in rv['messages']


@bolitest(before=set_up)
async def test_login(client):
    user1 = client.mock(1, 'user')

    rv = await client.post('/user/login', user1.to_payload('login'))
    assert rv['code'] == 200


@bolitest(before=set_up)
async def test_access_user_info_failed(client):
    rv = await client.get('/user/me')
    assert rv['code'] == 401


@bolitest(before=set_up)
async def test_access_user_info(client):
    user1 = client.mock(1, 'user')

    await client.post('/user/login', user1.to_payload('login'))

    rv = await client.get('/user/me')
    assert rv['code'] == 200
    assert rv['data'].get('username') == user1.fields.username
    assert rv['data'].get('email') == user1.fields.email
    assert rv['data'].get('password') is None


@bolitest(before=set_up)
async def test_logout(client):
    user1 = client.mock(1, 'user')

    await client.post('/user/login', user1.to_payload('login'))

    rv = await client.get('/user/me')
    assert rv['code'] == 200

    rv = await client.post('/user/logout')
    assert rv['code'] == 200

    rv = await client.get('/user/me')
    assert rv['code'] == 401


@bolitest(before=set_up)
async def test_register(client):
    user2 = client.mock(2, 'user', post_mock_fn=_fix_mocked_user)

    rv = await client.post('/user/register', user2.to_payload('register'))
    assert rv['code'] == 201

    rv = await client.post('/user/login', user2.to_payload('login'))
    assert rv['code'] == 200


@bolitest(before=set_up)
async def test_logged_in_after_register(client):
    user2 = client.mock(2, 'user', post_mock_fn=_fix_mocked_user)

    rv = await client.post('/user/register', user2.to_payload('register'))
    assert rv['code'] == 201

    rv = await client.get('/user/me')
    assert rv['code'] == 200
    assert rv['data'].get('username') == user2.fields.username
    assert rv['data'].get('email') == user2.fields.email


@bolitest(before=set_up)
async def test_register_bad_request(client):
    rv = await client.post('/user/register', {})
    assert rv['code'] == 400
    assert 'param.required:username' in rv['messages']
    assert 'param.required:password' in rv['messages']
    assert 'param.required:email' in rv['messages']


@bolitest(before=set_up)
async def test_register_conflict(client):
    user1 = client.mock(1, 'user', post_mock_fn=_fix_mocked_user)

    rv = await client.post('/user/register', user1.to_payload('register'))
    assert rv['code'] == 409
    assert f'param.conflict:username:{user1.fields.username}' in rv['messages']
    assert f'param.conflict:email:{user1.fields.email}' in rv['messages']


@bolitest(before=set_up)
async def test_change_username(client):
    user1 = client.mock(1, 'user')

    await client.post('/user/login', user1.to_payload('login'))

    rv = await client.patch('/user/me', {'username': 'new_username'})
    assert rv['code'] == 200
    assert rv['data']['username'] == 'new_username'
    assert rv['data']['email'] == user1.fields.email


@bolitest(before=set_up)
async def test_change_password(client):
    user1 = client.mock(1, 'user')

    await client.post('/user/login', user1.to_payload('login'))
    await client.patch('/user/me', {'password': 'new_password'})
    await client.post('/user/logout')
    await client.post('/user/login', {'username': user1.fields.username, 'password': 'new_password'})

    rv = await client.get('/user/me')
    assert rv['code'] == 200


@bolitest(before=admin_set_up)
async def test_get_users(client):
    user1 = client.mock(1, 'user')

    await client.post('/user/login', user1.to_payload('login'))

    rv = await client.get('/user')
    assert rv['code'] == 200
    assert len(rv['data']) == 2


@bolitest(before=admin_set_up)
async def test_get_users_forbidden(client):
    user1 = client.mock(2, 'user')

    await client.post('/user/login', user1.to_payload('login'))

    rv = await client.get('/user')
    assert rv['code'] == 403
    assert 'user.forbidden:admin' in rv['messages']


@bolitest(before=admin_set_up)
async def test_add_self_role(client):
    user1 = client.mock(1, 'user')
    role1 = client.mock(1, 'role')

    await client.post('/user/login', user1.to_payload('login'))

    rv = await client.post(f'/user/{user1.fields.username}/roles', role1.to_payload())
    assert rv['code'] == 201
    assert f'user.roles.added:{user1.fields.username}:{role1.fields.name}' in rv['messages']


@bolitest(before=admin_set_up)
async def test_add_role_not_admin(client):
    user2 = client.mock(2, 'user')
    role1 = client.mock(1, 'role')

    await client.post('/user/login', user2.to_payload('login'))

    rv = await client.post(f'/user/{user2.fields.username}/roles', role1.to_payload())
    assert rv['code'] == 403
    assert f'user.forbidden:admin' in rv['messages']


@bolitest(before=admin_set_up)
async def test_remove_role(client):
    user1 = client.mock(1, 'user')
    role1 = client.mock(1, 'role')

    await client.post('/user/login', user1.to_payload('login'))
    await client.post(f'/user/{user1.fields.username}/roles', role1.to_payload())

    rv = await client.delete(f'/user/{user1.fields.username}/roles/{role1.fields.name}')
    assert rv['code'] == 200
    assert f'user.roles.removed:{user1.fields.username}:{role1.fields.name}' in rv['messages']


@bolitest(before=admin_set_up)
async def test_remove_role_not_found(client):
    user1 = client.mock(1, 'user')

    await client.post('/user/login', user1.to_payload('login'))

    rv = await client.delete(f'/user/{user1.fields.username}/roles/unknown_role')
    assert rv['code'] == 404
    assert f'entity.not_found:role:name:unknown_role' in rv['messages']


@bolitest(before=admin_set_up)
async def test_remove_role_not_in_user_roles(client):
    user1 = client.mock(1, 'user')
    role1 = client.mock(1, 'role')

    await client.post('/user/login', user1.to_payload('login'))

    rv = await client.delete(f'/user/{user1.fields.username}/roles/{role1.fields.name}')
    assert rv['code'] == 400
    assert f'user.roles.not_found:{user1.fields.username}:{role1.fields.name}' in rv['messages']


@bolitest(before=admin_set_up)
async def test_no_self_demotion(client):
    user1 = client.mock(1, 'user')

    await client.post('/user/login', user1.to_payload('login'))

    rv = await client.delete(f'/user/{user1.fields.username}/roles/admin')
    assert rv['code'] == 403
    assert f'role.admin.no_self_demotion' in rv['messages']


@bolitest(before=root_set_up)
async def test_root_self_demotion(client):
    user1 = client.mock(1, 'user')

    await client.post('/user/login', user1.to_payload('login'))

    rv = await client.delete(f'/user/{user1.fields.username}/roles/admin')
    assert rv['code'] == 200
    assert f'user.roles.removed:{user1.fields.username}:admin' in rv['messages']
