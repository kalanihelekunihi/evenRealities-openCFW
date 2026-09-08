/* SPDX-License-Identifier: MIT */
/* Recovered protection queries, image-A package 0x15900 and 0x15994.
 * Decoded queries qualified; table initialization and hardware remain unqualified. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
extern unsigned int open_cfw_gx8002_flash_read_status(void);
extern unsigned int open_cfw_gx8002_flash_read_status2(void);
/* CK804 loads zero-extend into the full register. GCC 13 otherwise emits
 * a second extension for each volatile narrow C load. These source-level
 * intrinsics retain exactly one ordered memory access, without encoded bytes. */
static inline unsigned read_byte(volatile uint8_t *address, unsigned offset)
{
    unsigned value;
    __asm__ volatile ("ld.b %0, (%1, %2)" : "=r"(value) : "r"(address), "i"(offset) : "memory");
    return value;
}
static inline unsigned read_halfword(volatile uint16_t *address, unsigned offset)
{
    unsigned value;
    __asm__ volatile ("ld.h %0, (%1, %2)" : "=r"(value) : "r"(address), "i"(offset) : "memory");
    return value;
}
static inline volatile uint32_t *selected(void)
{
    return (volatile uint32_t *)open_cfw_gx8002_flash_state.selected_device;
}
static inline volatile uint32_t *profile(volatile uint32_t *device)
{
    return (volatile uint32_t *)(uintptr_t)device[4];
}
int open_cfw_gx8002_flash_write_protect_mode(void)
{
    volatile uint32_t *p=profile(selected());
    return p && p[0] ? 1 : -1;
}
int open_cfw_gx8002_flash_write_protect_status(unsigned *length)
{
    *length=0;
    volatile uint32_t *p=profile(selected());
    unsigned result;
    if (p && p[0]) {
        open_cfw_gx8002_flash_wait_ready();
        unsigned manufacturer=read_halfword((volatile uint16_t *)selected(),6);
        if (manufacturer==0x5e || manufacturer==0x85) {
            unsigned first=(unsigned)open_cfw_gx8002_flash_read_status();
            unsigned second=(unsigned)open_cfw_gx8002_flash_read_status2();
            p=profile(selected());
            unsigned count=p[1];
            for (unsigned i=0;i!=count;++i) {
                volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)p[0]+i*8u;
                unsigned mask1=read_byte(entry,1);
                unsigned expected1=read_byte(entry,0);
                unsigned expected2=read_byte(entry,2);
                unsigned mask2=read_byte(entry,3);
                unsigned candidate=((volatile uint32_t *)entry)[1];
                if ((first&mask1)==expected1 && (second&mask2)==expected2) {
                    result=candidate;
                    goto finished;
                }
            }
        }
    }
    result=UINT32_MAX;
finished:
    *length=result;
    return result==UINT32_MAX ? -1 : 0;
}
