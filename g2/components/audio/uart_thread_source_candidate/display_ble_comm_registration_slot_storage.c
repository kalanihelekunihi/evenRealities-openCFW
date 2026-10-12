/* BSS pointer at native 0x200004b8. bleCommHandlerInit 0x4b7e74 writes its
 * authenticated ROM table address before SMP cancellation reads offset 7. */
#include <stdint.h>
const uint8_t *audio_ble_comm_registration_slot;
/* Cordio's pSmpCfg and the product slot resolve to the same native cell
 * 0x200004b8, proven by the literal load at smpDbMaxAttemptReached 0x5426c0. */
__asm__(".global pSmpCfg\n.set pSmpCfg,audio_ble_comm_registration_slot");
