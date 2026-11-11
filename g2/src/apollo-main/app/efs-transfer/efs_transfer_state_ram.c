/* EFS transfer state base 0x20071cc8; stock clears all 0x78 bytes.
 * The active flag is at +0x75, followed by two reserved bytes. */
#include <stdint.h>

uint8_t audio_efs_transfer_state[0x78]
    __attribute__((section(".bss.opencfw.efs.transfer"), aligned(4), used));

_Static_assert(sizeof(audio_efs_transfer_state) == 0x78u, "stock EFS object span");
