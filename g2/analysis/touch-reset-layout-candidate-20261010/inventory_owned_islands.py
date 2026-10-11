from pathlib import Path
import hashlib, json, struct, subprocess

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
candidate=ROOT/'g2/components/touch/reset_layout_candidate_20261010'
archive=ROOT/'g2/components/touch/source_candidate_20261010/build'
firmware=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()
assert hashlib.sha256(firmware).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
payload=firmware[32:]
obj=HERE/'reset_owned_data.o';elf=HERE/'owned_islands.elf'
subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fdata-sections',
                '-Wall','-Wextra','-Werror','-c',str(candidate/'reset_owned_data.c'),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-T',str(candidate/'owned_islands.ld'),str(obj),str(archive/'provider__reset_data.o'),'-o',str(elf)],check=True)
loads=subprocess.check_output(['arm-none-eabi-readelf','-l','-W',str(elf)],text=True)
for vma,lma,size in [(0x200004c0,0xb58c,12),(0x2000086c,0xb938,4),(0x20000870,0xb93c,1),(0x20000874,0xb940,4),(0x20000878,0xb944,4)]:
    assert any(int(parts[2],16)==vma and int(parts[3],16)==lma and int(parts[4],16)==size
               for line in loads.splitlines() if (parts:=line.split()) and parts[0]=='LOAD'),(vma,lma,size)
for section,lma,size in [('.touch_config',0xb58c,12),('.touch_delay32k',0xb938,4),('.touch_delay_mhz',0xb93c,1),('.touch_delay_khz',0xb940,4),('.touch_system_clock',0xb944,4)]:
    out=HERE/'section.tmp'
    subprocess.run(['arm-none-eabi-objcopy','--dump-section',f'{section}={out}',str(elf)],check=True)
    assert out.read_bytes()==payload[lma-0x3300:lma-0x3300+size],section
    out.unlink()
data=payload[0xb58c-0x3300:0xb950-0x3300]
words=struct.unpack('<241I',data)
def shape(value):
    if value==0:return 'zero'
    if 0x3300<=value<0xba00:return 'flash-range address candidate'
    if 0x20000000<=value<0x20002000:return 'RAM-range address candidate'
    if 0x40000000<=value<0x50000000:return 'peripheral-range address candidate'
    return 'other value'
records=[]
for i,value in enumerate(words):
    if i<=2:owner='source-owned EEPROM configuration; absolute island PASS'
    elif i in (235,236,237):owner='source-owned delay initializer; absolute island PASS'
    elif i==238:owner='vendor-source-owned SystemCoreClock reset initializer; absolute island PASS; runtime updates unproved'
    elif i in (239,240):owner='GNU crtbegin binary attribution; source build absent archive'
    else:owner='unowned reset data or padding'
    records.append({'word_index':i,'ram_address':hex(0x200004c0+4*i),'flash_address':hex(0xb58c+4*i),
                    'value':hex(value),'shape':shape(value),'ownership':owner})
receipt={'status':'PASS_PARTIAL_ABSOLUTE_ISLANDS','source_owned_words':7,'source_owned_bytes':25,
         'binary_attributed_crt_words':2,'unowned_words':232,
         'firmware_sha256':hashlib.sha256(firmware).hexdigest(),
         'copy_payload_sha256':hashlib.sha256(data).hexdigest(),
         'source_owned_islands':[{'ram':'0x200004c0','flash':'0xb58c','size':12},
                                 {'ram':'0x2000086c','flash':'0xb938','size':4},
                                 {'ram':'0x20000870','flash':'0xb93c','size':1},
                                 {'ram':'0x20000874','flash':'0xb940','size':4},
                                 {'ram':'0x20000878','flash':'0xb944','size':4}],
         'limits':['Only five disjoint source-owned segments are linked absolutely.',
                   'The other 939 bytes have no production image source/placement here.',
                   'Address-range shapes are heuristics, not relocation ownership.']}
(HERE/'init_word_inventory.json').write_text(json.dumps({'receipt':receipt,'words':records},indent=2)+'\n')
print(json.dumps(receipt))
