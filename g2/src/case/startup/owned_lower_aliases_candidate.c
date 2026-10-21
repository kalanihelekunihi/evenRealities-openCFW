/* SPDX-License-Identifier: MIT
 * Exact native target aliases shared with the source-owned command graph.
 * Their return values are not consumed by these startup/parser callers.
 */
#include <stdint.h>
extern uint32_t case_binary_5e_wait(uint32_t ticks); /* 0x08004958 */
extern void log_hex_buffer(const uint8_t *bytes,uint32_t count); /* 0x080067c8 */
extern void case_send(const uint8_t *bytes,uint32_t count); /* 0x0800680c */
void case_init_wait(uint32_t ticks){(void)case_binary_5e_wait(ticks);}
void case_init_hex_log(const uint8_t *bytes,uint32_t count){log_hex_buffer(bytes,count);}
void case_record_hex_log(const uint8_t *bytes,uint32_t count){log_hex_buffer(bytes,count);}
void case_record_forward(const uint8_t *bytes,uint32_t count){case_send(bytes,count);}
/* Native 0x08004e94 and 0x08004eb8/4ec4/4ed0 use these register offsets. */
uint32_t case_init_pin_read(uint32_t base,uint32_t mask)
{return (*(volatile uint32_t *)(uintptr_t)(base+0x10u)&mask)!=0u;}
uint32_t case_init_id2(void)
{return *(volatile uint32_t *)(uintptr_t)0x1fff7590u;}
uint32_t case_init_id1(void)
{return *(volatile uint32_t *)(uintptr_t)0x1fff7594u;}
uint32_t case_init_id0(void)
{return *(volatile uint32_t *)(uintptr_t)0x1fff7598u;}
/* Stock 0x08005094, 0x080050a8, 0x080050c4 register sequence. */
void case_init_wake_mask(uint32_t mask)
{volatile uint32_t *r=(volatile uint32_t *)(uintptr_t)0x40007000u;r[2]&=~(mask&0x3fu);}
void case_init_wake_config(uint32_t value)
{volatile uint32_t *r=(volatile uint32_t *)(uintptr_t)0x40007000u;r[3]=(r[3]&~(value&0x3fu))|(value>>8);r[2]|=value&0x3fu;}
void case_init_wake_clock(void)
{volatile uint32_t *r=(volatile uint32_t *)(uintptr_t)0x40007000u;volatile uint32_t *scb=(volatile uint32_t *)(uintptr_t)0xe000ed00u;r[0]=(r[0]&~7u)+3u;scb[4]|=4u;__asm__ volatile("wfi" ::: "memory");}
extern void case_init_selfcheck_read(uint32_t selector,uint8_t *out,uint32_t count); /* 0x080035b8 */
uint32_t case_init_usb_reset_requested(void)
{uint8_t value=0u;case_init_selfcheck_read(0xa2u,&value,1u);return value==1u;}
/* Stock 0x08003a30 calls two state clearers at 0x3a3c and 0x3a60. */
static void clear16(volatile uint8_t *p){p[0]=0u;p[1]=0u;}
static void clear32(volatile uint8_t *p){for(uint32_t i=0;i<4u;i++)p[i]=0u;}
void case_init_sensor_prepare(void)
{
    volatile uint8_t *a=(volatile uint8_t *)(uintptr_t)0x2000089cu;
    a[0x10]=0u;a[0x11]=0u;clear16(a+0x18);a[0x12]=0u;a[0x13]=0u;
    clear16(a+0x16);a[0x14]=0u;
    clear32(a+0x20);clear32(a+0x1c);clear32(a+0x24);clear32(a+0x28);
    volatile uint8_t *b=(volatile uint8_t *)(uintptr_t)0x200008bcu;
    b[0xc]=0u;b[0xd]=0u;clear16(b+0x14);b[0xe]=0u;b[0xf]=0u;
    clear16(b+0x12);b[0x10]=0u;
    clear32(b+0x1c);clear32(b+0x18);clear32(b+0x20);clear32(b+0x24);
}
