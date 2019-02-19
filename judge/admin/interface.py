from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelForm, CharField
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from mptt.admin import DraggableMPTTAdmin
from reversion.admin import VersionAdmin

from judge.dblock import LockModel
from judge.widgets import HeavySelect2MultipleWidget, HeavyPreviewAdminPageDownWidget, HeavySelect2Widget
from ckeditor.widgets import CKEditorWidget


class NoticePostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NoticePostForm, self).__init__(*args, **kwargs)
        self.fields['authors'].widget.can_add_related = False

    class Meta:
        widgets = {
            'authors': HeavySelect2MultipleWidget(data_view='profile_select2', attrs={'style': 'width: 100%'}),
            'content' : CKEditorWidget()
        }


class NoticePostAdmin(VersionAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'authors', 'visible', 'sticky', 'publish_on')}),
        (_('Content'), {'fields': ('content', )}),
    )
    list_display = ('id', 'title', 'visible', 'sticky', 'publish_on')
    list_display_links = ('id', 'title')
    ordering = ('-publish_on',)
    form = NoticePostForm
    date_hierarchy = 'publish_on'

    def has_change_permission(self, request, obj=None):
        return (request.user.has_perm('judge.edit_all_post') or
                request.user.has_perm('judge.change_noticepost') and (
                    obj is None or
                    obj.authors.filter(id=request.user.profile.id).exists()))


class SolutionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SolutionForm, self).__init__(*args, **kwargs)
        self.fields['authors'].widget.can_add_related = False

    class Meta:
        widgets = {
            'authors': HeavySelect2MultipleWidget(data_view='profile_select2', attrs={'style': 'width: 100%'}),
            'problem': HeavySelect2Widget(data_view='problem_select2', attrs={'style': 'width: 250px'}),
        }

        if HeavyPreviewAdminPageDownWidget is not None:
            widgets['content'] = HeavyPreviewAdminPageDownWidget(preview=reverse_lazy('solution_preview'))