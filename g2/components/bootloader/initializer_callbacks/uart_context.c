/* Locked f89a4c46 bootloader UART reconstruction. Volatile stores retain the
 * observed order; activation borrows buffers. No allocation or drain claim. */
#include "uart_context.h"
#include "../platform_control/power_domains.h"
#include "../clock_manager/clock_manager.h"
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define H(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
#define POOL 0x20024400u
#define UART 0x40039000u
#define HIGH_BAUD 1500001u
__attribute__((section(".bss.boot_uart_context_pool"),used))
volatile opencfw_boot_uart_context opencfw_boot_uart_context_pool[4];
static uint32_t valid(uint32_t p) {return p&&(R(p)&0x01ffffffu)==0x01ea9e06u;}
NI uint32_t opencfw_bl_post_context_register(uint32_t module,const void *output) {
    if(module>=4)return 5;
    if(!output)return 6;
    uintptr_t out=(uintptr_t)output;
    if(R(out)&&valid(R(out)))return 7;
    uint32_t p=POOL+module*0x11cu;
    R(p)|=0x01000000u;R(p)=(R(p)&0xff000000u)|0x00ea9e06u;
    R(p+0x28)=module;B(p+4)=0;R(p+0x30)=0;
    B(p+0x11a)=0;B(p+0x119)=0;B(p+0xdc)=0;B(p+0xdd)=0;
    R(p+0xd8)=0;R(p+0x9c)=0;B(p+0xde)=1;R(out)=p;
    return 0;
}
/* Original 4275ea; no copy, allocation, or ownership transfer. */
NI void opencfw_boot_uart_ring_initialize(uint32_t p,uint32_t buffer,uint32_t width,uint32_t capacity) {
    R(p)=0;R(p+4)=0;R(p+8)=0;R(p+12)=capacity;R(p+16)=width;R(p+20)=buffer;
}
NI uint32_t opencfw_bl_post_activate(uint32_t p,uint32_t tx,uint32_t tx_capacity,uint32_t rx,uint32_t rx_capacity) {
    if(!valid(p))return 2;
    B(p+0xdc)=0;B(p+0xdd)=0;
    if(tx&&tx_capacity){B(p+0xdc)=1;opencfw_boot_uart_ring_initialize(p+0x34,tx,1,tx_capacity);}
    if(rx&&rx_capacity){B(p+0xdd)=1;opencfw_boot_uart_ring_initialize(p+0x4c,rx,1,rx_capacity);}
    return 0;
}
NI uint32_t opencfw_bl_post_finish(uint32_t p,uint32_t mask) {
    uint32_t module=R(p+0x28); /* Original reads before null/magic guard. */
    if(!valid(p))return 2;
    R(UART+(module<<12)+0x38)|=mask;return 0;
}
NI uint32_t opencfw_boot_uart_interrupt_clear(uint32_t p,uint32_t mask) {
    uint32_t module=R(p+0x28);
    if(!valid(p))return 2;
    R(UART+(module<<12)+0x44)=mask;(void)R(UART+(module<<12)+0x40);return 0;
}
/* Accepted branch of 422ba8. Existing native guard retains error precedence. */
NI uint32_t opencfw_boot_control_power_apply_configure(uint32_t *object,uint32_t operation,uint8_t save) {
    uint32_t p=(uint32_t)(uintptr_t)object,module=R(p+0x28),user=(uint8_t)(module+11),base=UART+(module<<12);
    const uint32_t offsets[8]={0x20,0x24,0x28,0x2c,0x30,0x34,0x38,0x48};
    if(operation==0) {
        if(save&&!B(p+4))return 7;
        (void)opencfw_bl_mspi_mode_enter(user);
        if(save) {
            if(R(p+0x30)>=HIGH_BAUD&&(R(0x4002000c)&255u)>=34)R(0x400201b0)|=0x400000u<<module;
            (void)clock_request(B(p+0x118),user);
            for(uint32_t i=0;i<8;i++)R(base+offsets[i])=R(p+8+4*i);
            B(p+4)=0;
        }
    } else {
        if(save){for(uint32_t i=0;i<8;i++)R(p+8+4*i)=R(base+offsets[i]);B(p+4)=1;}
        if(R(p+0x30)>=HIGH_BAUD&&(R(0x4002000c)&255u)>=34)R(0x400201b0)&=~(0x400000u<<module);
        (void)clock_release(B(p+0x118),user);
        (void)opencfw_boot_uart_interrupt_clear(p,0xffffffffu);
        R(base+0x30)=0;(void)opencfw_bl_mspi_mode_leave(user);
    }
    return 0;
}
static uint32_t udiv(uint32_t n,uint32_t d) {uint32_t q;__asm__("udiv %0,%1,%2":"=r"(q):"r"(n),"r"(d));return q;}
/* Specialization of the 42287c call: UART always supplies a 32-bit divisor.
 * Its zero-divisor path jumps to 4275e8 (BX LR), retaining numerator R0/R1.
 * This is not a reconstruction of all entry paths of the division helper. */
static uint64_t quotient(uint64_t n,uint32_t d) {
    if(!d)return n;
    uint64_t q=0,r=0;
    for(uint32_t i=64;i;i--){r=(r<<1)|((n>>(i-1))&1u);if(r>=d){r-=d;q|=(uint64_t)1<<(i-1);}}
    return q;
}
NI uint32_t opencfw_boot_uart_baud(uint32_t module,uint32_t baud,uint32_t *actual) {
    uint32_t base=UART+(module<<12),selector=(R(base+0x30)>>4)&7u,f;
    switch(selector){case 1:f=24000000;break;case 2:f=12000000;break;case 3:f=6000000;break;case 4:f=3000000;break;case 5:f=48000000;break;case 6:f=49152000;break;default:*(volatile uint32_t *)actual=0;return 0x08000002;}
    uint32_t d=baud<<4,integer=udiv(f,d),fraction=(uint32_t)(quotient((uint64_t)f<<6,d)-((uint64_t)integer<<6));
    if(!integer){*(volatile uint32_t *)actual=0;return 0x08000003;}
    R(base+0x24)=integer;R(base+0x28)=fraction;
    *(volatile uint32_t *)actual=udiv(f,(fraction>>2)+(integer<<4));return 0;
}
NI uint32_t opencfw_bl_post_validate(uint32_t p,uint32_t config) {
    if(!valid(p))return 2;
    uint32_t module=R(p+0x28),base=UART+(module<<12);
    R(base+0x30)=0;R(base+0x30)|=8;
    if(B(config+12)>=2||(B(config+12)==1&&(R(0x4002000c)&255u)==33))return 6;
    B(p+0x118)=B(config+12)==0?4:6;
    uint32_t high=R(config)>=HIGH_BAUD;
    if((R(0x4002000c)&255u)>=34){if(high)R(0x400201b0)|=0x400000u<<module;else R(0x400201b0)&=~(0x400000u<<module);}
    uint32_t selector=B(p+0x118)==6?6:high?5:1;
    R(base+0x30)=(R(base+0x30)&~0x70u)|(selector<<4);
    (void)clock_request(B(p+0x118),(uint8_t)(module+11));
    R(base+0x30)&=~1u;R(base+0x30)&=~0x200u;R(base+0x30)&=~0x100u;
    uint32_t status=opencfw_boot_uart_baud(module,R(config),(uint32_t *)(uintptr_t)(p+0x30));if(status)return status;
    R(base+0x30)&=~0x4000u;R(base+0x30)&=~0x8000u;R(base+0x30)|=H(config+8);
    uint32_t parity=B(config+5),enabled=parity<2,odd=parity==1;
    R(base+0x2c)&=~1u;R(base+0x2c)=(R(base+0x2c)&~2u)|(enabled<<1);
    R(base+0x2c)=(R(base+0x2c)&~4u)|(odd<<2);
    R(base+0x2c)=(R(base+0x2c)&~8u)|((B(config+6)&1u)<<3);
    R(base+0x2c)|=0x10;R(base+0x2c)=(R(base+0x2c)&~0x60u)|((B(config+4)&3u)<<5);R(base+0x2c)&=~0x80u;
    R(base+0x34)=(R(base+0x34)&~7u)|(B(config+10)&7u);
    R(base+0x34)=(R(base+0x34)&~0x38u)|((B(config+11)&7u)<<3);
    R(base+0x30)|=1;R(base+0x30)|=0x200;R(base+0x30)|=0x100;return 0;
}
/* Names retained for existing row-loop ABI. Exact addresses determine action. */
NI uint32_t opencfw_bl_post_enable(uint32_t irq) {
    int32_t n=(int16_t)irq;if(n<0)return irq;
    uint32_t index=(uint32_t)n>>5;R(0xe000e280u+4*index)=1u<<(irq&31);return index;
}
NI uint32_t opencfw_bl_post_precommit(uint32_t irq) {
    int32_t n=(int16_t)irq;if(n<0)return irq;
    uint32_t index=(uint32_t)n>>5;R(0xe000e100u+4*index)=1u<<(irq&31);return index;
}
NI uint32_t opencfw_bl_register_mode(uint32_t irq,uint32_t priority) {
    int32_t n=(int16_t)irq;
    if(n>=0){B(0xe000e400u+(uint32_t)n)=(uint8_t)(priority<<4);return (uint32_t)n;}
    uint32_t address=0xe000ed18u+(irq&15);B(address-4)=(uint8_t)(priority<<4);return address;
}
