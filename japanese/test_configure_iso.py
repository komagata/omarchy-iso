import importlib.util,tempfile,unittest
from pathlib import Path
SCRIPT=Path(__file__).with_name('configure_iso.py')
class ConfigureIsoTest(unittest.TestCase):
 def test_locale_and_package_list_and_phase(self):
  self.assertTrue(SCRIPT.exists(),'Japanese ISO configuration is not implemented')
  spec=importlib.util.spec_from_file_location('configure_iso',SCRIPT); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for name,text in [('root/configurator','"sys_lang": "en_US.UTF-8"\n' * 2),('usr/share/omarchy-iso/omarchy-base.packages','fcitx5\n'),('usr/share/omarchy-iso/orchestrator/main.py','from .ui import error, info\n        ("Finalizing user",            run_chroot_finalizer),\n')]:
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
   m.patch_iso(root)
   self.assertEqual((root/'root/configurator').read_text().count('en_US.UTF-8'), 2)
   self.assertIn('voxtype-bin',(root/'usr/share/omarchy-iso/omarchy-base.packages').read_text())
   self.assertIn('configure_jp',(root/'usr/share/omarchy-iso/orchestrator/main.py').read_text())
if __name__=='__main__': unittest.main()
