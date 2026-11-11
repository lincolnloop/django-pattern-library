from django.test import Client, SimpleTestCase

from bs4 import BeautifulSoup

from .utils import reverse


class ViewsTestCase(SimpleTestCase):
    def test_index(self):
        response = self.client.get(reverse("pattern_library:index"))
        self.assertEqual(response.status_code, 200)

    def test_pretty_names_from_context(self):
        test_molecule_display_url = reverse(
            "pattern_library:display_pattern",
            kwargs={
                "pattern_template_name": "patterns/molecules/test_molecule/test_molecule.html"
            },
        )
        test_molecule_render_url = reverse(
            "pattern_library:render_pattern",
            kwargs={
                "pattern_template_name": "patterns/molecules/test_molecule/test_molecule.html"
            },
        )

        response = self.client.get(test_molecule_display_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, features="html.parser")

        display_link = soup.select_one(f'a[href="{test_molecule_display_url}"]')
        render_link = soup.select_one(f'a[href="{test_molecule_render_url}"]')

        self.assertEqual(display_link.text.strip(), "Pretty name for test molecule")
        self.assertEqual(render_link.text.strip(), "Pretty name for test molecule")

    def test_pretty_names_from_filename(self):
        pattern_path = "patterns/molecules/test_molecule/test_molecule_no_context.html"
        test_molecule_display_url = reverse(
            "pattern_library:display_pattern",
            kwargs={"pattern_template_name": pattern_path},
        )
        test_molecule_render_url = reverse(
            "pattern_library:render_pattern",
            kwargs={"pattern_template_name": pattern_path},
        )

        response = self.client.get(test_molecule_display_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, features="html.parser")

        display_link = soup.select_one(
            f'.list__item>a[href="{test_molecule_display_url}"]'
        )
        render_link = soup.select_one(f'a[href="{test_molecule_render_url}"]')

        self.assertEqual(display_link.text.strip(), "test_molecule_no_context.html")
        self.assertEqual(render_link.text.strip(), pattern_path)

    def test_pretty_names_from_filename_containing_dashes(self):
        pattern_path = "patterns/molecules/test-molecule/test-molecule.html"
        test_molecule_display_url = reverse(
            "pattern_library:display_pattern",
            kwargs={"pattern_template_name": pattern_path},
        )
        test_molecule_render_url = reverse(
            "pattern_library:render_pattern",
            kwargs={"pattern_template_name": pattern_path},
        )

        response = self.client.get(test_molecule_display_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, features="html.parser")

        display_link = soup.select_one(
            f'.list__item>a[href="{test_molecule_display_url}"]'
        )
        render_link = soup.select_one(f'a[href="{test_molecule_render_url}"]')

        self.assertEqual(display_link.text.strip(), "test-molecule.html")
        self.assertEqual(render_link.text.strip(), pattern_path)

    def test_includes(self):
        pattern_path = "patterns/atoms/test_includes/test_includes.html"
        display_url = reverse(
            "pattern_library:display_pattern",
            kwargs={"pattern_template_name": pattern_path},
        )
        render_url = reverse(
            "pattern_library:render_pattern",
            kwargs={"pattern_template_name": pattern_path},
        )

        display_response = self.client.get(display_url)
        self.assertEqual(display_response.status_code, 200)

        render_response = self.client.get(render_url)
        self.assertEqual(render_response.status_code, 200)
        self.assertContains(render_response, "SHOWME")
        self.assertNotContains(render_response, "HIDEME")
        self.assertContains(render_response, "included content from variable")

    def test_page(self):
        test_page_render_url = reverse(
            "pattern_library:render_pattern",
            kwargs={"pattern_template_name": "patterns/pages/test_page/test_page.html"},
        )
        response = self.client.get(test_page_render_url)

        self.assertContains(response, "<title>Page</title>")

    def test_fragments(self):
        test_cases = [
            (
                "patterns/atoms/test_atom/test_atom.html",
                "<title>Django pattern library</title>",
            ),
            (
                "patterns/molecules/test_molecule/test_molecule.html",
                "<title>Pretty name for test molecule | Django pattern library</title>",
            ),
            (
                "patterns/molecules/test-molecule/test-molecule.html",
                "<title>Django pattern library</title>",
            ),
        ]
        for template_name, expected_title in test_cases:
            with self.subTest(template_name=template_name):
                self.assertContains(
                    self.client.get(
                        reverse(
                            "pattern_library:render_pattern",
                            kwargs={"pattern_template_name": template_name},
                        ),
                    ),
                    expected_title,
                )

    def test_fragment_extended_from_variable(self):
        self.assertContains(
            self.client.get(
                reverse(
                    "pattern_library:render_pattern",
                    kwargs={
                        "pattern_template_name": "patterns/atoms/test_extends/extended.html"
                    },
                ),
            ),
            "base content - extended content",
        )

    def test_pattern_name_in_context(self):
        """Test that pattern_name and pattern_config are added to context for fragments"""
        # Test pattern with custom name from YAML
        response = self.client.get(
            reverse(
                "pattern_library:render_pattern",
                kwargs={
                    "pattern_template_name": "patterns/molecules/test_molecule/test_molecule.html"
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<title>Pretty name for test molecule | Django pattern library</title>",
        )

        # Test pattern without custom name (should have empty pattern_name)
        response = self.client.get(
            reverse(
                "pattern_library:render_pattern",
                kwargs={
                    "pattern_template_name": "patterns/atoms/test_atom/test_atom.html"
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<title>Django pattern library</title>")

    def test_pattern_config_in_context_is_not_mutated_by_rendering(self):
        response = self.client.get(
            reverse(
                "pattern_library:render_pattern",
                kwargs={
                    "pattern_template_name": "patterns/molecules/button/button.html"
                },
            )
        )
        self.assertEqual(
            response.context["pattern_config"]["context"],
            {"target_page": {"title": "Get started"}},
        )

    def test_index_has_config_editor(self):
        response = self.client.get(
            reverse(
                "pattern_library:display_pattern",
                kwargs={
                    "pattern_template_name": "patterns/molecules/button/button.html"
                },
            )
        )
        self.assertContains(response, "Toggle live mode")
        self.assertContains(response, "js-config-editor")
        self.assertContains(response, "js-config-mount")
        self.assertContains(response, 'aria-label="Template config (YAML)"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "title: Get started")


class LiveConfigViewsTestCase(SimpleTestCase):
    def setUp(self):
        self.url = reverse(
            "pattern_library:render_pattern",
            kwargs={"pattern_template_name": "patterns/molecules/button/button.html"},
        )

    def test_renders_posted_config(self):
        response = self.client.post(
            self.url,
            {
                "config": "name: Edited\n"
                "context:\n  target_page:\n    title: Edited title\n"
                "tags:\n  pageurl:\n    target_page:\n      raw: /edited\n"
            },
        )
        self.assertContains(response, "Edited title")
        self.assertContains(response, "/edited")
        self.assertContains(response, "<title>Edited | Django pattern library</title>")
        self.assertEqual(response["X-Frame-Options"], "SAMEORIGIN")

    def test_invalid_yaml(self):
        for config in ("context: [unclosed", "just a string"):
            with self.subTest(config=config):
                response = self.client.post(self.url, {"config": config})
                self.assertEqual(response.status_code, 400)
                self.assertContains(response, "Invalid YAML", status_code=400)

    def test_scalar_context_is_rejected(self):
        # A scalar context/tags used to 500 when rendering tried to index it
        for config in ("context: t", "tags: t"):
            with self.subTest(config=config):
                response = self.client.post(self.url, {"config": config})
                self.assertEqual(response.status_code, 400)
                self.assertContains(response, "must be a mapping", status_code=400)

    def test_empty_config_renders_empty_not_default(self):
        response = self.client.post(self.url, {"config": ""})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Get started")

    def test_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(self.url, {"config": "context: {}"})
        self.assertEqual(response.status_code, 403)

    def test_options_marks_live_edit_backend(self):
        response = self.client.options(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("POST", response["Allow"])
        self.assertEqual(response["X-Pattern-Library-Live-Edit"], "1")


class APIViewsTestCase(SimpleTestCase):
    def test_renders_with_tag_overrides(self):
        api_endpoint = reverse("pattern_library:render_pattern_api")
        response = self.client.post(
            api_endpoint,
            content_type="application/json",
            data={
                "template_name": "patterns/molecules/button/button.html",
                "config": {
                    "context": {"target_page": {"title": "API"}},
                    "tags": {"pageurl": {"target_page": {"raw": "/hello-api"}}},
                },
            },
        )
        self.assertContains(response, "/hello-api")

    def test_404(self):
        api_endpoint = reverse("pattern_library:render_pattern_api")
        response = self.client.post(
            api_endpoint,
            content_type="application/json",
            data={
                "template_name": "doesnotexist.html",
                "config": {},
            },
        )
        self.assertEqual(response.status_code, 404)
