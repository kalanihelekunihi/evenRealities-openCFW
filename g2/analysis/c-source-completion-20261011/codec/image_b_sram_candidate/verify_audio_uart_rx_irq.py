#!/usr/bin/env python3
"""Bounded host state cuts of image-B native RX IRQ, with SRAM rebasing."""
import json
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[5]
SOURCE=ROOT/'g2/components/gx8002/image_b_sram_candidate/backup_audio_uart_rx_irq.c'
HARNESS=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
uintptr_t test_shared_base;uint8_t *test_scratch_ptr;static uint8_t ram[0x2000],stream[64];static uint32_t crc_value;static int rings,crc_calls;
extern int32_t gx8002_image_b_audio_uart_rx_irq_1000b198(uint32_t,uint32_t);
int32_t gx8002_image_b_uart_poll_read_100045d8(uint32_t p,uint8_t*d,int32_t n){(void)p;if(n>0)memcpy(d,stream,(size_t)n);return n;}
int32_t gx8002_image_b_audio_uart_receive_packet_1000ad60(uint32_t c,volatile uint8_t*p,uint8_t**i,uint32_t*a){(void)c;(void)p;(void)i;(void)a;return 0;}
uint32_t gx8002_image_b_audio_ring_write_10015b64(volatile int32_t*r,const uint8_t*s){(void)r;(void)s;rings++;return 1;}
uint32_t gx8002_image_b_crc32_1000c5c4(uint32_t s,const unsigned char*d,unsigned int n){(void)s;(void)d;(void)n;crc_calls++;return crc_value;}
static uint32_t get(uint32_t off){return *(uint32_t *)(void *)(ram+off);}static void put(uint32_t off,uint32_t v){*(uint32_t *)(void *)(ram+off)=v;}
static int ck(int ok,const char*n){if(!ok){fprintf(stderr,"FAIL %s\n",n);return 1;}return 0;}
static void reset(void){memset(ram,0,sizeof(ram));memset(stream,0,sizeof(stream));rings=crc_calls=0;}
int main(void){test_shared_base=(uintptr_t)ram;
 reset();put(0,0x44332211u);stream[0]=0x11;stream[1]=0x22;stream[2]=0x33;stream[3]=0x44;
 if(ck(gx8002_image_b_audio_uart_rx_irq_1000b198(0,4)==0&&get(0x1c)==0x44332211u&&get(0x170)==1u,"sync_search"))return 1;
 reset();put(0x170,1);put(0x1200,4);
 stream[4]=8;stream[6]=0x44;stream[7]=0x33;stream[8]=0x22;stream[9]=0x11;crc_value=0x11223344u;
 if(ck(gx8002_image_b_audio_uart_rx_irq_1000b198(0,10)==0&&get(0x170)==2u&&crc_calls==1&&rings==0,"header_crc"))return 1;
 reset();put(0x170,3);stream[0]=1;stream[1]=2;stream[2]=3;stream[3]=4;
 if(ck(gx8002_image_b_audio_uart_rx_irq_1000b198(0,4)==0&&get(0x38)==0x04030201u&&get(0x170)==0u&&rings==1,"trailing_crc"))return 1;
 if(ck(gx8002_image_b_audio_uart_rx_irq_1000b198(2,1)==-1,"invalid_port"))return 1;
 puts("4 RX IRQ state cuts PASS");return 0;}
'''
with tempfile.TemporaryDirectory(prefix='gx8002-rx-irq-') as t:
 p=Path(t);src=SOURCE.read_text().replace('#include <stdint.h>','#include <stdint.h>\nextern uintptr_t test_shared_base;\nextern uint8_t *test_scratch_ptr;')
 for address,off in [('0x2002cc20',0),('0x2002cd9c',0x17c),('0x2002d0f0',0x4d0),('0x20016f64',0x1200),('0x2002d770',0xb50)]:
  src=src.replace('UINT32_C('+address+')','(test_shared_base + '+hex(off)+'u)')
 src=src.replace('store32(shared, 0x588u, (uint32_t)(uintptr_t)scratch);','test_scratch_ptr = scratch;')
 src=src.replace('uint8_t *input = (uint8_t *)(uintptr_t)load32(shared, 0x588u);','uint8_t *input = test_scratch_ptr;')
 src=src.replace('store32(shared, 0x588u, (uint32_t)(uintptr_t)input);','test_scratch_ptr = input;')
 src=src.replace('store32(shared, 0x588u, (uint32_t)(uintptr_t)(input + count));','test_scratch_ptr = input + count;')
 src=src.replace('uint8_t **input = (uint8_t **)(uintptr_t)\n                ((test_shared_base + 0x0u) + 0x588u);','uint8_t **input = &test_scratch_ptr;')
 (p/'rebase.c').write_text(src);(p/'h.c').write_text(HARNESS)
 subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror',str(p/'rebase.c'),str(p/'h.c'),'-o',str(p/'t')],check=True)
 x=subprocess.run([str(p/'t')],capture_output=True,text=True)
 if x.returncode: raise RuntimeError(x.stdout+x.stderr)
 print(json.dumps({'native_entry':'0x1000b198','cases':4,'result':'PASS','output':x.stdout.strip(),'limit':'Host SRAM/pointer rebasing and stubbed children; native instruction trace and physical IRQ interleavings unqualified.'}))
