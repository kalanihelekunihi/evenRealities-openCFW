/* Audio delayed-block remove is the pinned FreeRTOS uxListRemove body at
 * Apollo 0x4560e8. Export the caller name at the same compiled entry. */
#include "../../foundation/freertos_ready/list_subset.c"

__asm__(".global audio_block_remove\n"
        ".set audio_block_remove, uxListRemove\n"
        ".global audio_aux_list_remove\n.set audio_aux_list_remove, uxListRemove\n"
        ".global audio_timer_list_remove\n.set audio_timer_list_remove, uxListRemove\n"
        ".global stock_list_remove\n.set stock_list_remove, uxListRemove\n");
