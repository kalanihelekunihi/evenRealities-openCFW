/* SPDX-License-Identifier: MIT */
/* Backup 0x410b0: first default pin is constant zero; later pin IDs and
 * fallback functions are read from the default table. First override wins. */
#include <stdint.h>
extern const uint8_t open_cfw_gx8002_backup_padmux_defaults[64];
extern int open_cfw_gx8002_padmux_set(int,int);
int open_cfw_gx8002_padmux_init(const void *table,int size)
{
    if (!table || size<0) return -1;
    uintptr_t end=(uintptr_t)table+2u*(unsigned)size;
    const volatile uint8_t *fallback=open_cfw_gx8002_backup_padmux_defaults+1;
    unsigned pin=0;
    for (;;) {
        uintptr_t entry=(uintptr_t)table;
        while (entry!=end && *(volatile uint8_t *)entry!=pin) entry+=2;
        unsigned function=entry==end ? *fallback : *(volatile uint8_t *)(entry+1);
        open_cfw_gx8002_padmux_set(pin,function);
        if (fallback==open_cfw_gx8002_backup_padmux_defaults+63) break;
        pin=fallback[1];fallback+=2;
    }
    return 0;
}
