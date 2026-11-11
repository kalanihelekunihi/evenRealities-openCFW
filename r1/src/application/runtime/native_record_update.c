#include <stdint.h>
#include "native_health_profile.h"

extern int r1_native_memcmp(const void *, const void *, uint32_t);
extern void r1_record12_persist(const void *);
extern void r1_record12_apply(const volatile uint8_t *,
                              const volatile uint8_t *);

/* Stock 0x6c66c. Persistence may modify either view: apply consumes the live
 * records after persistence, with no snapshot or status-based suppression. */
void r1_event_service_0006c66c(const volatile uint8_t *previous,
                              const volatile uint8_t *updated)
{
    if (!previous || !updated) return;
    if (!r1_record12_validate(updated)) return;
    if (!r1_native_memcmp((const void *)previous, (const void *)updated, 12))
        return;
    r1_record12_persist((const void *)updated);
    r1_record12_apply(previous, updated);
}
