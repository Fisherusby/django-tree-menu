import random
from tree_menu.models import TreeMenuItem, TreeMenu


def get_item_for_tree(deep_count: int = 5, prefix: str = 'Item '):
    siblings = []
    rnd_count = random.randrange(1, deep_count+1)
    for i in range(rnd_count):
        elem = chr(65+i)
        name = f'{prefix}{elem}'
        siblings.append(
            {
                'name': name,
                'url': f'/example/{name}',
                'child': get_item_for_tree(deep_count=deep_count-1, prefix=name) if deep_count > 1 else None
            }
        )
    return siblings


def make_child_items(root_item, menu_items):
    for item in menu_items:
        menu_item = TreeMenuItem(
            name=item['name'],
            url=item['url'],
            parent=root_item,
            menu=root_item.menu,
        )
        menu_item.save()
        if item['child'] is not None:
            make_child_items(menu_item, item['child'])


def make_menu_by_tree(menu_name, menu_items):
    tree_menu_model = TreeMenu(name=menu_name)
    tree_menu_model.save()
    root_item = TreeMenuItem.objects.filter(menu=tree_menu_model, parent__isnull=True)[0]
    make_child_items(root_item, menu_items)


def clear_all_menus():
    TreeMenu.objects.all().delete()


def gen_example_menus():
    clear_all_menus()
    menu_items_for_tree = get_item_for_tree()
    make_menu_by_tree('Example menu 1', menu_items_for_tree)

