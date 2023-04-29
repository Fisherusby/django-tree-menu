from django.urls import exceptions, resolve, reverse

from ..models import TreeMenuItem


class TreeMenu:
    menu_item_html = '<li><span class="{current}"><a href="{url}">{name}</a></span>'
    list_menu_items_html = "<ul {ul_class}>{menu_items}</ul>"
    css_class_html = 'class="wtree"'

    def __init__(self, menu_name, request):
        self.menu_name = menu_name
        self.request = request
        self.current_url = [
            self._get_url(),
            self._get_absolute_url(),
            self._get_url_name(),
        ]
        self.current_url_name = self._get_url_name()
        self.__family, self.__head, self.__current = self._query_to_family()

    def _get_url(self):
        """Get path for current url."""
        return self.request.path_info

    def _get_absolute_url(self):
        """Get absolute current url."""
        return self.request.build_absolute_uri()

    def _get_url_name(self):
        """Get url router name."""
        try:
            return resolve(self.request.path_info).url_name
        except Exception as e:
            print(e)
            return None

    def _get_queryset(self):
        """Get queryset for all menu`s items by menu name."""
        return TreeMenuItem.objects.filter(menu__name=self.menu_name)

    def __to_url(self, url: str):
        """Convert model`s named url to path url."""
        try:
            named_url = reverse(url)
            return named_url
        except exceptions.NoReverseMatch:
            return url

    def _query_to_family(self):
        """Generate relation dict for menu`s items, find head`s item and current menu`s item."""
        family = {}
        head_item = None
        current_item = None
        for obj in self._get_queryset():
            if family.get(obj.pk) is None:
                family[obj.pk] = {"children": []}
            family[obj.pk].update(
                {
                    "parent": obj.parent_id,
                    "name": obj.name,
                    "obj": obj,
                    "url": self.__to_url(obj.url),
                }
            )

            if obj.parent_id is None:
                head_item = obj.pk

            if family.get(obj.parent_id) is None:
                family[obj.parent_id] = {"children": []}
            family[obj.parent_id]["children"].append(obj.pk)

            if obj.url is not None and obj.url in self.current_url:
                current_item = obj

        return family, head_item, current_item

    def _tree_for_render(self):
        """Prepare tree before render."""
        if self.__head is None:
            return None

        return self._get_children(self.__head)

    def _get_children(self, menu_item_id):
        """Return list of sibling with at children."""
        result = []
        for child_id in self.__family[menu_item_id]["children"]:
            item_menu = {
                "name": self.__family[child_id]["name"],
                "url": self.__family[child_id]["url"],
                "current": "current" if self.__current == self.__family[child_id]['obj'] else "",
            }
            if (
                AdminModelsItemMenuChoices.is_child(
                    self.__family[child_id]['obj'],
                    self.__current
                )
                or self.__current == self.__family[child_id]['obj']
            ):
                if len(self.__family[child_id]["children"]) > 0:
                    item_menu["children"] = self._get_children(child_id)
            result.append(item_menu)

        return result

    def __render_by_tree(self, for_render_tree, first: bool = True):
        """Render tree to html code."""
        if first:
            ul_class = self.css_class_html
        else:
            ul_class = ""
        list_menu_items = ""
        for item_menu in for_render_tree:
            list_menu_items += self.menu_item_html.format(**item_menu)
            children = item_menu.get("children")
            if children is not None:
                list_menu_items += self.__render_by_tree(children, first=False)
        return self.list_menu_items_html.format(
            menu_items=list_menu_items, ul_class=ul_class
        )

    def render_menu(self):
        """Return tree menu html code."""
        if self.__head is None:
            return f"Tree menu &lt;{self.menu_name}&gt; not fount"

        for_render_tree = self._tree_for_render()
        return self.__render_by_tree(for_render_tree)


class AdminModelsItemMenuChoices:
    def __init__(self, current_item):
        self.current_item = current_item
        self.menu_items_qs = TreeMenuItem.objects.select_related('menu').all()
        self.menu_items = self.__items()

    @staticmethod
    def is_child(paren_obj, child_obj):
        if paren_obj is None or child_obj is None:
            return False
        return (
                paren_obj.left_value < child_obj.left_value
                and paren_obj.right_value > child_obj.right_value
                and paren_obj.menu_id == child_obj.menu_id
        )

    def __items(self):
        items = {
            obj.id: {
                'obj': obj,
                'parent': obj.parent_id,
                'children': [],
            }
            for obj in self.menu_items_qs
        }

        for obj in self.menu_items_qs:
            if obj.parent_id is not None:
                items[obj.parent_id]['children'].append(obj.id)
        return items

    def __all_children(self, obj_id):
        result = self.menu_items[obj_id]['children']
        for c in self.menu_items[obj_id]['children']:
            result.extend(self.__all_children(c))
        return result

    def __full_name(self, menu_item_id):
        if self.menu_items[menu_item_id]['parent'] is None:
            return f"{self.menu_items[menu_item_id]['obj'].menu.name}"
        else:
            parent_name = self.__full_name(self.menu_items[menu_item_id]['parent'])
            return f"{parent_name} > {self.menu_items[menu_item_id]['obj'].name}"

    def __name_as_tree(self, obj):
        if obj.level == 0:
            return f'{obj.menu}'
        return f"{obj.level*'⠀⠀'}└─ {obj.name}"

    def choices(self):
        result = [('', '-----------'), ]
        for obj in self.menu_items_qs:
            if not self.is_child(self.current_item, obj) and self.current_item != obj:
                result.append(
                    (obj.id, self.__name_as_tree(obj))
                )
        # return sorted(result, key=lambda o: o[1])
        return result
