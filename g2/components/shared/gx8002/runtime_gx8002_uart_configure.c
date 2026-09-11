/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_uart_fifo_depth(volatile uint32_t *);
extern int open_cfw_gx8002_uart_interrupt(int,void *);
extern void open_cfw_gx8002_request_irq(int,int (*)(int,void *),void *);
/* Recovered configuration candidate. Floating-point helper lineage and the
 * full ordered MMIO trace require qualification before firmware admission. */
int open_cfw_gx8002_uart_configure(volatile uint32_t *d)
{
    if (!d[7]) d[7]=8;
    if (!d[8]) d[8]=1;
    volatile uint32_t *device=(volatile uint32_t *)(uintptr_t)d[1];
    device[1]=0;
    device[4]=d[9]?34:3;
    device[2]=d[9]?127:111;
    uint32_t baud=d[4];
    if (baud) {
        uint32_t clock=d[3];
        uint32_t denominator=baud<<4;
        uint32_t divisor=clock/denominator;
        uint32_t remainder=clock-divisor*denominator;
        d[5]=divisor;
        d[6]=(uint32_t)(((double)remainder/(double)denominator)*16.0+0.5);
        device[2]=0;
        uint32_t control=device[3];
        device[3]=control|128;
        device[0]=divisor&255;
        device[1]=(divisor>>8)&255;
        device[0x30]=*(volatile uint8_t *)((volatile uint8_t *)d+24);
        device[3]=control;
        device[2]=d[9]?127:111;
    }
    device[2]=0;
    device[3]=(device[3]&~31u)|3u;
    device[2]=d[9]?127:111;
    int32_t depth=(int32_t)open_cfw_gx8002_uart_fifo_depth(d);
    volatile uint32_t *current=(volatile uint32_t *)(uintptr_t)d[1];
    d[12]=(uint32_t)depth;
    uint32_t receive=current[0x27];
    uint32_t transmit=current[0x28];
    switch (receive) {
    case 0:d[14]=1;break;
    case 1:d[14]=(uint32_t)(depth/4);break;
    case 2:d[14]=(uint32_t)(depth/2);break;
    case 3:d[14]=(uint32_t)depth-2u;break;
    }
    switch (transmit) {
    case 0:d[13]=0;break;
    case 1:d[13]=2;break;
    case 2:d[13]=(uint32_t)(depth/4);break;
    case 3:d[13]=(uint32_t)(depth/2);break;
    }
    d[11]=1;
    uint32_t irq=d[15];
    d[26]=UINT32_MAX;
    d[31]=UINT32_MAX;
    open_cfw_gx8002_request_irq((int)irq,open_cfw_gx8002_uart_interrupt,(void *)d);
    return 0;
}
