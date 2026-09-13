# SPDX-License-Identifier: MIT
"""Experimental source admission of typed audio board initialization data."""
import json,shutil
from verify_gx8002_audio_board_storage import verify as startup
from verify_gx8002_audio_board_storage_config import verify as configure
from verify_gx8002_audio_board_storage_output import verify as output_config
from build_gx8002_audio_board_storage import ROOT,IMAGE,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'startup':startup(),'configuration':configure(),'output':output_config()}
    path=ROOT/'build/gx8002-audio-board-storage/storage.elf';elf=Elf32(path.read_bytes(),'board');section=next(s for s in elf.sections if s['name']=='.board');data=elf.contents(section);stock=IMAGE.read_bytes();symbol='open_cfw_audio_board_state'
    assert section['address']==0x200269a4 and len(data)==240 and data==stock[0x189b8:0x18aa8]
    row={'symbol':symbol,'section_name':'.board','ownership_kind':'generated_source_data','compiled_bytes':240,'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':0x189b8,'bytes':240,'sha256':sha(data),'region':'image_a_sram'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'storage.elf')
    files=sorted(p.name for p in (ROOT/'tools').glob('*gx8002_audio_board_storage*.py'))
    files+=['verify_gx8002_uart_loader_setup.py','compare_gx8002_clear_bss.py','execute_gx8002_audio_board_control.py','verify_gx8002_audio_input_config.py','verify_gx8002_audio_input_output.py','gx8002_audio_input_output_oracle.py','analyze_gx8002_gsensor_state_references.py','verify_gx8002_memcpy_source.py']
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid data admission using named pinned SDK fields; no binary input to compilation/linking.','Startup alias and flash transfer modeled; driver boundaries modeled in audio consumer checks. Physical firmware execution and remaining reconstruction incomplete.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-board-storage-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio board data admission checks passed')
