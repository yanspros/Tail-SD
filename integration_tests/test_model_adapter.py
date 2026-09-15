import unittest


class ExternalModelAdapterTest(unittest.TestCase):
    @unittest.skip("requires a user-installed CosyVoice checkout, checkpoint, and prompt assets")
    def test_external_cosyvoice_adapter(self):
        self.fail("integration adapter was not configured")
