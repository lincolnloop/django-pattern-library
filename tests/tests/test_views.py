from django.test import SimpleTestCase

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
        for template_name in [
            "patterns/atoms/test_atom/test_atom.html",
            "patterns/molecules/test_molecule/test_molecule.html",
            "patterns/molecules/test-molecule/test-molecule.html",
        ]:
            with self.subTest(template_name=template_name):
                self.assertContains(
                    self.client.get(
                        reverse(
                            "pattern_library:render_pattern",
                            kwargs={"pattern_template_name": template_name},
                        ),
                    ),
                    "<title>Fragment</title>",
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

    def test_columns_on_index_page(self):
        response = self.client.get(
            reverse(("pattern_library:index")),
        )
        columns = [
            "Template source",
            "Template output",
            "Template config",
            "Template docs",
        ]
        for column in columns:
            self.assertContains(response, column)

    def test_template_output_on_index_page(self):
        response = self.client.get(
            reverse(
                ("pattern_library:index"),
            ),
        )
        self.assertContains(
            response,
            """<pre><code class="code html">&lt;svg aria-hidden=&quot;true&quot; class=&quot;icon icon--close&quot; focusable=&quot;false&quot;&gt;\n    &lt;use xlink:href=&quot;#close&quot;&gt;\n    &lt;/use&gt;\n&lt;/svg&gt;\n</code></pre>\n                </div>\n\n                <div id="tab-3" class="tabbed-content__item">\n                    <pre><code class="code yaml">context:\n  name: close\n</code></pre>\n                </div>""",
        )


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
