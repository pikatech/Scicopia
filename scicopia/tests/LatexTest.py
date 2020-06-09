import unittest
from pylatexenc.latex2text import (
    LatexNodes2Text,
    get_default_latex_context_db,
    MacroTextSpec,
)


class LatexTest(unittest.TestCase):
    def test_macrospec(self):
        context_db = get_default_latex_context_db()
        textit = MacroTextSpec("textit", "<i>%s</i>")
        context_db.add_context_category(category="html", macros=[textit], prepend=True)

        latex = r"But \textit{how} is this done?"
        result = LatexNodes2Text(latex_context=context_db).latex_to_text(latex)
        self.assertEqual(result, "But <i>how</i> is this done?")

    def test_nested_macrospec(self):
        context_db = get_default_latex_context_db()
        textit = MacroTextSpec("textit", "<i>%s</i>")
        textbf = MacroTextSpec("textbf", "<b>%s</b>")
        context_db.add_context_category(
            category="html", macros=[textit, textbf], prepend=True
        )

        latex = r"But \textbf{\textit{how}} is this done?"
        result = LatexNodes2Text(latex_context=context_db).latex_to_text(latex)
        self.assertEqual(result, "But <b><i>how</i></b> is this done?")

    def test_math_mode(self):
        latex = r"How would you calculate $\sqrt{n}$?"
        result = LatexNodes2Text(math_mode="verbatim").latex_to_text(latex)
        self.assertEqual(result, "How would you calculate $\sqrt{n}$?")

    def test_comments(self):
        latex = r"http://www.ncstrl.org:8900/ncstrl/servlet/search?formname=detail\&id=oai%3Ancstrlh%3Autk_cs%3Ancstrl.utk_cs%2F%2FUT-CS-94-236"
        result = LatexNodes2Text(keep_comments=True).latex_to_text(latex)
        self.assertEqual(
            result,
            r"http://www.ncstrl.org:8900/ncstrl/servlet/search?formname=detail\&id=oai%3Ancstrlh%3Autk_cs%3Ancstrl.utk_cs%2F%2FUT-CS-94-236",
        )
