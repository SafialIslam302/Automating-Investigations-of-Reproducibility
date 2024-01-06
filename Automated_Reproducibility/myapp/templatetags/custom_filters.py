from django import template

register = template.Library()


@register.filter
def cycle_colors(value, colors):
    return colors[value % len(colors)]
