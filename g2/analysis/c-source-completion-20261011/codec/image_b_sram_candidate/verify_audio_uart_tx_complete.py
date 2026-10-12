#!/usr/bin/env python3
"""Bounded host checks of native-state cuts in the image-B TX callback."""
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_audio_uart_tx_complete.c'
HARNESS = r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
uintptr_t test_shared_base;
static uint8_t ram[0x2000];
extern int32_t gx8002_image_b_audio_uart_tx_complete_1000afc4(uint32_t,uint32_t);
static uint32_t writes, write_count, crc_calls, unmarks, starts, segment_calls;
int32_t gx8002_image_b_audio_uart_segment_send_1000ab7c(uint32_t a,const uint8_t*b,uint32_t*c){(void)a;(void)b;(void)c;segment_calls++;return 1;}
int32_t gx8002_image_b_uart_poll_write_buffer_10004614(uint32_t a,const uint8_t*b,int32_t c){(void)a;(void)b;writes++;write_count=(uint32_t)c;return c;}
uint32_t gx8002_image_b_crc32_1000c5c4(uint32_t a,const unsigned char*b,unsigned int c){(void)a;(void)b;(void)c;crc_calls++;return 0xaabbccddu;}
uint32_t gx8002_image_b_audio_resource_unmark_1000a8c4(int32_t a){(void)a;unmarks++;return 0;}
int32_t gx8002_image_b_audio_uart_tx_start_1000ab10(uint32_t a){(void)a;starts++;return -1;}
static volatile uint32_t *at(uintptr_t address){return (volatile uint32_t *)(uintptr_t)address;}
static void reset(void){memset(ram,0,sizeof(ram));writes=write_count=crc_calls=unmarks=starts=segment_calls=0;}
static int check(int ok,const char*name){if(!ok){fprintf(stderr,"FAIL %s\n",name);return 1;}return 0;}
int main(void){
 test_shared_base=(uintptr_t)ram;
 uintptr_t state=test_shared_base;
reset(); *at(state+0x174u)=0u;
 if(check(gx8002_image_b_audio_uart_tx_complete_1000afc4(0,5)==0 && writes==1 && write_count==5 && *at(state+0x510u)==5u && *at(state+0x174u)==0u,"header_partial"))return 1;
reset(); *at(state+0x174u)=0u;
 if(check(gx8002_image_b_audio_uart_tx_complete_1000afc4(0,14)==0 && writes==1 && write_count==14 && *at(state+0x510u)==0u && *at(state+0x174u)==3u,"header_finish"))return 1;
 reset(); *at(state+0x174u)=1u;
 if(check(gx8002_image_b_audio_uart_tx_complete_1000afc4(0,0)==0 && segment_calls==1 && *at(state+0x174u)==3u,"payload_finish"))return 1;
 reset(); *at(state+0x174u)=2u; *at(state+0x4cu)=state+0x80u;*at(state+0x54u)=8u;
 if(check(gx8002_image_b_audio_uart_tx_complete_1000afc4(0,4)==0 && crc_calls==1 && *at(state+0x520u)==0xaabbccddu && writes==1 && write_count==4 && *at(state+0x174u)==3u,"crc_finish"))return 1;
 reset(); *at(state+0x174u)=3u;((volatile uint8_t *)(uintptr_t)(state+0x3cu))[0x14u]=2u;
 if(check(gx8002_image_b_audio_uart_tx_complete_1000afc4(0,1)==0 && starts==1 && unmarks==0,"finish_other_kind"))return 1;
 reset(); *at(state+0x174u)=3u; *at(state+0x178u)=9u;*((volatile uint16_t *)(uintptr_t)(state+0x40u))=1u;
 if(check(gx8002_image_b_audio_uart_tx_complete_1000afc4(0,1)==0 && starts==1 && unmarks==1,"finish_owner"))return 1;
 if(check(gx8002_image_b_audio_uart_tx_complete_1000afc4(2,1)==-1,"bad_channel"))return 1;
 puts("7 bounded state cuts PASS");return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='gx8002-tx-callback-') as tmp:
    tmp = Path(tmp)
    harness = tmp / 'harness.c'
    transformed = tmp / 'address_rebased_source.c'
    binary = tmp / 'check'
    harness.write_text(HARNESS)
    source_text = SOURCE.read_text().replace('#include <stdint.h>', '#include <stdint.h>\nextern uintptr_t test_shared_base;')
    source_text = source_text.replace('UINT32_C(0x2002cc20)', 'test_shared_base')
    source_text = source_text.replace('UINT32_C(0x2002cd9c)', '(test_shared_base + 0x17cu)')
    source_text = source_text.replace('UINT32_C(0x2002d148)', '(test_shared_base + 0x528u)')
    transformed.write_text(source_text)
    subprocess.run(['clang', '-std=c11', '-D_DARWIN_C_SOURCE', '-Wno-deprecated-declarations',
                    '-Wall', '-Wextra', '-Werror', str(transformed), str(harness), '-o', str(binary)], check=True)
    result = subprocess.run([str(binary)], capture_output=True, text=True)
    if result.returncode: raise RuntimeError(result.stdout + result.stderr or f"exit {result.returncode}")
    print(json.dumps({'native_entry':'0x1000afc4','cases':7,'result':'PASS','output':result.stdout.strip(),
                      'limit':'Host address rebasing and stubbed children; native instruction trace and physical IRQ interleavings unqualified.'}))
