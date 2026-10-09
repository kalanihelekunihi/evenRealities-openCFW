from pathlib import Path
import json,struct,itertools,random
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'gcd':0x53937c,'integer':0x5393e8,'fraction':0x5394e0,'generate':0x5395a0,'min_vco':0x539674,'postdiv':0x539794}
names={'gcd':'audio_pll_gcd','integer':'audio_pll_integer','fraction':'audio_pll_fraction','generate':'audio_pll_generate','min_vco':'audio_pll_min_vco','postdiv':'audio_pll_postdiv'}
math_entries={0x43a5a0:'floorf',0x577c3c:'fmodf',0x577d08:'roundf',0x577d40:'ceilf'}
for a,n in list(math_entries.items()):math_entries[sym['audio_'+n]&~1]=n
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def run(native,c):
 u=machine();out=0x20006000;u.mem_write(out,bytes.fromhex('a55a5aa5a55a5aa5a55a5aa5a55a5aa5'));u.reg_write(UC_ARM_REG_FPSCR,c.get('fpscr',0));op=c['op'];calls=[]
 def code(u,a,n,d):
  if a in math_entries:calls.append([math_entries[a],u.reg_read(UC_ARM_REG_S0),u.reg_read(UC_ARM_REG_S1) if math_entries[a]=='fmodf' else None])
 u.hook_add(UC_HOOK_CODE,code)
 if op in ['gcd','integer','fraction','generate']:
  u.reg_write(UC_ARM_REG_S0,c['a']);u.reg_write(UC_ARM_REG_S1,c['b'])
  args=[out if c.get('nonnull',1) else 0]
  if op in ['integer','fraction']:args=[out+3,out+6,out+8]
 else:args=[out if c.get('nonnull',1) else 0,c['reference'],c['output'],c.get('minimum',60000000)]
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
 u.emu_start((sym[names[op]] if native else entries[op])|1,0x2007f000,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,c
 return dict(result=u.reg_read(UC_ARM_REG_S0) if op=='gcd' else u.reg_read(UC_ARM_REG_R0),output=bytes(u.mem_read(out,16)).hex(),fpscr=u.reg_read(UC_ARM_REG_FPSCR),math_calls=calls)
rows=[]
def compare(c):
 o=run(False,c);n=run(True,c)
 assert o==n,(c,o,n)
 rows.append(dict(inputs=c,**o))
# First a bounded smoke set, then independent integer-Hz and float-MHz profiles.
for op in ['gcd','integer','fraction','generate']:
 for a,b in [(12,240),(12,48),(12,196.608),(24,60),(1,960),(0,240),(12,0),(0,0),(12,960.0000610351562),(12,59.999996185302734)]:compare(dict(op=op,a=bits(a),b=bits(b)))
for op in ['min_vco','postdiv']:
 for reference,output in itertools.product([12000000,24000000,32768,0],[0,1000000,48000000,196608000,250000000,960000000]):compare(dict(op=op,reference=reference,output=output))
# Quiet vs signaling NaN, infinities, subnormal and signed zero; full FPSCR.
float_values=[0,0x80000000,bits(12),bits(60),bits(240),bits(960),0x7f800000,0xff800000,0x7fc01234,0x7f801234,1,0x80000001]
for op,profile,a,b in itertools.product(['gcd','integer','fraction','generate'],[0,1<<22,2<<22,3<<22,1<<24,1<<25,(1<<24)|(1<<25),0xa000009f],float_values,[bits(240),bits(960),0x7fc01234]):compare(dict(op=op,a=a,b=b,fpscr=profile))
for op,ref,out,profile in itertools.product(['min_vco','postdiv'],[0,1,9999999,10000000,12000000,24000000,32000000,0xffffffff],[0,1,1224489,1224490,48000000,196608000,250000000,960000000,0xffffffff],[0,1<<22,1<<24]):compare(dict(op=op,reference=ref,output=out,fpscr=profile))
for ref,out,minimum in itertools.product([1,1000000,9999999,12000000,12345678,24000000],[0,1,1000000,2000000,48000000,196608000],[0,60000000,240000000,960000000,0xffffffff]):compare(dict(op='min_vco',reference=ref,output=out,minimum=minimum))
for op in ['generate','min_vco']:
 compare(dict(op=op,nonnull=0,a=bits(12),b=bits(240),reference=12000000,output=48000000))
rng=random.Random(539794)
for i in range(160):
 ref=rng.choice([12000000,24000000,32000000,1000000,12345678]);out=rng.randrange(1000000,970000001)
 compare(dict(op='postdiv',reference=ref,output=out))
 for op in ['integer','fraction','generate']:compare(dict(op=op,a=bits(ref/1000000),b=bits(out/1000000)))
# Nearest representable values around lower/upper/VCO-selector and helper bounds.
for a,b in itertools.product([bits(1),bits(12),bits(24),bits(960)],[bits(60)-1,bits(60),bits(60)+1,bits(240)-1,bits(240),bits(240)+1,bits(960)-1,bits(960),bits(960)+1]):compare(dict(op='generate',a=a,b=b))
(D/'generator-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['All four math providers are reconstructed native code in source guest; original guest executes authenticated instructions. No return stubs.','Full FPSCR, output bytes, status and actual math-provider argument sequence compared.','M33-compatible scalar VFP profile; DIV_0_TRP=0, no exception/IRQ scheduling or physical PLL model.','Native source preserves original quiet comparisons/unordered flags and explicit saturating float conversions.']),separators=(',',':'))+'\n');print('PASS',len(rows),'generator comparisons')
