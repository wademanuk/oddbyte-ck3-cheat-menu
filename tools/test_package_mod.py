"""Release consistency and installation failure recovery, entirely in temporary folders."""
from pathlib import Path
import os,tempfile,unittest
from unittest.mock import patch
from package_mod import publish_release,install_mod,archive_contents,hashes

class PackageTests(unittest.TestCase):
 def setUp(self):
  temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
  self.root=Path(temporary.name);self.package=self.root/'package';self.source=self.package/'tw_basic_cheat_menu'
  self.source.mkdir(parents=True)
  (self.source/'descriptor.mod').write_text('version="1.0.0"\nname="Test"\n')
  (self.source/'effects.txt').write_text('old effect')
  self.releases=self.root/'releases';self.usermod=self.root/'user-mods';self.backups=self.root/'backups'
 def test_same_version_changed_contents_is_rejected_before_current_zip_changes(self):
  release=publish_release(self.package,self.releases);current=Path(release['zip']);before=current.read_bytes()
  (self.source/'effects.txt').write_text('different effect')
  with self.assertRaisesRegex(ValueError,'Bump the mod version'):publish_release(self.package,self.releases)
  self.assertEqual(current.read_bytes(),before)
 def test_same_contents_with_new_timestamps_reuses_the_named_zip(self):
  release=publish_release(self.package,self.releases);before=Path(release['zip']).read_bytes()
  os.utime(self.source/'effects.txt',(1800000000,1800000000))
  publish_release(self.package,self.releases)
  self.assertEqual(Path(release['zip']).read_bytes(),before)
 def test_new_release_preserves_previous_and_both_current_archives_match(self):
  first=publish_release(self.package,self.releases);old=Path(first['zip']).read_bytes()
  (self.source/'descriptor.mod').write_text('version="1.0.1"\nname="Test"\n')
  release=publish_release(self.package,self.releases)
  self.assertEqual((self.releases/'Oddbyte-CK3-Cheat-Menu-v1.0.0.zip').read_bytes(),old)
  self.assertEqual(Path(release['zip']).read_bytes(),(self.releases/'Oddbyte-CK3-Cheat-Menu-v1.0.1.zip').read_bytes())
  self.assertEqual(archive_contents(release['zip'])['tw_basic_cheat_menu/descriptor.mod'],(self.source/'descriptor.mod').read_bytes())
 def installed_fixture(self):
  info=install_mod(self.source,self.usermod,self.backups)
  installed=Path(info['installed_mod']);external=Path(info['descriptor'])
  (installed/'retired-effect.txt').write_text('must not remain active')
  return installed,external,hashes(installed),external.read_bytes()
 def test_upgrade_removes_retired_files_and_preserves_them_in_backup(self):
  installed,external,_,_=self.installed_fixture()
  (self.source/'effects.txt').write_text('new effect')
  info=install_mod(self.source,self.usermod,self.backups)
  self.assertEqual(hashes(installed),hashes(self.source))
  self.assertEqual((Path(info['backup'])/installed.name/'retired-effect.txt').read_text(),'must not remain active')
  self.assertIn(str(installed.resolve()),external.read_text())
 def test_upgrade_preserves_local_workshop_id_without_adding_it_to_the_portable_source(self):
  installed,external,_,_=self.installed_fixture()
  for path in [installed/'descriptor.mod',external]:
   path.write_text(path.read_text()+'remote_file_id="3840619967"\n')
  info=install_mod(self.source,self.usermod,self.backups)
  for path in [installed/'descriptor.mod',external]:self.assertIn('remote_file_id="3840619967"',path.read_text())
  self.assertNotIn('remote_file_id',(self.source/'descriptor.mod').read_text())
  self.assertIn('remote_file_id',(Path(info['backup'])/installed.name/'descriptor.mod').read_text())
 def test_explicit_source_publication_id_takes_precedence(self):
  installed,external,_,_=self.installed_fixture()
  (installed/'descriptor.mod').write_text((installed/'descriptor.mod').read_text()+'remote_file_id="111"\n')
  (self.source/'descriptor.mod').write_text((self.source/'descriptor.mod').read_text()+'remote_file_id="222"\n')
  install_mod(self.source,self.usermod,self.backups)
  self.assertIn('remote_file_id="222"',(installed/'descriptor.mod').read_text())
  self.assertNotIn('remote_file_id="111"',external.read_text())
 def test_staging_failure_leaves_active_files_and_descriptor_untouched(self):
  installed,external,before,descriptor=self.installed_fixture()
  from shutil import copytree as real_copytree
  def fail_source_copy(src,dst,*args,**kwargs):
   if Path(src)==self.source:raise OSError('simulated stage failure')
   return real_copytree(src,dst,*args,**kwargs)
  with patch('package_mod.shutil.copytree',side_effect=fail_source_copy):
   with self.assertRaisesRegex(OSError,'stage failure'):install_mod(self.source,self.usermod,self.backups)
  self.assertEqual(hashes(installed),before);self.assertEqual(external.read_bytes(),descriptor)
 def test_descriptor_replace_failure_rolls_back_mod_and_descriptor(self):
  installed,external,before,descriptor=self.installed_fixture();real_replace=os.replace
  def fail_new_descriptor(src,dst):
   if Path(src).name==external.name and Path(dst)==external:raise OSError('simulated descriptor failure')
   return real_replace(src,dst)
  with patch('package_mod.os.replace',side_effect=fail_new_descriptor):
   with self.assertRaisesRegex(OSError,'descriptor failure'):install_mod(self.source,self.usermod,self.backups)
  self.assertEqual(hashes(installed),before);self.assertEqual(external.read_bytes(),descriptor)
if __name__=='__main__':unittest.main()
