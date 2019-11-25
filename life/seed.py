from model.profile import Profile


class Seed(object):

    @classmethod
    async def profiles(cls):
        administrator = Profile({
            'username': 'admin',
            'password': 'admin',
            'email': 'administrator@domain.com',
            'name': {
                'first': 'administrator'
            }
        })
        await administrator.save()
