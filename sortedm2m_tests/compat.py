def m2m_set(instance, field_name, objs):
    getattr(instance, field_name).set(objs)
