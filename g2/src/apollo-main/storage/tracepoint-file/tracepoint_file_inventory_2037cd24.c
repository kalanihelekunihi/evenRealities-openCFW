/* Stock Main 0x2037cd24: 16 sequence/size pairs, count, and total bytes. */
#include <stdint.h>
uint8_t audio_tracepoint_file_inventory[0x88]
    __attribute__((section(".bss.opencfw.tracepoint.file_inventory"),aligned(4),used));
_Static_assert(sizeof(audio_tracepoint_file_inventory)==0x88u,"file inventory span");
