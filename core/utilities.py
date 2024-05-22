async def proxy_add_value(state, key, value):
    async with state.proxy() as data:
        data[key] = value


async def proxy_get_value(state, key):
    async with state.proxy() as data:
        return data[key]


async def proxy_get_all(state):
    async with state.proxy() as data:
        return data.as_dict()
