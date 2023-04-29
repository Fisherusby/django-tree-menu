import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.expressions import RawSQL
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import exceptions, reverse


def item_menu_url_validator(value: str):
    """Validated url value."""
    # for absolute url
    url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    # for path url
    url_pattern_2 = "^/\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"

    if bool(re.match(url_pattern, value)):
        return value

    if bool(re.match(url_pattern_2, value)):
        return value

    try:
        reverse(value)
    except exceptions.NoReverseMatch:
        raise ValidationError("this is not url")

    return value


class TreeMenu(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name}"


class TreeMenuItem(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="children"
    )

    url = models.CharField(
        max_length=255,
        validators=[
            item_menu_url_validator,
        ],
    )
    menu = models.ForeignKey(
        "TreeMenu", related_name="menu_tree_items", on_delete=models.CASCADE
    )
    left_value = models.IntegerField(default=-1, verbose_name="Order")
    right_value = models.IntegerField(default=-1)
    level = models.IntegerField(default=-1)

    __original_menu_id = None

    class Meta:
        unique_together = (
            "menu_id",
            "url",
        )
        ordering = ("menu_id", "left_value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # need for check to change or create object
        self.__original_parent_id = self.parent_id
        self.__original_pk = self.pk

    @property
    def full_name(self):
        if self.parent is None:
            return f"{self.name}"
        return f"{self.parent} > {self.name}"

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pk is None or self.parent_id != self.__original_parent_id:
            TreeMenuItem.rebuild_menu(self.menu_id)

    @classmethod
    def get_descendants(cls, node):
        """Returns a queryset of all descendants of a node using a single SELECT statement."""
        sql = """
            WITH RECURSIVE descendants(id, name, url, menu_id, parent_id) AS (
                SELECT id, name, url, menu_id, parent_id FROM {table} WHERE id = %s
                UNION ALL
                SELECT {table}.id, {table}.name, {table}.url, {table}.menu_id, {table}.parent_id FROM descendants
                JOIN {table} ON descendants.id = {table}.parent_id
            )
            SELECT id FROM descendants 
        """.format(
            table=cls._meta.db_table
        )

        return cls.objects.filter(id__in=RawSQL(sql, [node.id]))

    @classmethod
    def rebuild_menu(cls, menu_id):
        lft = 1
        level = 0
        # Get the root nodes
        root_obj = cls.objects.filter(parent=None, menu_id=menu_id)
        cls._build_menu_item(root_obj[0], lft, level, menu_id)

    @classmethod
    def _build_menu_item(cls, obj, lft, level, menu_id):
        obj.left_value = lft
        obj.menu_id = menu_id
        obj.level = level
        lft += 1
        level += 1
        rght = lft
        for child in obj.children.all().order_by("name"):
            rght = cls._build_menu_item(child, lft, level, menu_id)
            lft = rght + 1
        obj.right_value = rght
        obj.save()
        return rght + 1


@receiver(post_save, sender=TreeMenu)
def save_tree_menu(sender, instance, created, **kwargs):
    if created:
        # create root menu`s item for new menu
        root_item = TreeMenuItem(name=instance.name, menu=instance)
        root_item.save()
    else:
        # after change menu name have to change name for root menu item
        root_child = TreeMenuItem.objects.filter(menu=instance, parent__isnull=True)[0]
        root_child.name = instance.name
        root_child.save()
