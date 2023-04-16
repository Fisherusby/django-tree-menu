from django.contrib import admin
from .models import TreeMenuItem, TreeMenu
from django import forms


def choice_parents_list(cur_obj=None):
    childs = {}
    queryset = TreeMenuItem.objects.all()
    for obj in queryset:
        if obj.parent is not None:
            if childs.get(obj.parent.pk) is None:
                childs[obj.parent.pk] = []
            childs[obj.parent.pk].append(obj.pk)

    def get_childs(iam: int):
        result = childs.get(iam)
        if result is None:
            return []
        childs_child = []
        for c_id in result:
            c_c = get_childs(c_id)
            childs_child.extend(c_c)
        result.extend(childs_child)
        return result

    exclude_child_list = []
    if cur_obj is not None:
        exclude_child_list = get_childs(cur_obj.pk)
        exclude_child_list.append(cur_obj.pk)

    return exclude_child_list


class TreeMenuItemsFormAdmin(forms.ModelForm):
    def clean_parent(self):
        if self.data['parent'] == '':
            raise forms.ValidationError('This field is required.')
        return self.cleaned_data['parent']


class TreeMenuItemsAdmin(admin.ModelAdmin):
    list_filter = (
        "menu",
    )
    search_fields = ("name__startswith",)
    fields = ('name', 'url', 'parent')
    list_display = ("full_name", "url")

    # ordering = ('full_name')
    form = TreeMenuItemsFormAdmin

    def save_model(self, request, obj, form, change):
        obj.menu = obj.parent.menu
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(parent__isnull=False)
        return qs

    def render_change_form(self, request, context, *args, **kwargs):
        exclude_child_list = choice_parents_list(kwargs.get('obj'))
        context['adminform'].form.fields['parent'].queryset = context['adminform'].form.fields[
                    'parent'].queryset.exclude(id__in=exclude_child_list)
        return super().render_change_form(request, context, *args, **kwargs)


admin.site.register(TreeMenu)
admin.site.register(TreeMenuItem, TreeMenuItemsAdmin)
