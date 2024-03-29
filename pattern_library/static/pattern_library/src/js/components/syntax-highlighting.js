import hljs from "highlight.js/lib/core";
import django from "highlight.js/lib/languages/django";
import yaml from "highlight.js/lib/languages/yaml";
import html from "highlight.js/lib/languages/vbscript-html.js";
import md from "highlight.js/lib/languages/markdown.js";

export default function () {
    hljs.registerLanguage("django", django);
    hljs.registerLanguage("yaml", yaml);
    hljs.registerLanguage("md", md);
    hljs.registerLanguage("html", html);
    hljs.highlightAll();
}
