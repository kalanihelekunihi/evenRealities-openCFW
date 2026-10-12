#!/usr/bin/env python3
"""Bounded host cuts for image-B UART receive packet state logic."""
import json
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[5]
SOURCE=ROOT/'g2/components/gx8002/image_b_sram_candidate/backup_audio_uart_receive_packet.c'
HARNESS=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
uintptr_t test_shared_base;static uint8_t ram[0x2000];
extern int32_t gx8002_image_b_audio_uart_receive_packet_1000ad60(uint32_t,volatile uint8_t*,uint8_t**,uint32_t*);
static int enables,disables,dmas,rings;
uint32_t gx8002_image_b_native_word_at_zero_1000ada6(void){return 0;}
int32_t gx8002_image_b_uart_rx_irq_enable_100046ac(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;enables++;return 0;}
int32_t gx8002_image_b_uart_rx_irq_disable_100046e0(uint32_t a){(void)a;disables++;return 0;}
int32_t gx8002_image_b_uart_dma_receive_100047a4(uint32_t a,uint8_t*b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;dmas++;return 0;}
uint32_t gx8002_image_b_audio_ring_write_10015b64(volatile int32_t*r,const uint8_t*s){(void)r;(void)s;rings++;return 1;}
int32_t gx8002_image_b_audio_uart_rx_irq_1000b198(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
int32_t gx8002_image_b_audio_uart_rx_dma_complete_1000af94(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
static void put32(volatile uint8_t*b,uint32_t o,uint32_t v){*(volatile uint32_t *)(volatile void *)(b+o)=v;}
static uint32_t get32(volatile uint8_t*b,uint32_t o){return *(volatile uint32_t *)(volatile void *)(b+o);}
static int ck(int ok,const char*n){if(!ok){fprintf(stderr,"FAIL %s\n",n);return 1;}return 0;}
static void reset(void){memset(ram,0,sizeof(ram));enables=disables=dmas=rings=0;}
int main(void){test_shared_base=(uintptr_t)ram;volatile uint8_t packet[64];uint8_t bytes[8]={0};uint8_t*input=bytes;uint32_t avail=0;
 reset();memset((void*)packet,0,sizeof(packet));*(volatile uint16_t *)(volatile void *)(packet+4)=1;*(volatile uint16_t *)(volatile void *)(packet+8)=8;put32(packet,16,0x7777);put32(packet,24,0x8888);
 if(ck(gx8002_image_b_audio_uart_receive_packet_1000ad60(0,packet,&input,&avail)==-1&&get32(packet,16)==0&&get32(packet,24)==0&&enables==0,"no_registration"))return 1;
 reset();memset((void*)packet,0,sizeof(packet));packet[7]=1;*(volatile uint16_t *)(volatile void *)(packet+8)=4;
 if(ck(gx8002_image_b_audio_uart_receive_packet_1000ad60(0,packet,&input,&avail)==0&&enables==1&&get32((volatile uint8_t*)ram,0x170)==3&&rings==0,"complete_control"))return 1;
 reset();memset((void*)packet,0,sizeof(packet));*(volatile uint16_t *)(volatile void *)(packet+4)=1;*(volatile uint16_t *)(volatile void *)(packet+8)=8;
 volatile uint8_t*table=(volatile uint8_t *)(test_shared_base+0x310u);put32(table,4,1);put32(table,8,0x6000);put32(table,12,32);
 if(ck(gx8002_image_b_audio_uart_receive_packet_1000ad60(0,packet,&input,&avail)==-1&&enables==1&&get32(packet,16)==0x6000&&get32(table,16)==8&&dmas==0,"registered_no_available"))return 1;
 puts("3 receive packet cuts PASS");return 0;}
'''
with tempfile.TemporaryDirectory(prefix='gx8002-rx-packet-') as t:
 p=Path(t);src=SOURCE.read_text().replace('#include <stdint.h>','#include <stdint.h>\nextern uintptr_t test_shared_base;')
 for address,off in [('0x2002cc20',0),('0x2002cd9c',0x17c),('0x2002cf30',0x310),('0x2002d0f0',0x4d0),('0x2002d770',0xb50)]:
  src=src.replace('UINT32_C('+address+')','(test_shared_base + '+hex(off)+'u)')
 (p/'rebase.c').write_text(src);(p/'h.c').write_text(HARNESS)
 subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror',str(p/'rebase.c'),str(p/'h.c'),'-o',str(p/'t')],check=True)
 x=subprocess.run([str(p/'t')],check=True,capture_output=True,text=True)
 print(json.dumps({'native_entry':'0x1000ad60','cases':3,'result':'PASS','output':x.stdout.strip(),'limit':'Host address rebasing and stubbed children; DMA/IRQ and native C-SKY execution unqualified.'}))
