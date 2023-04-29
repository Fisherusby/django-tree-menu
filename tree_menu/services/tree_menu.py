from typing import List, Optional

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

    def _get_url(self) -> str:
        """Get path for current url."""
        return self.request.path_info

    def _get_absolute_url(self) -> str:
        """Get absolute current url."""
        return self.request.build_absolute_uri()

    def _get_url_name(self) -> Optional[str]:
        """Get url router name."""
        try:
            return resolve(self.request.path_info).url_name
        except Exception as e:
            print(e)
            return None

    def _get_queryset(self):
        """Get queryset for all menu`s items by menu name."""
        return TreeMenuItem.objects.filter(menu__name=self.menu_name)

    def __to_url(self, url: str) -> str:
        """Convert model`s named url to path url."""
        try:
            named_url = reverse(url)
            return named_url
        except exceptions.NoReverseMatch:
            return url

    def _query_to_family(self) -> (dict, Optional[int], Optional[TreeMenuItem]):
        """Generate relation dict for menu`s items, find head`s item and current menu`s item."""
        family: dict = {}
        head_item: Optional[int] = None
        current_item: Optional[TreeMenuItem] = None
        for obj in self._get_queryset():
            if family.get(obj.pk) is None:
                family[obj.pk]: dict = {"children": []}
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
                family[obj.parent_id]: dict = {"children": []}
            family[obj.parent_id]["children"].append(obj.pk)

            if obj.url is not None and obj.url in self.current_url:
                current_item = obj

        return family, head_item, current_item

    def _tree_for_render(self) -> Optional[list]:
        """Prepare tree before render."""
        if self.__head is None:
            return None

        return self._get_children(self.__head)

    def _get_children(self, menu_item_id) -> List[dict]:
        """Return list of sibling with at children."""
        result: list = []
        for child_id in self.__family[menu_item_id]["children"]:
            item_menu: dict = {
                "name": self.__family[child_id]["name"],
                "url": self.__family[child_id]["url"],
                "current": "current"
                if self.__current == self.__family[child_id]["obj"]
                else "",
            }
            if (
                AdminModelsItemMenuChoices.is_child(
                    self.__family[child_id]["obj"], self.__current
                )
                or self.__current == self.__family[child_id]["obj"]
            ):
                if len(self.__family[child_id]["children"]) > 0:
                    item_menu["children"]: list = self._get_children(child_id)
            result.append(item_menu)

        return result

    def __render_by_tree(
        self, for_render_tree: Optional[list], first: bool = True
    ) -> str:
        """Render tree to html code."""
        if first:
            ul_class = self.css_class_html
        else:
            ul_class = ""
        list_menu_items: str = ""
        for item_menu in for_render_tree:
            list_menu_items += self.menu_item_html.format(**item_menu)
            children: list = item_menu.get("children")
            if children is not None:
                list_menu_items += self.__render_by_tree(children, first=False)
        return self.list_menu_items_html.format(
            menu_items=list_menu_items, ul_class=ul_class
        )

    def render_menu(self) -> str:
        """Return tree menu html code."""
        if self.__head is None:
            return f"Tree menu &lt;{self.menu_name}&gt; not fount"

        for_render_tree: Optional[list] = self._tree_for_render()
        return self.__render_by_tree(for_render_tree)


class AdminModelsItemMenuChoices:
    def __init__(self, current_item: TreeMenuItem):
        self.current_item: TreeMenuItem = current_item
        self.menu_items_qs = TreeMenuItem.objects.select_related("menu").all()
        self.menu_items: dict = self.__items()

    @staticmethod
    def is_child(paren_obj: TreeMenuItem, child_obj: TreeMenuItem) -> bool:
        """Checks the relationship of objects."""
        if paren_obj is None or child_obj is None:
            return False
        return (
            paren_obj.left_value < child_obj.left_value
            and paren_obj.right_value > child_obj.right_value
            and paren_obj.menu_id == child_obj.menu_id
        )

    def __items(self) -> dict:
        """Create dict with all menu items.

        key: menu item id
        value: include obj and list of children
        """
        items: dict = {
            obj.id: {
                "obj": obj,
                "parent": obj.parent_id,
                "children": [],
            }
            for obj in self.menu_items_qs
        }

        for obj in self.menu_items_qs:
            if obj.parent_id is not None:
                items[obj.parent_id]["children"].append(obj.id)
        return items

    def __all_children(self, obj_id: int) -> list:
        """Return all children for menu item with children of children."""
        result: list = self.menu_items[obj_id]["children"]
        for c in self.menu_items[obj_id]["children"]:
            result.extend(self.__all_children(c))
        return result

    def __name_as_tree(self, obj: TreeMenuItem) -> str:
        """Return menu item as tree."""
        if obj.level == 0:
            return f"{obj.menu}"
        return f"{obj.level*'⠀⠀'}└─ {obj.name}"

    def choices(self) -> list:
        """Return list for choice parent without impossible parent."""
        result: list = [
            ("", "-----------"),
        ]
        for obj in self.menu_items_qs:
            if not self.is_child(self.current_item, obj) and self.current_item != obj:
                result.append((obj.id, self.__name_as_tree(obj)))
        return result
