import base64

from django.template import Library, Node, TemplateSyntaxError
from django.utils.html import strip_spaces_between_tags

register = Library()


@register.filter
def dict_get(dictionary, key):
    """
    Return the value for the given key or '' if not found.
    """
    return dictionary.get(key, '')


@register.simple_tag
def method(obj, method, *args, **kwargs):
    """
    Call an object method. {% method object method **kwargs %}
    """
    try:
        return getattr(obj, method)(*args, **kwargs)
    except Exception as exception:
        raise TemplateSyntaxError(
            'Error calling object method; {}'.format(exception)
        )


@register.simple_tag
def set(value):
    """
    Set a context variable to a specific value.
    """
    return value


@register.filter
def split(obj, separator):
    """
    Return a list of the words in the string, using sep as the delimiter
    string.
    """
    return obj.split(separator)


class SpacelessPlusNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context).strip()
        result = []
        for line in content.split('\n'):
            if line.strip() != '':
                result.append(line)

        return strip_spaces_between_tags(
            value='\n'.join(result)
        )


@register.tag
def spaceless_plus(parser, token):
    """
    Removes empty lines between the tag nodes.
    """
    nodelist = parser.parse(
        ('endspaceless_plus',)
    )
    parser.delete_first_token()
    return SpacelessPlusNode(nodelist=nodelist)


@register.filter
def to_base64(value, altchars=None):
    """
    Convert a value to base64 encoding. Accepts optional `altchars` argument.
    """
    if altchars:
        altchars = bytes(encoding='utf-8', source=altchars)
    return base64.b64encode(s=value, altchars=altchars).decode('utf-8')
