from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_nav(context, pattern):
    """Return the string 'active' when the request path starts with pattern.

    Usage in template:
      {% load nav_tags %}
      <a class="nav-link {% active_nav '/vehicles/' %}" href="/vehicles/">Vehicles</a>
    """
    request = context.get('request')
    if not request:
        return ''
    path = request.path or ''
    try:
        # simple startswith check; pattern should include leading and trailing slash
        if path.startswith(pattern):
            return 'active'
    except Exception:
        return ''
    return ''


@register.simple_tag(takes_context=True)
def has_group(context, group_name):
    request = context.get('request')
    if not request:
        return False
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False
    try:
        return user.groups.filter(name=group_name).exists()
    except Exception:
        return False


@register.simple_tag(takes_context=True)
def is_service_center(context):
    request = context.get('request')
    if not request:
        return False
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_staff", False):
        return True
    try:
        if user.groups.filter(name="service_center").exists():
            return True
    except Exception:
        pass
    try:
        profile = user.profile  # type: ignore[attr-defined]
        return getattr(profile, "role", "") == "service_center"
    except Exception:
        return False
