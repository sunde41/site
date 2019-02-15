from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin


class CommentedDetailView(TemplateResponseMixin, SingleObjectMixin, View):
    comment_page = None

    def get_comment_page(self):
        if self.comment_page is None:
            raise NotImplementedError()
        return self.comment_page

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data(
            object=self.object,
        ))

    def get_context_data(self, **kwargs):
        context = super(CommentedDetailView, self).get_context_data(**kwargs)
        return context
