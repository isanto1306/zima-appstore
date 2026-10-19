"""Offline tests for the GHCR-verified ZimaOS app-store version sync."""
import tempfile
import unittest
from pathlib import Path

from scripts.sync_install_monitor import sync


def fixture(version: str) -> str:
    return (
        f"# Install Monitor v{version} public beta for ZimaOS.\n"
        "name: install-monitor\n"
        "services:\n"
        "  install-monitor:\n"
        f"    image: ghcr.io/isanto1306/install-monitor:{version}\n"
        "  registry:\n"
        "    image: registry:2.8.3\n"
        "x-casaos:\n"
        f"  version: \"{version}\"\n"
        "  update_at: \"2026-10-19\"\n"
    )


class InstallMonitorStoreSyncTests(unittest.TestCase):
    def prepare(self, old="0.2.56-beta.11"):
        tmp = tempfile.TemporaryDirectory()
        path = Path(tmp.name) / "docker-compose.yml"
        path.write_text(fixture(old), encoding="utf-8")
        self.addCleanup(tmp.cleanup)
        return path

    def test_updates_version_and_image_without_corrupting_yaml(self):
        path = self.prepare()
        checked = []
        changed = sync(
            path,
            fetch=lambda: 'VERSION = "0.2.56-beta.12"\n',
            image_exists=lambda tag: checked.append(tag) or True,
        )
        self.assertTrue(changed)
        body = path.read_text(encoding="utf-8")
        self.assertEqual(checked, ["0.2.56-beta.12"])
        self.assertEqual(body, fixture("0.2.56-beta.12"))
        self.assertIn("\n  update_at:", body)
        self.assertIn("image: registry:2.8.3", body)

    def test_does_not_advertise_unpublished_version(self):
        path = self.prepare()
        changed = sync(
            path,
            fetch=lambda: 'VERSION = "0.2.56-beta.12"\n',
            image_exists=lambda tag: False,
        )
        self.assertFalse(changed)
        self.assertEqual(path.read_text(encoding="utf-8"), fixture("0.2.56-beta.11"))

    def test_does_not_downgrade(self):
        path = self.prepare()
        def no_registry_call(tag):
            self.fail("No registry call expected for older version")
        changed = sync(
            path,
            fetch=lambda: 'VERSION = "0.2.56-beta.10"\n',
            image_exists=no_registry_call,
        )
        self.assertFalse(changed)
        self.assertEqual(path.read_text(encoding="utf-8"), fixture("0.2.56-beta.11"))

    def test_rejects_inconsistent_store_metadata(self):
        path = self.prepare()
        body = path.read_text(encoding="utf-8").replace(
            '  version: "0.2.56-beta.11"', '  version: "0.2.56-beta.3"'
        )
        path.write_text(body, encoding="utf-8")
        with self.assertRaises(RuntimeError):
            sync(
                path,
                fetch=lambda: 'VERSION = "0.2.56-beta.12"\n',
                image_exists=lambda tag: True,
            )
        self.assertEqual(path.read_text(encoding="utf-8"), body)


if __name__ == "__main__":
    unittest.main()
