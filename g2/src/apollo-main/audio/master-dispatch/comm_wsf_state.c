#include <stdint.h>

/* Native BLE communication state 0x200727f0; observed handler byte +0x56. */
/* audio_ble_comm_state: stock 0x200727f0 is one cell; defined as an alias of
 * audio_ble_controller in ble_controller_observed.c (Fix 33). */

/* Native BLE WSF thread state 0x20004068; semaphore handle at +0x14. */
/* Sim-test fix (2026-10-26): stock .data init at 0x20004068 is
 * {0x4d0af7, 0x4d0b1d, 0, 0, 0, 0} (.waves/init_20000000.bin +0x4068) =
 * threadBleWsfInit 0x4d0af6 / threadBleWsfDeinit 0x4d0b1c (apollo_main.tsv,
 * thread_ble_wsf.c:173,182). It was zero (.bss), so the thread manager's
 * blx of +0 went to address 0. Same 0x18-byte layout. */
void threadBleWsfInit(void);
void threadBleWsfDeinit(void);
struct { void (*init)(void); void (*deinit)(void); uint8_t rest[0x10]; }
    audio_ble_wsf_thread_state __attribute__((aligned(4))) =
    { threadBleWsfInit, threadBleWsfDeinit, {0} };
