#ifndef R1_GOMORE_RUNTIME_CONFIGURATION_H
#define R1_GOMORE_RUNTIME_CONFIGURATION_H

#include <stddef.h>
#include <stdint.h>

/* Stock 0x20007c50 is shared by runtime validation and SDK authorization.
 * The first 12 bytes retain their existing owner; authentication also writes
 * the trailing word and field counter at offsets 12 and 16. */
struct r1_gomore_runtime_configuration {
    uint32_t random_seed;
    int16_t utc_offset;
    uint16_t padding;
    uint32_t timestamp_limit;
    uint32_t auth_field12;
    uint8_t auth_field_count;
    uint8_t auth_reserved[3];
};

_Static_assert(sizeof(struct r1_gomore_runtime_configuration) == 20u,
               "stock GoMore runtime/auth record size");
_Static_assert(offsetof(struct r1_gomore_runtime_configuration,
                        auth_field12) == 12u,
               "stock GoMore auth word offset");
_Static_assert(offsetof(struct r1_gomore_runtime_configuration,
                        auth_field_count) == 16u,
               "stock GoMore auth field counter offset");

extern volatile struct r1_gomore_runtime_configuration
    r1_gomore_runtime_configuration;

#endif
