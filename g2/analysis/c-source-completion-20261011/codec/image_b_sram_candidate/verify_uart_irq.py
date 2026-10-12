#!/usr/bin/env python3
"""Bounded host-state checks for the image-B UART IRQ's two status routes."""
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_uart_irq.c'
HARNESS = r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
volatile uint32_t test_uart[64];
uint8_t *test_rx_ptr;const uint8_t *test_tx_ptr;
uint32_t callbacks,last_address,last_first,last_second,last_third;
extern int32_t gx8002_image_b_uart_irq_10004250(int32_t,void*);
void test_callback(uint32_t address,uint32_t first,uint32_t second,uint32_t third){++callbacks;last_address=address;last_first=first;last_second=second;last_third=third;}
static int check(int yes,const char*name){if(!yes){fprintf(stderr,"FAIL %s\n",name);return 1;}return 0;}
static void reset(uint32_t*r){memset(r,0,40*sizeof(*r));memset((void*)test_uart,0,sizeof(test_uart));callbacks=last_address=last_first=last_second=last_third=0;}
int main(void){uint32_t r[40];uint8_t rx[4]={0},tx[4]={0x11,0x22,0x33,0x44};
 reset(r);r[0]=7;r[0x40/4]=1;r[0x50/4]=0xa;r[0x54/4]=0xb;test_uart[2]=4;test_uart[0x84/4]=3;
 if(check(gx8002_image_b_uart_irq_10004250(0,r)==0&&callbacks==1&&last_address==0xa&&last_first==7&&last_second==3&&last_third==0xb,"receive_callback"))return 1;
 reset(r);r[0]=8;r[0x44/4]=1;r[0x48/4]=0xc;r[0x4c/4]=0xd;test_uart[2]=2;test_uart[0xf4/4]=1u<<16;test_uart[0x80/4]=14;
 if(check(gx8002_image_b_uart_irq_10004250(0,r)==0&&callbacks==1&&last_address==0xc&&last_first==8&&last_second==2&&last_third==0xd,"transmit_callback"))return 1;
 reset(r);test_rx_ptr=rx;r[0x40/4]=2;r[0x64/4]=2;r[0x58/4]=0xe;test_uart[2]=4;test_uart[0x84/4]=2;test_uart[0]=0x5a;test_uart[1]=3;
 if(check(gx8002_image_b_uart_irq_10004250(0,r)==0&&rx[0]==0x5a&&rx[1]==0x5a&&test_rx_ptr==rx+2&&r[0x64/4]==0&&test_uart[1]==2&&callbacks==1&&last_address==0xe,"receive_bytes"))return 1;
 reset(r);test_tx_ptr=tx;r[0x44/4]=2;r[0x78/4]=2;r[0x6c/4]=0xf;test_uart[2]=2;test_uart[0xf4/4]=1u<<16;test_uart[0x80/4]=14;test_uart[0x14/4]=64;test_uart[1]=3;
 if(check(gx8002_image_b_uart_irq_10004250(0,r)==0&&test_tx_ptr==tx+2&&r[0x78/4]==0&&test_uart[0]==0x22&&test_uart[1]==1&&callbacks==1&&last_address==0xf,"transmit_bytes"))return 1;
 reset(r);test_rx_ptr=rx;r[0x40/4]=2;r[0x64/4]=2;r[0x2c/4]=1;test_uart[2]=4;test_uart[0x84/4]=2;
 if(check(gx8002_image_b_uart_irq_10004250(0,r)==0&&test_rx_ptr==rx&&r[0x64/4]==2&&callbacks==0,"active_guard"))return 1;
 puts("5 UART IRQ state cuts PASS");return 0;}
'''

with tempfile.TemporaryDirectory(prefix='gx8002-uart-irq-') as temporary:
    work = Path(temporary)
    source = SOURCE.read_text().replace('#include <stdint.h>',
        '#include <stdint.h>\nextern volatile uint32_t test_uart[64];\nextern uint8_t *test_rx_ptr;\nextern const uint8_t *test_tx_ptr;\nextern void test_callback(uint32_t,uint32_t,uint32_t,uint32_t);')
    source = re.sub(r'static void callback_word\(.*?\n}\n\n',
                    'static void callback_word(uint32_t a,uint32_t b,uint32_t c,uint32_t d){test_callback(a,b,c,d);}\n\n',
                    source, count=1, flags=re.S)
    source = source.replace('(volatile uint32_t *)(uintptr_t)record[1]', 'test_uart')
    source = source.replace('(uint8_t *)(uintptr_t)\n                record[0x60u / 4u]', 'test_rx_ptr')
    source = source.replace('(const uint8_t *)(uintptr_t)\n                record[0x74u / 4u]', 'test_tx_ptr')
    source = source.replace('record[0x60u / 4u] += count;', 'test_rx_ptr = destination + count;')
    source = source.replace('record[0x74u / 4u] += count;', 'test_tx_ptr = source + count;')
    (work / 'irq.c').write_text(source)
    (work / 'h.c').write_text(HARNESS)
    subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    str(work / 'irq.c'), str(work / 'h.c'), '-o', str(work / 'test')],
                   check=True)
    result = subprocess.run([str(work / 'test')], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    print(json.dumps({'native_entry': '0x10004250', 'cases': 5,
                      'result': 'PASS', 'output': result.stdout.strip(),
                      'limit': 'Host UART/pointer rebasing and callback logging; native C-SKY execution and physical IRQ interleavings unqualified.'}))
