/* Apollo Main LittleFS context at stock RAM 0x20071ac8.
 * The pinned LittleFS lfs_t is 128 bytes for the ARM target. */
#include <stdint.h>
#include "lfs.h"

uint8_t audio_file_lfs_context[sizeof(lfs_t)]
    __attribute__((section(".bss.opencfw.file.lfs_context"), used,
                   aligned(_Alignof(lfs_t))));

_Static_assert(sizeof(lfs_t) == 0x80u, "pinned ARM LittleFS context size");
_Static_assert(_Alignof(lfs_t) == 4u, "pinned ARM LittleFS context alignment");
