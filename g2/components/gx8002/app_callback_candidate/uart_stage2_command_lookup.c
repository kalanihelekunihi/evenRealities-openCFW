/* SPDX-License-Identifier: MIT
 * Stage-2 command name helpers, stock 0x10006294, 0x100062e0,
 * 0x100062fc, and 0x10005e74. The five-word descriptor stride and
 * exact/unique-prefix policy follow the retained stage-2 pseudocode.
 */
#include <stdint.h>
#include <stddef.h>
#include "uart_stage2_command.h"

uint32_t gx8002_uart_stage2_strlen_62fc(const char *s)
{
    const char *p = s;
    while (*p != '\0') ++p;
    return (uint32_t)(p - s);
}

const char *gx8002_uart_stage2_strchr_62e0(const char *s, char c)
{
    for (;;) {
        if (*s == c) return s;
        if (*s == '\0') return NULL;
        ++s;
    }
}

int32_t gx8002_uart_stage2_strncmp_6294(const char *a, const char *b,
                                          uint32_t length)
{
    while (length != 0) {
        uint8_t x = (uint8_t)*a++;
        uint8_t y = (uint8_t)*b++;
        if (x != y) return x < y ? -1 : 1;
        if (x == 0) break;
        --length;
    }
    return 0;
}

const struct gx8002_stage2_command *gx8002_uart_stage2_find_command_5e74(
    const char *name, const struct gx8002_stage2_command *table,
    uint32_t count)
{
    if (name == NULL) return NULL;
    const char *dot = gx8002_uart_stage2_strchr_62e0(name, '.');
    uint32_t prefix = dot ? (uint32_t)(dot - name) :
                            gx8002_uart_stage2_strlen_62fc(name);
    const struct gx8002_stage2_command *sole = NULL;
    uint32_t matches = 0;
    for (uint32_t i = 0; i < count; ++i) {
        if (gx8002_uart_stage2_strncmp_6294(name, table[i].name,
                                               prefix) != 0) continue;
        if (gx8002_uart_stage2_strlen_62fc(table[i].name) == prefix)
            return &table[i];
        sole = &table[i];
        ++matches;
    }
    return matches == 1 ? sole : NULL;
}
