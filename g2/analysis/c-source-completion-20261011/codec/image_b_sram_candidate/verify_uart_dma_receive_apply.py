#!/usr/bin/env python3
"""Bounded source checks for the native image-B UART receive DMA apply."""
import json
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[5]
SOURCE=ROOT/'g2/components/gx8002/image_b_sram_candidate/backup_uart_dma_receive_apply.c'
HARNESS=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern int32_t gx8002_image_b_uart_dma_receive_apply_10004188(volatile uint32_t*,uint32_t,uint32_t);
static int32_t selected;static int invalidates, widths, callbacks, transfers;static uint32_t spec[12],source_arg,dest_arg,length_arg,channel_arg;
void gx8002_image_b_dcache_invalidate_range_10004dd8(uint32_t a,int32_t n){if(a!=0x1234u||n!=32){puts("bad invalidate");}invalidates++;}
int32_t gx8002_image_b_dma_select_10004b6c(void){return selected;}
uint32_t gx8002_image_b_uart_width_code_10004078(uint32_t m,const uint32_t*f,uint32_t use){if(m!=17||*f!=0x55||use!=0){puts("bad width");}widths++;return 9;}
void gx8002_image_b_dma_callback_10004cb8(uint32_t c,uintptr_t cb,uintptr_t ctx){(void)c;(void)cb;(void)ctx;callbacks++;}
void gx8002_image_b_uart_receive_complete_10004054(volatile uint32_t*r){(void)r;}
int32_t gx8002_image_b_dma_transfer_10004ccc(uint32_t s,uint32_t d,int32_t n,uint32_t c,const uint32_t*x){source_arg=s;dest_arg=d;length_arg=(uint32_t)n;channel_arg=c;memcpy(spec,x,sizeof(spec));transfers++;return -1;}
static void reset(void){invalidates=widths=callbacks=transfers=0;memset(spec,0,sizeof(spec));}
static int ck(int ok,const char*n){if(!ok){fprintf(stderr,"FAIL %s\n",n);return 1;}return 0;}
int main(void){volatile uint32_t r[32]={0};r[1]=0x4455;r[0x60/4]=0x1234;r[0x64/4]=32;r[0x34/4]=17;r[0x38/4]=0x55;
 reset();selected=-1;if(ck(gx8002_image_b_uart_dma_receive_apply_10004188(r,0xabcd,48)==-1&&invalidates==1&&widths==0&&transfers==0,"no_dma"))return 1;
 reset();selected=1;r[0]=0;if(ck(gx8002_image_b_uart_dma_receive_apply_10004188(r,0xabcd,48)==0&&r[0x68/4]==1&&widths==2&&callbacks==1&&transfers==1&&source_arg==0xabcd&&dest_arg==0x4455&&length_arg==48&&channel_arg==1&&spec[3]==6&&spec[1]==9&&spec[6]==9&&spec[11]==2,"port0"))return 1;
 reset();r[0]=1;if(ck(gx8002_image_b_uart_dma_receive_apply_10004188(r,0xabcd,48)==0&&spec[3]==4,"port1"))return 1;
 reset();r[0]=2;if(ck(gx8002_image_b_uart_dma_receive_apply_10004188(r,0xabcd,48)==-1&&widths==1&&callbacks==0&&transfers==0&&r[0x68/4]==1,"bad_port"))return 1;
 puts("4 receive DMA cuts PASS");return 0;}
'''
with tempfile.TemporaryDirectory(prefix='gx8002-rx-dma-') as t:
 p=Path(t);(p/'h.c').write_text(HARNESS)
 subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror',str(SOURCE),str(p/'h.c'),'-o',str(p/'t')],check=True)
 x=subprocess.run([str(p/'t')],check=True,capture_output=True,text=True)
 print(json.dumps({'native_entry':'0x10004188','cases':4,'result':'PASS','output':x.stdout.strip(),'limit':'Host stubs for cache/DMA and no physical transfer proof.'}))
