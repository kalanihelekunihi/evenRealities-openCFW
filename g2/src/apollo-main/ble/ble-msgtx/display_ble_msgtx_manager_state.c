/* Apollo Main compressed SRAM record 0x75d3f4 initializes this observed
 * BLE MsgTx manager at 0x20004020. The first eight bytes carry native code
 * addresses; the selected paths use thread/queue cells at +8/+12. Final
 * absolute placement and any wider allocation remain separate gates. */
#include <stdint.h>

/* Sim-test fix (2026-10-26): stock init words 0x00475349/0x00475375 are
 * Thumb pointers to threadBleMsgTxInit 0x475348 / threadBleMsgTxDeinit
 * 0x475374 (g2/symbols/apollo_main.tsv); called via blx from
 * thread_manager_threads_init_4c953e. Relocated to our symbols. */
void threadBleMsgTxInit(void);
void threadBleMsgTxDeinit(void);
struct ble_msgtx_manager {void (*init)(void);void (*deinit)(void);void *thread;void *queue;};
_Static_assert(sizeof(struct ble_msgtx_manager)==16u,"BLE manager ABI");
struct ble_msgtx_manager audio_ble_msgtx_manager = {
    threadBleMsgTxInit,threadBleMsgTxDeinit,
    0,0,
};
__asm__(".global audio_ble_tx_thread_state\n"
        ".set audio_ble_tx_thread_state,audio_ble_msgtx_manager");
