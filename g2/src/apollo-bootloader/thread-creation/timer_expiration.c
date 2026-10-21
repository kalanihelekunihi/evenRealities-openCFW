/* SPDX-License-Identifier: MIT. Source reconstruction of 0x419406/0x41965c.
 * Original image: locked g2-2.2.6.10 ota_s200_bootloader.bin, SHA-256
 * f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5,
 * loaded at 0x00410000. */
#include "timer_expiration.h"
#include "timer_wait.h"

#define WORD(address) (*(volatile uint32_t *)(uintptr_t)(address))

/* Exact direct-call contract from 0x419406: (timer, base, now). This is the
 * separately recovered 0x4193de provider. */
extern void opencfw_boot_timer_reload(uint32_t *timer,
                                     uint32_t deadline,
                                     uint32_t now);

static uint32_t *current_timer(void) {
    uint32_t *list = (uint32_t *)(uintptr_t)WORD(0x20027178);
    uint32_t *item = (uint32_t *)(uintptr_t)list[3];
    return (uint32_t *)(uintptr_t)item[3];
}

void opencfw_bl_timer_expire(uint32_t base, uint32_t now) {
    uint32_t *timer = current_timer();

    /* The stock routine unlinks timer->list_item at timer+4 before examining
     * bit 2 of the byte at timer+0x28 (LSLS #29; BPL). */
    (void)opencfw_boot_list_unlink(timer + 1);
    uint8_t flags = *((volatile uint8_t *)timer + 0x28);
    if (flags & 0x04u) {
        opencfw_boot_timer_reload(timer, base, now);
    } else {
        *((volatile uint8_t *)timer + 0x28) = (uint8_t)(flags & 0xfeu);
    }

    void (*callback)(uint32_t *) =
        (void (*)(uint32_t *))(uintptr_t)timer[8];
    callback(timer);
}

void opencfw_bl_timer_rollover(void) {
    volatile uint32_t *current = (volatile uint32_t *)(uintptr_t)0x20027178;
    volatile uint32_t *overflow = (volatile uint32_t *)(uintptr_t)0x2002717c;

    /* 0x41965c repeatedly expires the first element of the current list with
     * now=UINT32_MAX. It then exchanges the list pointers. */
    while (((uint32_t *)(uintptr_t)*current)[0] != 0) {
        uint32_t *timer = current_timer();
        opencfw_bl_timer_expire(timer[1], UINT32_MAX);
    }

    uint32_t old_current = *current;
    *current = *overflow;
    *overflow = old_current;
}
