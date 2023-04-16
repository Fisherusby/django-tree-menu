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
        # return TreeMenuItem.objects.filter(menu__name=self.menu_name).prefetch_related('childs')

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
                family[obj.pk] = {"child": []}
            family[obj.pk].update(
                {
                    "parent": obj.parent_id,
                    "name": obj.name,
                    "url": self.__to_url(obj.url),
                }
            )

            if obj.parent_id is None:
                head_item = obj.pk

            if family.get(obj.parent_id) is None:
                family[obj.parent_id] = {"child": []}
            family[obj.parent_id]["child"].append(obj.pk)

            if obj.url is not None and obj.url in self.current_url:
                current_item = obj.pk

        def get_all_child_with_grandchild(item_id):
            """Create all child`s child list."""
            family[item_id]["all_child"] = []
            for child_id in family[item_id]["child"]:
                family[item_id]["all_child"].append(child_id)
                family[item_id]["all_child"].extend(
                    get_all_child_with_grandchild(child_id)
                )
            return family[item_id]["all_child"]

        if head_item is not None:
            get_all_child_with_grandchild(head_item)

        return family, head_item, current_item

    def _tree_for_render(self):
        """Prepare tree before render."""
        if self.__head is None:
            return None

        return self._get_child(self.__head)

    def _get_child(self, menu_item):
        """Return list of sibling with they child."""
        result = []
        for child_id in self.__family[menu_item]["child"]:
            item_menu = {
                "name": self.__family[child_id]["name"],
                "url": self.__family[child_id]["url"],
                "current": "current" if self.__current == child_id else "",
            }
            if (
                self.__current in self.__family[child_id]["all_child"]
                or self.__current == child_id
            ):
                if len(self.__family[child_id]["child"]) > 0:
                    item_menu["child"] = self._get_child(child_id)
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
            child = item_menu.get("child")
            if child is not None:
                list_menu_items += self.__render_by_tree(child, first=False)
        return self.list_menu_items_html.format(
            menu_items=list_menu_items, ul_class=ul_class
        )

    def render_menu(self):
        """Return tree menu html code."""
        if self.__head is None:
            return f"Tree menu &lt;{self.menu_name}&gt; not fount"

        for_render_tree = self._tree_for_render()
        return self.__render_by_tree(for_render_tree)
