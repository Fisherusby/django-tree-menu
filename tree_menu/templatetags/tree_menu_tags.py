from django import template

from ..services.tree_menu import TreeMenu

register = template.Library()


@register.inclusion_tag(filename="tree_menu.html", name="draw_menu", takes_context=True)
def draw_menu(context, menu_name):
    tree_menu = TreeMenu(menu_name, context.request)

    return {
        "tree_menu": tree_menu.render_menu(),
        "menu_name": menu_name,
    }
