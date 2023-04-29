from django import forms
from django.contrib import admin
from .models import TreeMenu, TreeMenuItem
from .services import AdminModelsItemMenuChoices


class TreeMenuItemsFormAdmin(forms.ModelForm):
    def clean_parent(self):
        if self.data["parent"] == "":
            raise forms.ValidationError("This field is required.")
        return self.cleaned_data["parent"]


class TreeMenuItemsAdmin(admin.ModelAdmin):
    list_filter = ("menu",)
    search_fields = ("name__startswith",)
    fields = ("name", "url", "parent")
    list_display = ('list_name', '_menu', "_url", '_level')

    form = TreeMenuItemsFormAdmin

    def list_name(self, obj):
        if obj.level == 1:
            return f'{obj.name}'
        return f"{(obj.level-1)*'⠀⠀⠀'}└── {obj.name}"

    list_name.admin_order_field = None

    def _url(self, obj):
        return obj.url
    _url.admin_order_field = None

    def _menu(self, obj):
        return obj.menu
    _menu.admin_order_field = None

    def _level(self, obj):
        return obj.level
    _level.admin_order_field = None

    def _level(self, obj):
        return obj.level
    _level.admin_order_field = None

    def save_model(self, request, obj, form, change):
        # Set obj`s menu from parent
        obj.menu = obj.parent.menu
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=False).select_related('menu')

    def render_change_form(self, request, context, *args, **kwargs):

        menu_item_choicer = AdminModelsItemMenuChoices(kwargs.get("obj"))
        choices = menu_item_choicer.choices()

        context["adminform"].form.fields["parent"].queryset = TreeMenuItem.objects.none()
        context["adminform"].form.fields["parent"].choices = choices

        return super().render_change_form(request, context, *args, **kwargs)





admin.site.register(TreeMenu)
admin.site.register(TreeMenuItem, TreeMenuItemsAdmin)
