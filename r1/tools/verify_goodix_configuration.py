#!/usr/bin/env python3
"""Compare compiled public-source Goodix configuration with authenticated stock."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, __version__ as unicorn_version
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output=ROOT/'r1/research/source-build/goodix';receipt=output/'configuration-verification.json'
    receipt.unlink(missing_ok=True)
    application=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=application.read_bytes()
    assert sha(application)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((output/'report.json').read_text());assert report['compiled']==report['total']==16
    for row in report['units']:
        assert sha(ROOT/row['source'])==row['source_sha256']
        assert sha(Path(row['command'][-1]))==row['object_sha256']
        assert sha(ROOT/row['original_source'])==row['original_source_sha256']
    configurations=[('goodix_hba_config.c','external_hba_cfg','goodix_hba_config_get_arr','goodix_hba_config_get_size',0xad13c,36),
                    ('goodix_hrv_config.c','external_hrv_cfg','goodix_hrv_config_get_arr','goodix_hrv_config_get_size',0x9d5ec,24),
                    ('goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c','external_cfg','goodix_spo2_config_get_instance','goodix_spo2_config_get_size',0xad160,76)]
    records=[]
    with tempfile.TemporaryDirectory(prefix='r1-goodix-config-') as temporary:
        temp=Path(temporary);objects=[];roots=[]
        for name,symbol,getter,size_getter,address,size in configurations:
            row=next(row for row in report['units'] if Path(row['original_source']).name==name)
            obj=Path(row['command'][-1]);objects.append(obj);roots.extend([getter,size_getter]);datafile=temp/(symbol+'.bin')
            subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.rodata.'+symbol,str(obj),str(datafile)],check=True)
            data=datafile.read_bytes();expected=image[address-0x27000:address-0x27000+size]
            assert len(data)==size and data==expected,name
            records.append(dict(source=row['source'],original_source=row['original_source'],symbol=symbol,stock_address=hex(address),bytes=size,sha256=hashlib.sha256(data).hexdigest()))
        # Confirm that only three declared calibration fields need changing.
        spo2_row=next(row for row in report['units'] if Path(row['original_source']).name.startswith('goodix_spo2_config_for_'));command=list(spo2_row['command']);command[command.index('-c')+1]=str(ROOT/spo2_row['original_source']);command[-1]=str(temp/'public-spo2.o')
        subprocess.run(command,check=True)
        baseline=temp/'public-spo2.bin'
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.rodata.external_cfg',command[-1],str(baseline)],check=True)
        public=baseline.read_bytes();stock=image[0xad160-0x27000:0xad1ac-0x27000]
        assert len(public)==len(stock)==76
        assert public[:16]==stock[:16] and public[28:]==stock[28:]
        assert struct.unpack_from('<iii',public,16)==(-124026,-59505,1043941)
        assert struct.unpack_from('<iii',stock,16)==(-156022,-42041,1066184)
        elf=temp/'config.elf';binary=temp/'config.bin'
        subprocess.run(['arm-none-eabi-ld','-Ttext=0x01000000','--gc-sections','--entry='+roots[0],
                        *['--undefined='+name for name in roots],*map(str,objects),'-o',str(elf)],check=True)
        assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
        subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
        lines=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
        symbols={line.split()[-1]:int(line.split()[0],16) for line in lines if len(line.split())==3}
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x1000000,0x10000);uc.mem_write(0x1000000,binary.read_bytes());uc.mem_map(0x20000000,0x10000)
        stop=0x20000100;uc.mem_write(stop,b'\x00\xbe')
        def call(name):
            uc.reg_write(UC_ARM_REG_SP,0x2000f000);uc.reg_write(UC_ARM_REG_LR,stop|1)
            uc.emu_start(symbols[name]|1,stop,count=1000);assert uc.reg_read(UC_ARM_REG_PC)==stop
            return uc.reg_read(UC_ARM_REG_R0)
        for name,symbol,getter,size_getter,address,size in configurations:
            pointer=call(getter);assert bytes(uc.mem_read(pointer,size))==image[address-0x27000:address-0x27000+size]
            assert call(size_getter)==size
    record=dict(application_sha256=sha(application),upstream_pin=report['upstream_pin'],configurations=records,
                getter_checks=6,unicorn_version=unicorn_version,
                public_spo2_sha256=hashlib.sha256(public).hexdigest(),stock_spo2_sha256=hashlib.sha256(stock).hexdigest(),
                calibration_patch={'fields':['cali_coef_a2','cali_coef_a1','cali_coef_a0'],'offsets':[16,20,24],
                                   'public':[-124026,-59505,1043941],'stock':[-156022,-42041,1066184]},
                scope='136 compiled configuration bytes equal authenticated stock; six linked getter/size results checked',
                limitations=['Getter code location and instruction bytes are not matched to stock.','No algorithm output, calibration suitability or physical sensor behavior is established.','Full Goodix component and application links remain unresolved.'],
                application_linked=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    print('136 compiled configuration bytes match stock; 6 linked getter checks passed; SpO2 delta confined to three calibration words')


if __name__=='__main__':main()
