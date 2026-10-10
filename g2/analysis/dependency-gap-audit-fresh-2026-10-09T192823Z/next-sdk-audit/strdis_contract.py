from pathlib import Path
import zipfile,re,json,hashlib,html
O=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();rows=[]
with zipfile.ZipFile('/Users/kalani/Downloads/AmbiqSuite_5.2.0.zip') as z:
 def read(suffix):
  n=next(n for n in z.namelist() if n.endswith(suffix));b=z.read(n);rows.append({'zip_member':n,'sha256':sha(b),'bytes':len(b)});return b.decode()
 src=read('/mcu/apollo510/hal/mcu/am_hal_iom.c');head=read('/CMSIS/AmbiqMicro/Include/apollo510.h');doc=read('/docs/registers/apollo510/pages/iom_regs.html');hal=read('/mcu/apollo510/hal/mcu/am_hal_iom.h')
 oldp=Path('third-party/upstream/ambiqhal-apollo510/mcu/apollo510/hal/mcu/am_hal_iom.c');old=oldp.read_text();fields={}
 for field,pos,mask in re.findall(r'#define IOM0_MI2CCFG_(\w+)_Pos\s+\((\d+)UL\).*?\n#define IOM0_MI2CCFG_\1_Msk\s+\((0x[0-9a-fA-F]+)UL\)',head):fields[field]={'position':int(pos),'mask':int(mask,16)}
 assert fields['STRDIS']=={'position':24,'mask':0x1000000}
 def eqs(s):
  out=[]
  for rate in ['100KHZ','400KHZ','1MHZ']:
   block=s.split('case AM_HAL_IOM_'+rate+':',1)[1].split('break;',1)[0];expr=block.split('->MI2CCFG =',1)[1].split(';',1)[0];vals={}
   for f,v in re.findall(r'_VAL2FLD\(IOM0_MI2CCFG_(\w+),\s*(\w+)\)',expr):
    if v=='AM_HAL_IOM_MI2CCFG_STRDIS_DEFAULT':value=1
    elif v.startswith('IOM0_'):
     value=int(re.search(re.escape(v)+r'\s*=\s*(\d+)',head)[1])
    else:value=int(v,0)
    vals[f]=value
   word=0
   for f,v in vals.items():word|=(v<<fields[f]['position'])&fields[f]['mask']
   out.append({'rate_selection':rate,'nominal_argument_hz':int(re.search(r'#define AM_HAL_IOM_'+rate+r'\s+(\d+)',hal)[1]),'fields':vals,'word_hex':f'0x{word:08x}'})
  return out
 before=eqs(old);after=eqs(src)
 for a,b in zip(before,after):assert int(a['word_hex'],16)^int(b['word_hex'],16)==0x1000000 and {k:v for k,v in a['fields'].items() if k!='STRDIS'}=={k:v for k,v in b['fields'].items() if k!='STRDIS'}
 plain=html.unescape(re.sub('<[^>]+>',' ',doc));plain=re.sub(r'\s+',' ',plain);description='Disable detection of clock stretch events smaller than 1 cycle';assert description in plain;assert '0x400502C0' in plain
 result={'status':'PASS','sources':rows,'baseline':{'path':str(oldp),'sha256':sha(oldp.read_bytes()),'declared_revision':re.search(r'revision (release_\S+)',old)[1]},'sdk_revision':re.search(r'revision (release_\S+)',src)[1],'register':{'name':'MI2CCFG','iom0_address':'0x400502c0','offset':'0x2c0','field':'STRDIS','position':24,'mask':'0x01000000','authoritative_description':description,'reset_value':0},'before':before,'after':after,'fields':fields,'rate_comment_limit':'1MHZ branch source says settings should give approximately860kHz; no physical frequency verified','scope':'Source/header/document mapping only. Stock extent/producer/physical bus behavior unbound. No extraction or execution.'}
(O/'STRDIS-CONTRACT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','before':[(x['rate_selection'],x['word_hex']) for x in before],'after':[(x['rate_selection'],x['word_hex']) for x in after]},indent=2))
