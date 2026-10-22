/* AT^NUS probe command (module g2-at-nus; no stock path string survives).
 * Native 0x5a5520..0x5a552b; literal pool word 0x5a552c. */
#include <stdint.h>
#include "g2_at_core.h"

static const char o_ok[] = "NUS+OK\r\n"; /* ROM 0x78a370 */

int32_t atNusHandler(const char *arg1, const char *arg2)
{
    (void)arg1;
    (void)arg2;
    at_core_output(o_ok);
    return 1;
}
