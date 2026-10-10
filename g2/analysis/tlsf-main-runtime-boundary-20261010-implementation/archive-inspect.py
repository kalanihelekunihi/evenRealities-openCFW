from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd();D=R/'g2/analysis/tlsf-main-runtime-boundary-20261010-implementation';L=R/'third-party/local-vendor/toolchains/iar-linux-x86_64/cxarm-10.10.2/arm/lib';sha=lambda b:hashlib.sha256(b).hexdigest();rows=[]
for library,members in [('rt7M_tl.a',['memcpy.o','ABImemcpy.o','ABImemcpy_small.o']),('dl7M_tln.a',['assert.o','printf.o'])]:
 archive=L/library;arhash=sha(archive.read_bytes())
 for member in members:
  b=subprocess.check_output(['arm-none-eabi-ar','p',str(archive),member]);p=Path('/tmp')/('tlsf-iar-'+member);p.write_bytes(b)
  row=dict(archive=str(archive.relative_to(R)),archive_sha256=arhash,member=member,member_sha256=sha(b))
  for label,args in [('symbols',['arm-none-eabi-nm',str(p)]),('sections',['arm-none-eabi-readelf','-S',str(p)]),('attributes',['arm-none-eabi-readelf','-A',str(p)]),('relocations',['arm-none-eabi-readelf','-r',str(p)])]:row[label]=subprocess.run(args,text=True,capture_output=True).stdout
  rows.append(row)
(D/'archive-inspection.json').write_text(json.dumps(rows,indent=2)+'\n')
# No copyrighted runtime source/object is copied into report; only metadata/hash receipts.
print('\n'.join(x['member']+': '+x['symbols'][:300] for x in rows))
