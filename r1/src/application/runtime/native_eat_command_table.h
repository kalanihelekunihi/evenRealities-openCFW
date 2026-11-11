#ifndef R1_NATIVE_EAT_COMMAND_TABLE_H
#define R1_NATIVE_EAT_COMMAND_TABLE_H

#include <stdint.h>

struct r1_eat_command_entry {
    uint32_t flags;
    const char *name;
    void (*callback)(char *);
    uint32_t reserved;
};

extern const struct r1_eat_command_entry r1_eat_command_table[37];

#endif
