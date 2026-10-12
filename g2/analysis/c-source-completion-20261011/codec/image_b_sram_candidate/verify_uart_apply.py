#!/usr/bin/env python3
"""Bounded host-state checks for native image-B UART apply branches."""
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_uart_apply.c'
HARNESS = r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
volatile uint32_t test_uart[64];
static uint32_t fifo_depth, irq_line, irq_arg;
static void *irq_handler;
extern int32_t gx8002_image_b_uart_apply_100043a4(volatile uint32_t *);
uint32_t gx8002_image_b_uart_fifo_depth_1000433c(volatile uint32_t *r){(void)r;return fifo_depth;}
int32_t gx8002_image_b_uart_irq_10004250(int32_t l,void*a){(void)l;(void)a;return 0;}
void gx8002_image_b_request_irq_10004844(uint32_t l,int32_t(*h)(int32_t,void*),uint32_t a){irq_line=l;irq_handler=(void*)h;irq_arg=a;}
static int check(int ok,const char*n){if(!ok){fprintf(stderr,"FAIL %s\n",n);return 1;}return 0;}
int main(void){uint32_t rec[40];memset(rec,0,sizeof(rec));memset((void*)test_uart,0,sizeof(test_uart));
 fifo_depth=16;rec[3]=48000000;rec[4]=16;rec[0x3c/4]=9;test_uart[0x9c/4]=1;test_uart[0xa0/4]=2;
 if(check(gx8002_image_b_uart_apply_100043a4(rec)==0&&rec[0x1c/4]==8&&rec[0x20/4]==1&&rec[0x14/4]==187500&&rec[0x18/4]==0&&test_uart[0]==108&&test_uart[1]==92&&test_uart[4]==3&&test_uart[2]==111&&rec[0x38/4]==4&&rec[0x34/4]==4&&irq_line==9&&irq_handler!=0&&irq_arg==(uint32_t)(uintptr_t)rec,"default_fraction_zero"))return 1;
 memset(rec,0,sizeof(rec));memset((void*)test_uart,0,sizeof(test_uart));fifo_depth=15;
 rec[3]=100;rec[4]=3;rec[0x24/4]=1;rec[0x3c/4]=2;test_uart[0x9c/4]=3;test_uart[0xa0/4]=1;
 if(check(gx8002_image_b_uart_apply_100043a4(rec)==0&&rec[0x14/4]==2&&rec[0x18/4]==1&&test_uart[0]==2&&test_uart[1]==0&&test_uart[0xc0/4]==1&&test_uart[4]==34&&test_uart[2]==127&&rec[0x38/4]==13&&rec[0x34/4]==2&&irq_line==2,"fractional_alt_port"))return 1;
 puts("2 UART apply state cuts PASS");return 0;}
'''

with tempfile.TemporaryDirectory(prefix='gx8002-uart-apply-') as temporary:
    work = Path(temporary)
    source = SOURCE.read_text().replace('#include <stdint.h>',
        '#include <stdint.h>\nextern volatile uint32_t test_uart[64];')
    source = source.replace('(volatile uint32_t *)(uintptr_t)record[1]',
                            'test_uart')
    (work / 'apply.c').write_text(source)
    (work / 'h.c').write_text(HARNESS)
    subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    str(work / 'apply.c'), str(work / 'h.c'), '-o', str(work / 'test')],
                   check=True)
    result = subprocess.run([str(work / 'test')], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    print(json.dumps({'native_entry': '0x100043a4', 'cases': 2,
                      'result': 'PASS', 'output': result.stdout.strip(),
                      'limit': 'Host MMIO rebasing and stubbed FIFO/IRQ; C-SKY binary64 rounding and physical UART not qualified.'}))
