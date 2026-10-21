/* The stock 0x5ee438 writer and 0x5eed06/0x5eee68 reader/clearer access
 * a full word at 0x20074ae4. The earlier source defined its first byte.
 * This extent tail is a relocatable-chain repair until that provider is
 * rebuilt from its original stage with a four-byte declaration. */
#include <stdint.h>

uint8_t audio_tracepoint_file_list_ready_extent_tail_20074ae5[3]
    __attribute__((section(".bss.opencfw.tracepoint.file_list_ready"),
                   aligned(1), used));
