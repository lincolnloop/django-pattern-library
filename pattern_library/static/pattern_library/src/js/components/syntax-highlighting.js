import hljs from "highlight.js/lib/core";
import django from "highlight.js/lib/languages/django";
import yaml from "highlight.js/lib/languages/yaml";
import md from "highlight.js/lib/languages/markdown";
import xml from "highlight.js/lib/languages/xml";

export default function () {
    hljs.registerLanguage("django", django);
    hljs.registerLanguage("yaml", yaml);
    hljs.registerLanguage("md", md);
    hljs.registerLanguage("xml", xml);
    hljs.highlightAll();
}
