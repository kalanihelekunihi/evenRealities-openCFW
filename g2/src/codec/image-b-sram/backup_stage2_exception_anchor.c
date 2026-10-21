/* Native exception entry stores and reloads one word at 0x20017390.
 * Its 72-byte frame below this address is a separate runtime stack region. */
#include <stdint.h>

uint32_t gx8002_image_b_exception_scratch_20017390[1]
    __attribute__((section(".bss.image_b_exception_anchor"), used, aligned(4)));
