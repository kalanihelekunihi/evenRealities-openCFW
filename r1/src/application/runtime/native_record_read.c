/* Stock 0x735e0 four-core-register entry. Reuse the canonical cached getter;
 * its incidental two-word return is not part of this void entry contract. */
#include <stdint.h>
#include "native_health_profile.h"
void r1_event_service_000735e0(void *destination,uint32_t fallback0,
                              uint32_t fallback1,uint32_t fallback2)
{
    (void)r1_kv_health_get(destination,fallback0,fallback1,fallback2);
}
