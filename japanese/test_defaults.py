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
 def test_whisper_is_local_japanese_and_pastes(self):
  self.apply(); c=tomllib.loads((self.home/'.config/voxtype/config.toml').read_text())
  self.assertEqual(c['engine'],'whisper'); self.assertEqual(c['whisper']['language'],'ja'); self.assertEqual(c['output']['mode'],'paste')
  self.assertEqual(c['whisper']['model'],'small')
  model=self.home/'.local/share/voxtype/models/ggml-small.bin'
  self.assertTrue(model.is_symlink())
  self.assertEqual(str(model.readlink()),'/usr/local/share/omarchy-jp/ggml-small.bin')
  self.assertFalse(c['hotkey']['enabled'])
 def test_plugin_insert_preserves_existing_bar(self):
  p=self.home/'.config/omarchy/shell.json'; p.parent.mkdir(parents=True); p.write_text(json.dumps({'version':1,'bar':{'layout':{'right':[{'id':'omarchy.audio'}]}}}))
  self.apply(); c=json.loads(p.read_text()); ids=[x['id'] for x in c['bar']['layout']['right']]
  self.assertEqual(ids,['komagata.input-method','omarchy.audio'])
 def test_reboot_preserves_user_changes(self):
  p=self.home/'.config/omarchy/shell.json'; p.parent.mkdir(parents=True); p.write_text('{"version":1,"bar":{"layout":{"right":[]}}}')
  self.apply(); config=self.home/'.config/voxtype/config.toml'; config.write_text('engine="soniox"\n')
  self.apply(); self.assertEqual(config.read_text(),'engine="soniox"\n')
 def test_voice_service_enabled_without_first_run_prompt(self):
  self.apply(); service=self.home/'.config/systemd/user/graphical-session.target.wants/voxtype.service'
  self.assertTrue(service.is_symlink()); self.assertTrue((self.home/'.local/state/omarchy/done/voxtype-install-invitation').exists())
if __name__=='__main__': unittest.main()
