import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LocaleFilesTest(unittest.TestCase):
    def test_locale_files_are_valid_json(self):
        for path in (ROOT / "locales").glob("*.json"):
            with self.subTest(path=path.name):
                json.loads(path.read_text(encoding="utf-8"))

    def test_non_english_locales_only_use_known_keys(self):
        english = json.loads((ROOT / "locales" / "en.json").read_text(encoding="utf-8"))
        english_keys = set(english)

        for path in (ROOT / "locales").glob("*.json"):
            if path.name == "en.json":
                continue
            with self.subTest(path=path.name):
                locale = json.loads(path.read_text(encoding="utf-8"))
                self.assertLessEqual(set(locale), english_keys)


if __name__ == "__main__":
    unittest.main()
