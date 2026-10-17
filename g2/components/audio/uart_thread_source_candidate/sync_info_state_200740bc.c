/* Native SyncInfo common-data handler clears 12 bytes at RAM 0x200740bc. */
#include <stdint.h>

__attribute__((used, section(".g2_sync_info_state_200740bc"), aligned(4)))
uint8_t audio_sync_info_state_200740bc[12];

_Static_assert(sizeof audio_sync_info_state_200740bc == 12u,
               "SyncInfo decoded state span");
