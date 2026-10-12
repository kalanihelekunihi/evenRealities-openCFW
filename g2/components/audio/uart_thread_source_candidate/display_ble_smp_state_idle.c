/* Native smpStateIdle 0x537bb8: CCB state byte at +0x3e. */
#include <stdint.h>
uint8_t smpStateIdle(const uint8_t *ccb){return ccb[0x3eu]==0u;}
