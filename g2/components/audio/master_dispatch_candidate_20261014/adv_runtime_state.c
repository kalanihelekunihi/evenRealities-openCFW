#include <stdint.h>

/* Native RAM 0x20074f38: only the enable and route bytes are observed. */
volatile uint8_t audio_ble_adv_resume_state_20074f38[2];

/* Native RAM 0x20073df4: Cordio WSF timer layout is 16 bytes and
 * four-byte aligned. Startup contents and final placement remain open. */
uint8_t audio_ble_adv_timer_20073df4[16] __attribute__((aligned(4)));
