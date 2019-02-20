# -*- coding: utf-8 -*-

from django.http import HttpResponseBadRequest
from django.views.generic.base import TemplateResponseMixin, ContextMixin, View


class MarkdownPreviewView(TemplateResponseMixin, ContextMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            self.preview_data = data = request.POST['preview']
        except KeyError:
            return HttpResponseBadRequest('No preview data specified.')

        return self.render_to_response(self.get_context_data(
            preview_data=data,
        ))


class ProblemMarkdownPreviewView(MarkdownPreviewView):
    template_name = 'problem/preview.html'


class SolutionMarkdownPreviewView(MarkdownPreviewView):
    template_name = 'solution-preview.html'