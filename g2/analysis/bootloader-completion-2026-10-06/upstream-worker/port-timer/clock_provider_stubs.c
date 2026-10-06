/* Test-link implementations only. The differential runner intercepts these
 * boundaries on both stock and source sides; no clock hardware is modeled. */
#include <stdint.h>

__attribute__((noinline))
uint32_t clock_request(uint8_t clock_id, uint8_t user_id)
{
    (void)clock_id;
    (void)user_id;
    return 0u;
}

__attribute__((noinline))
uint32_t clock_release(uint8_t clock_id, uint8_t user_id)
{
    (void)clock_id;
    (void)user_id;
    return 0u;
}
