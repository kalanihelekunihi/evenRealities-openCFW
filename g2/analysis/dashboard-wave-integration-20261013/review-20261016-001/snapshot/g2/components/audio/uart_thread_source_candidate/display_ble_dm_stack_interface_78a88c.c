/* Native Cordio DM dispatch table at ROM 0x78a880. The stack interface
 * pointer at 0x78a88c addresses slot three of this eight-entry table. */
#include <stdint.h>

extern void audio_ble_dm_dispatch_536820(void *);
extern void audio_ble_dm_dispatch_536896(void *);
extern void audio_ble_dm_dispatch_5368ae(void *);
extern void audio_ble_dm_stack_reset_536918(void *);
extern void audio_ble_dm_stack_hci_handler_53694c(void *);
extern void audio_ble_dm_stack_msg_handler_5369d8(void *);
extern void audio_ble_dm_dispatch_4d2544(void *);
extern void audio_ble_dm_dispatch_4d2364(void *);

typedef void (*audio_ble_dm_interface_fn)(void *);
_Static_assert(sizeof(audio_ble_dm_interface_fn) == 4u, "Thumb pointer ABI");

const audio_ble_dm_interface_fn audio_ble_dm_dispatch_table_78a880[8]
    __attribute__((used, aligned(4))) = {
        audio_ble_dm_dispatch_536820,
        audio_ble_dm_dispatch_536896,
        audio_ble_dm_dispatch_5368ae,
        audio_ble_dm_stack_reset_536918,
        audio_ble_dm_stack_hci_handler_53694c,
        audio_ble_dm_stack_msg_handler_5369d8,
        audio_ble_dm_dispatch_4d2544,
        audio_ble_dm_dispatch_4d2364,
    };

/* Relocatable alias for the existing Main import; a final root C rebuild
 * can instead refer directly to &audio_ble_dm_dispatch_table_78a880[3]. */
__asm__(".globl audio_ble_dm_stack_table_78a88c\n"
        ".set audio_ble_dm_stack_table_78a88c, audio_ble_dm_dispatch_table_78a880 + 12\n"
        ".type audio_ble_dm_stack_table_78a88c, %object\n"
        ".size audio_ble_dm_stack_table_78a88c, 20\n");
