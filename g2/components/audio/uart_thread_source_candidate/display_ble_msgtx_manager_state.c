/* Apollo Main compressed SRAM record 0x75d3f4 initializes this observed
 * BLE MsgTx manager at 0x20004020. The first eight bytes carry native code
 * addresses; the selected paths use thread/queue cells at +8/+12. Final
 * absolute placement and any wider allocation remain separate gates. */
#include <stdint.h>

struct ble_msgtx_manager {uint8_t reserved[8];void *thread;void *queue;};
_Static_assert(sizeof(struct ble_msgtx_manager)==16u,"BLE manager ABI");
struct ble_msgtx_manager audio_ble_msgtx_manager = {
    {0x49u,0x53u,0x47u,0x00u,0x75u,0x53u,0x47u,0x00u},
    0,0,
};
__asm__(".global audio_ble_tx_thread_state\n"
        ".set audio_ble_tx_thread_state,audio_ble_msgtx_manager");
