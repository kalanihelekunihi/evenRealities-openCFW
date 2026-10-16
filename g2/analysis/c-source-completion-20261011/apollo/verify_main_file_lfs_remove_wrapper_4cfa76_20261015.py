#!/usr/bin/env python3
"""Bound the public LittleFS remove wrapper against the authenticated OTA bytes."""
import hashlib, json, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_file_lfs_remove_wrapper_4cfa76.c'
BLOB = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-file-lfs-remove-wrapper-4cfa76'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
NATIVE = bytes.fromhex('80b50022fef72ffd02bd')

def sha(data): return hashlib.sha256(data).hexdigest()

def main():
    payload = BLOB.read_bytes()[32:]
    if sha(payload) != PAYLOAD_SHA:
        raise RuntimeError('stock Main payload changed')
    offset = 0x4cfa76 - 0x438000
    actual = payload[offset:offset + len(NATIVE)]
    if actual != NATIVE:
        raise RuntimeError(('remove wrapper bytes changed', actual.hex()))
    # Four host C calls test the argument and return contract while a stub
    # records the core invocation. The instruction bytes above establish r2=0,
    # BL 0x4ce4dc, and return without changing r0/r1.
    harness = '''#include <stdint.h>
extern int32_t audio_file_lfs_remove_4cfa76(void *,const char *);
static void *got_fs;static const char *got_path;static uint32_t got_option;
static int32_t answer;
int32_t audio_file_lfs_remove_core_4ce4dc(void *f,const char *p,uint32_t o){got_fs=f;got_path=p;got_option=o;return answer;}
int main(void){const char *p[]={"a","/tp_42.bin",0,""};int32_t r[]={0,-2,-5,0x12345678};
for(int i=0;i<4;i++){void *f=(void *)(uintptr_t)(0x100+i*4);answer=r[i];
if(audio_file_lfs_remove_4cfa76(f,p[i])!=r[i]||got_fs!=f||got_path!=p[i]||got_option!=0)return i+1;}return 0;}
'''
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / 'harness.c'; binary = Path(td) / 'test'
        path.write_text(harness)
        subprocess.run(['clang','-std=c11','-O2','-Wall','-Wextra','-Werror',str(SOURCE),str(path),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
    OUT.mkdir(parents=True,exist_ok=True)
    row = {'status':'PASS_BOUNDED_MAIN_FILE_LFS_REMOVE_WRAPPER_NATIVE_C',
           'source':str(SOURCE.relative_to(ROOT)), 'source_sha256':sha(SOURCE.read_bytes()),
           'payload_sha256':PAYLOAD_SHA, 'entry':'0x4cfa76', 'core':'0x4ce4dc',
           'native_bytes':actual.hex(), 'native_c_cases':4,
           'scope':'Exact ten-byte stock wrapper and four host C argument/return cases; core behavior untested.'}
    path = OUT / 'oracle.json'; path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],row['native_c_cases'],sha(path.read_bytes()))

if __name__ == '__main__': main()
