import importlib.util,json,tempfile,unittest,tomllib
from pathlib import Path
SCRIPT=Path(__file__).with_name('jp_defaults.py')
class DefaultsTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
  self.home=Path(self.tmp.name)/'home'; self.home.mkdir()
 def apply(self,layout='us'):
  self.assertTrue(SCRIPT.exists(),'JP defaults initializer has not been implemented')
  spec=importlib.util.spec_from_file_location('jp_defaults',SCRIPT); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
  m.configure_user(self.home,layout)
 def test_japanese_input_keeps_physical_keyboard(self):
  self.apply('jp'); p=(self.home/'.config/fcitx5/profile').read_text()
  self.assertIn('Default Layout=jp',p); self.assertIn('Name=keyboard-jp',p); self.assertIn('Name=mozc',p)
if __name__=='__main__': unittest.main()
