

def singleton(clazz):
    instances = {}
    def get_instance(*args, **kwargs):
        key = (clazz, args)
        if key not in instances:
            instances[key] = clazz(*args, **kwargs)
        return instances[key]
    return get_instance



