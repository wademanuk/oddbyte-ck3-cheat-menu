"""Verify immutable release contents and replace the local mod with rollback on failure."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,shutil,tempfile,zipfile
from project_config import ROOT,PACKAGE,USERMOD,ARCHIVE_STEM


def hashes(folder):
 return {str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob('*')) if p.is_file()}


def descriptor_version(text):
 match=re.search(r'^\s*version\s*=\s*"([^"\r\n]+)"',text,flags=re.M)
 if not match:raise ValueError('Mod descriptor has no quoted version')
 return match[1]


def archive_contents(path):
 with zipfile.ZipFile(path) as archive:
  if archive.testzip() is not None:raise ValueError('Corrupt release ZIP: '+str(path))
  names=archive.namelist()
  if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP entries: '+str(path))
  return {name:archive.read(name) for name in names}


def publish_release(package,releases):
 package=Path(package);releases=Path(releases);releases.mkdir(parents=True,exist_ok=True)
 source=package/'tw_basic_cheat_menu'
 version=descriptor_version((source/'descriptor.mod').read_text(encoding='utf-8-sig'))
 expected={str(p.relative_to(package)):p.read_bytes() for p in sorted(package.rglob('*')) if p.is_file()}
 current=releases/(ARCHIVE_STEM+'.zip')
 named=releases/f'{ARCHIVE_STEM}-v{version}.zip'
 prior=archive_contents(current) if current.exists() else None
 prior_version=descriptor_version(prior['tw_basic_cheat_menu/descriptor.mod'].decode('utf-8-sig')) if prior else None
 # Check version collisions before changing either archive or the installed mod.
 if named.exists() and archive_contents(named)!=expected:
  raise ValueError(f'Release {version} already exists with different contents. Bump the mod version before packaging.')
 if prior_version==version and prior!=expected:
  raise ValueError(f'Current release {version} differs from this build. Bump the mod version before packaging.')
 if prior:
  archived=releases/f'{ARCHIVE_STEM}-v{prior_version}.zip'
  if archived.exists():
   if archive_contents(archived)!=prior:raise ValueError('Current ZIP does not match its archived version: '+str(archived))
  else:shutil.copy2(current,archived)
 with tempfile.TemporaryDirectory(prefix='.twcm-package-',dir=releases) as temporary:
  candidate=Path(temporary)/'candidate.zip'
  with zipfile.ZipFile(candidate,'w',zipfile.ZIP_DEFLATED) as archive:
   for path in sorted(package.rglob('*')):
    if path.is_file():archive.write(path,path.relative_to(package))
  if archive_contents(candidate)!=expected:raise ValueError('Candidate ZIP contents differ from package')
  if not named.exists():os.replace(candidate,named)
  # Reuse the immutable archive even when rebuilding only changed source file timestamps.
  shutil.copy2(named,candidate)
  os.replace(candidate,current)
 return {'version':version,'zip':str(current),'zip_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),'files':hashes(source)}


def install_mod(source,usermod,backup_root):
 source=Path(source);usermod=Path(usermod);backup_root=Path(backup_root)
 usermod.mkdir(parents=True,exist_ok=True);backup_root.mkdir(parents=True,exist_ok=True)
 installed=usermod/source.name;external=usermod/(source.name+'.mod')
 if installed.is_symlink():raise ValueError('Installed mod directory is a symlink; refusing to replace its target')
 expected=hashes(source)
 descriptor=(source/'descriptor.mod').read_text(encoding='utf-8-sig')+'path='+json.dumps(str(installed.resolve()))+'\n'
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S-UTC-')
 backup=Path(tempfile.mkdtemp(prefix=stamp,dir=backup_root))
 if installed.exists():shutil.copytree(installed,backup/installed.name)
 if external.exists():shutil.copy2(external,backup/external.name)
 # Stage and verify before touching the active installation. Replacement removes retired files.
 with tempfile.TemporaryDirectory(prefix='.twcm-install-',dir=usermod) as temporary:
  stage=Path(temporary);new_mod=stage/source.name;new_descriptor=stage/external.name
  shutil.copytree(source,new_mod)
  if hashes(new_mod)!=expected:raise ValueError('Staged mod differs from generated source')
  new_descriptor.write_text(descriptor)
  retired_mod=stage/'previous-mod';retired_descriptor=stage/'previous.mod'
  wrote_mod=False;wrote_descriptor=False
  try:
   if installed.exists():os.replace(installed,retired_mod)
   if external.exists() or external.is_symlink():os.replace(external,retired_descriptor)
   os.replace(new_mod,installed);wrote_mod=True
   os.replace(new_descriptor,external);wrote_descriptor=True
   if hashes(installed)!=expected:raise ValueError('Installed mod differs from staged contents')
   if external.read_text()!=descriptor:raise ValueError('Installed descriptor differs from staged contents')
  except BaseException:
   if wrote_mod:shutil.rmtree(installed)
   if wrote_descriptor:external.unlink()
   if retired_mod.exists():os.replace(retired_mod,installed)
   if retired_descriptor.exists() or retired_descriptor.is_symlink():os.replace(retired_descriptor,external)
   raise
 return {'installed_mod':str(installed),'descriptor':str(external),'backup':str(backup)}


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--install',action='store_true');args=parser.parse_args()
 root=ROOT;package=PACKAGE
 report=publish_release(package,root/'releases')
 if args.install:
  report.update(install_mod(package/'tw_basic_cheat_menu',USERMOD,root/'backups'))
 (root/'installation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))

if __name__=='__main__':main()
