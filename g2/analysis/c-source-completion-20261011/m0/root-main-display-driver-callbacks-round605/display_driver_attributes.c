/* Apollo Main ROM 0x75381c and initialized SRAM 0x2000067c describe the
 * displaydrv_manager CMSIS thread and message queue. Relocatable C pointers
 * replace stock absolute name/storage addresses; final scatter placement and
 * CMSIS producer configuration remain open gates. */
#include "display_driver_attributes.h"

_Static_assert(sizeof(struct display_driver_thread_attrs)==36u,"thread attributes ABI");
_Static_assert(sizeof(struct display_driver_queue_attrs)==24u,"queue attributes ABI");

static const char thread_name[]="displaydrv_mgr_task";
static const char queue_name[]="display_mgr_Queue";
_Alignas(4) uint8_t audio_display_driver_queue_control_block[0x50u];
_Alignas(4) uint8_t audio_display_driver_queue_storage[0xd80u];

const struct display_driver_thread_attrs audio_display_driver_thread_attrs = {
    thread_name,0,0,0,0,0x800u,0x2du,1u,0,
};
struct display_driver_queue_attrs audio_display_driver_queue_attrs = {
    queue_name,0,audio_display_driver_queue_control_block,0x50u,
    audio_display_driver_queue_storage,0xd80u,
};
