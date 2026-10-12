#!/usr/bin/env python3
"""Host rebase of ISA-derived IMCRA record layout and branch cuts."""
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_imcra_state_init.c'
HARNESS = r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static unsigned power_calls,cosine_calls,log_calls;static char last_log[100];
extern int32_t gx8002_image_b_imcra_state_init_1000e384(uint32_t,void*,uint32_t);
extern uint32_t gx8002_image_b_imcra_required_1000e314(const uint32_t*,uint32_t);
float gx8002_image_b_power_float_100100a4(float b,float e){++power_calls;return b+e;}
float gx8002_image_b_cosine_lookup_1000ee64(float a){(void)a;++cosine_calls;return 0.0f;}
void gx8002_image_b_zero_100113c4(void*p,uint32_t v,uint32_t n){memset(p,(int)v,n);}
int gx8002_image_b_heap_log_10009934(const char*s,...){++log_calls;snprintf(last_log,sizeof(last_log),"%s",s);return 0;}
static int check(int yes,const char*name){if(!yes){fprintf(stderr,"FAIL %s\n",name);return 1;}return 0;}
int main(void){static uint32_t area[10752];uint8_t*bytes=(uint8_t*)area;memset(area,0xa5,sizeof(area));
 if(check(gx8002_image_b_imcra_state_init_1000e384(16000,area,195)==0&&log_calls==1&&strstr(last_log,"At least sizeof")!=0,"small_header"))return 1;
 log_calls=0;if(check(gx8002_image_b_imcra_state_init_1000e384(16000,area,42319)==0&&log_calls==1&&strstr(last_log,"required size")!=0,"required_guard"))return 1;
 log_calls=power_calls=cosine_calls=0;memset(area,0xa5,sizeof(area));
 if(check(gx8002_image_b_imcra_state_init_1000e384(16000,area,43008)!=0&&gx8002_image_b_imcra_required_1000e314(area,2)==42124&&area[0x24/4]==196&&area[0x30/4]==1732&&area[0x88/4]==11488&&area[0x90/4]==20740&&area[0xa8/4]==34104&&area[0xac/4]==35132&&area[0xb8/4]==37192&&power_calls==1&&cosine_calls==513&&log_calls==3,"layout_and_calls"))return 1;
 if(check(bytes[196]==0&&bytes[196+1023]==0&&*(uint32_t*)(void*)(bytes+34104)==0x3f800000u&&*(uint32_t*)(void*)(bytes+29992)==0x3f800000u&&*(float*)(void*)(bytes+35132)==1.0f,"initialized_regions"))return 1;
 puts("4 IMCRA state/layout cuts PASS");return 0;}
'''

with tempfile.TemporaryDirectory(prefix='gx8002-imcra-') as temporary:
    work = Path(temporary)
    source = SOURCE.read_text()
    source = source.replace('state[field / 4u] = (uint32_t)*cursor;',
                            'state[field / 4u] = (uint32_t)(*cursor - (uintptr_t)state);')
    for field in ('0xa8u', '0x98u', '0xacu', '0x30u', '0x34u', '0x24u'):
        source = source.replace('(uintptr_t)state[' + field + ' / 4u]',
                                '((uintptr_t)state + state[' + field + ' / 4u])')
    (work / 'imcra.c').write_text(source)
    (work / 'h.c').write_text(HARNESS)
    subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    str(work / 'imcra.c'), str(work / 'h.c'), '-o', str(work / 'test')],
                   check=True)
    result = subprocess.run([str(work / 'test')], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    print(json.dumps({'native_entry': '0x1000e384', 'cases': 4,
                      'result': 'PASS', 'output': result.stdout.strip(),
                      'limit': 'Host pointer rebasing and stubbed power/cosine; C-SKY FPU rounding, lookup table, and audio runtime remain unqualified.'}))
