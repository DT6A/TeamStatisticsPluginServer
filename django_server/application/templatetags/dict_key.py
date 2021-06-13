from django.template.defaultfilters import register

@register.filter(name='dict_key')
def dict_key(d, k):
    if k not in d:
        return 0
    '''Returns the given key from a dictionary.'''
    return d[k]