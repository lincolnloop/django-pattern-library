import copy
import json

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

import yaml

from pattern_library import get_base_template_names, get_pattern_base_template_name
from pattern_library.exceptions import PatternLibraryEmpty, TemplateIsNotPattern
from pattern_library.utils import (
    get_pattern_config,
    get_pattern_config_str,
    get_pattern_markdown,
    get_renderer,
    get_sections,
    is_pattern,
    render_pattern,
)


class IndexView(TemplateView):
    http_method_names = ("get",)
    template_name = "pattern_library/index.html"

    def first_template_from_group(self, templates):
        try:
            return templates["templates_stored"][0]
        except IndexError:
            for template_group in templates["template_groups"].values():
                return self.first_template_from_group(template_group)
        return None

    def get_first_template(self, templates):
        first_template = self.first_template_from_group(templates)
        if first_template:
            return first_template.origin.template_name

        sections = get_sections()
        if sections:
            raise PatternLibraryEmpty(
                "No templates found matching: '%s'" % str(sections)
            )
        else:
            raise PatternLibraryEmpty(
                "No 'SECTIONS' found in the 'PATTERN_LIBRARY' setting"
            )

    def get(self, request, pattern_template_name=None):
        # Get all pattern templates
        renderer = get_renderer()
        templates = renderer.get_pattern_templates()

        if pattern_template_name is None:
            # Just display the first pattern if a specific one isn't requested
            pattern_template_name = self.get_first_template(templates)

        if not is_pattern(pattern_template_name):
            raise Http404

        template = get_template(pattern_template_name)
        pattern_config = get_pattern_config(pattern_template_name)

        context = self.get_context_data()
        context["pattern_templates"] = templates
        context["pattern_template_name"] = pattern_template_name
        context["pattern_source"] = renderer.get_pattern_source(template)
        context["pattern_config"] = escape(
            get_pattern_config_str(pattern_template_name)
        )
        context["pattern_name"] = pattern_config.get("name", pattern_template_name)
        context["pattern_markdown"] = get_pattern_markdown(pattern_template_name)

        return self.render_to_response(context)


@method_decorator(xframe_options_sameorigin, name="dispatch")
class RenderPatternView(TemplateView):
    http_method_names = ("get", "post", "options")
    template_name = get_pattern_base_template_name()

    def get(self, request, pattern_template_name=None):
        return self.render_with_config(
            request, pattern_template_name, get_pattern_config(pattern_template_name)
        )

    def post(self, request, pattern_template_name=None):
        try:
            config = yaml.safe_load(request.POST.get("config", "")) or {}
        except yaml.YAMLError:
            # Don't echo the exception back; it exposes internals (CodeQL)
            return HttpResponseBadRequest(
                "Invalid YAML: syntax error", content_type="text/plain"
            )
        if not isinstance(config, dict):
            return HttpResponseBadRequest(
                "Invalid YAML: config must be a mapping", content_type="text/plain"
            )
        for key in ("context", "tags"):
            if key in config and not isinstance(config[key], dict):
                return HttpResponseBadRequest(
                    f"Invalid YAML: {key} must be a mapping", content_type="text/plain"
                )
        return self.render_with_config(request, pattern_template_name, config)

    def options(self, request, *args, **kwargs):
        # Static hosts (e.g. Apache) can allow POST too; this marks a real backend
        response = super().options(request, *args, **kwargs)
        response["X-Pattern-Library-Live-Edit"] = "1"
        return response

    def render_with_config(self, request, pattern_template_name, config):
        renderer = get_renderer()
        pattern_template_ancestors = renderer.get_template_ancestors(
            pattern_template_name,
            context=config.get("context", {}),
        )
        pattern_is_fragment = set(pattern_template_ancestors).isdisjoint(
            set(get_base_template_names())
        )

        try:
            rendered_pattern = render_pattern(
                request, pattern_template_name, config=copy.deepcopy(config)
            )
        except TemplateIsNotPattern:
            raise Http404

        if pattern_is_fragment:
            context = self.get_context_data()
            context["pattern_library_rendered_pattern"] = mark_safe(rendered_pattern)

            # Add the pattern config to the context, so that name is available
            # in the base template.
            context["pattern_config"] = config
            context["pattern_name"] = config.get("name", "")

            return self.render_to_response(context)

        return HttpResponse(rendered_pattern)


@csrf_exempt
def render_pattern_api(request):
    data = json.loads(request.body.decode("utf-8"))
    template_name = data["template_name"]
    config = data["config"]

    try:
        rendered_pattern = render_pattern(
            request, template_name, allow_non_patterns=False, config=config
        )
    except TemplateIsNotPattern:
        raise Http404

    return HttpResponse(rendered_pattern)
