#!/usr/bin/env python3
"""Bounded host call/record checks for image-B native 0x1000b91c."""
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_denoise_state_init.c'
HARNESS = r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
volatile uint32_t test_state[4];static uint32_t allocation_bytes,init_word,init_bytes;
static int32_t init_result;static unsigned log_calls;static char log_text[80];
extern int32_t gx8002_image_b_denoise_state_init_1000b91c(void);
void *gx8002_image_b_heap_alloc_alias_10009f2c(uint32_t bytes){allocation_bytes=bytes;return (void*)(uintptr_t)0x12345678u;}
uint32_t gx8002_image_b_audio_word_20_10009f80(void){return 16000u;}
int32_t gx8002_image_b_imcra_state_init_1000e384(uint32_t word,void*memory,uint32_t bytes){init_word=word;init_bytes=bytes;if(memory!=(void*)(uintptr_t)0x12345678u)return 0;return init_result;}
int gx8002_image_b_heap_log_10009934(const char*text,...){++log_calls;snprintf(log_text,sizeof(log_text),"%s",text);return 0;}
static int check(int okay,const char*name){if(!okay){fprintf(stderr,"FAIL %s\n",name);return 1;}return 0;}
int main(void){memset((void*)test_state,0,sizeof(test_state));init_result=1;
 if(check(gx8002_image_b_denoise_state_init_1000b91c()==0&&allocation_bytes==43008&&init_word==16000&&init_bytes==43008&&test_state[2]==0x12345678u&&test_state[3]==1&&log_calls==0,"success"))return 1;
 init_result=0;
 if(check(gx8002_image_b_denoise_state_init_1000b91c()==-1&&test_state[3]==0&&log_calls==1&&strcmp(log_text,"[LVP_MODE_DENOISE]ImcraStateInit Fail!\n")==0,"failure"))return 1;
 puts("2 denoise state-init cuts PASS");return 0;}
'''
with tempfile.TemporaryDirectory(prefix='gx8002-denoise-init-') as temporary:
    work = Path(temporary)
    source = SOURCE.read_text().replace('#include <stdint.h>',
        '#include <stdint.h>\nextern volatile uint32_t test_state[4];')
    source = source.replace('(volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d2bc)',
                            'test_state')
    (work / 'init.c').write_text(source)
    (work / 'h.c').write_text(HARNESS)
    subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    str(work / 'init.c'), str(work / 'h.c'), '-o', str(work / 'test')],
                   check=True)
    result = subprocess.run([str(work / 'test')], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    print(json.dumps({'native_entry': '0x1000b91c', 'cases': 2,
                      'result': 'PASS', 'output': result.stdout.strip(),
                      'limit': 'Host state rebasing and stubbed IMCRA child; native C-SKY execution and denoise runtime are unqualified.'}))
