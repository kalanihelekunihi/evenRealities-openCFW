/* SPDX-License-Identifier: MIT */
/* Recovered package 0x177fc. Timer slots are owned by timer_dispatch. */
#include <stdint.h>
#include <stddef.h>
struct __attribute__((packed, aligned(4))) open_cfw_timer_slot {
    void (*callback)(void *);
    void *argument;
    uint32_t interval_ms, last_low, last_high, due_low, due_high, active, repeat;
};
_Static_assert(sizeof(struct open_cfw_timer_slot)==36,"Recovered timer slot ABI");
extern volatile struct open_cfw_timer_slot open_cfw_timer_slots[10];
extern unsigned open_cfw_gx8002_clock_frequency(unsigned);
extern void gx_clock_set_module_enable(unsigned,unsigned);
extern void *memset(void *,int,size_t);
extern int open_cfw_gx8002_timer_dispatch(void);
extern void gx_request_irq(unsigned,int (*)(void),void *);
extern void open_cfw_gx8002_timer_channel_initialize(void);
#define TIMER_REGISTER(offset) (*(volatile uint32_t *)(uintptr_t)(0xa0400000u+(offset)))
void open_cfw_gx8002_timer_initialize(void)
{
    gx_clock_set_module_enable(23,1);
    TIMER_REGISTER(0x10)=1;
    TIMER_REGISTER(0x10)=0;
    TIMER_REGISTER(0x20)=3;
    unsigned frequency=open_cfw_gx8002_clock_frequency(23);
    TIMER_REGISTER(0x24)=frequency/1000000u-1u;
    TIMER_REGISTER(0x28)=0xfffffc18u;
    TIMER_REGISTER(0x10)=2;
    memset((void *)open_cfw_timer_slots,0,sizeof(open_cfw_timer_slots));
    gx_request_irq(14,open_cfw_gx8002_timer_dispatch,0);
    open_cfw_gx8002_timer_channel_initialize();
    TIMER_REGISTER(0x90)=1;
    TIMER_REGISTER(0x90)=0;
    TIMER_REGISTER(0xa0)=1;
    TIMER_REGISTER(0xa4)=0;
    TIMER_REGISTER(0xa8)=0;
    TIMER_REGISTER(0x90)=2;
}
