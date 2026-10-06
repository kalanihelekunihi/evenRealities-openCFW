#include <stdint.h>

#define PROVIDER(name) \
    __attribute__((noinline, used)) uint32_t name(uint8_t user_id) \
    { (void)user_id; return 0u; }

PROVIDER(opencfw_bl_clock_request_id2)
PROVIDER(opencfw_bl_clock_request_id4)
PROVIDER(opencfw_bl_clock_request_id5)
PROVIDER(opencfw_bl_clock_request_id6)
PROVIDER(opencfw_bl_clock_release_id2)
PROVIDER(opencfw_bl_clock_release_id4)
PROVIDER(opencfw_bl_clock_release_id5)
PROVIDER(opencfw_bl_clock_release_id6)
