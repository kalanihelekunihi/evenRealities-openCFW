/* EFS transfer state base 0x20071cc8; observed active flag at offset 0x75. */
#include <stdint.h>

uint8_t audio_efs_transfer_state[0x76]
    __attribute__((section(".bss.opencfw.efs.transfer"), aligned(4), used));

_Static_assert(sizeof(audio_efs_transfer_state) == 0x76u, "observed EFS flag span");
