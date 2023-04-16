from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.urls import reverse, exceptions
import re


def item_menu_url_validator(value: str):

    url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
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
        return f'{self.name}'


class TreeMenuItem(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='childs')

    url = models.CharField(max_length=255, validators=[item_menu_url_validator,])
    menu = models.ForeignKey('TreeMenu', related_name='menu_tree_items', on_delete=models.CASCADE)
    # position = models.IntegerField(null=True, blank=True, default=None)

    __original_menu_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_menu_id = self.menu_id

    class Meta:
        unique_together = ('menu_id', 'url',)

    @property
    def full_name(self):
        if self.parent is None:
            return f'{self.name}'
        return f'{self.parent} - {self.name}'

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.__original_menu_id != self.menu_id and self.pk is not None:
            for child in self.childs.all():
                child.menu_id = self.menu_id
                child.save()

        # if self.position is None:
        #     all_sibling = TreeMenuItem.objects.filter(parent=self.parent)
        #     self.position = all_sibling.count() + 1

        super().save(*args, **kwargs)


@receiver(post_save, sender=TreeMenu)
def save_tree_menu(sender, instance, created, **kwargs):
    if created:
        root_item = TreeMenuItem(name=instance.name, menu=instance)
        root_item.save()
    else:
        root_child = TreeMenuItem.objects.filter(menu=instance, parent__isnull=True)[0]
        root_child.name = instance.name
        root_child.save()
