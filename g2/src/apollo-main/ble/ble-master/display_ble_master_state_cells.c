/* Source-owned mutable cells used by the Apollo central-profile paths.
 * Native RAM addresses are documented for final linker placement; the
 * source candidate does not yet establish image startup initialization. */
#include <stdint.h>

volatile uint16_t audio_ble_master_connect_wait;       /* 0x20074f18 */
volatile uint8_t audio_ble_master_auth_mode;          /* 0x20074f80 */
volatile uint8_t audio_ble_master_failure_notify;     /* 0x20074f82 */
volatile uint8_t audio_ble_master_failure_count;      /* 0x20074f83 */
volatile uint8_t audio_ble_master_connection_flag;    /* 0x20074f84 */
volatile uint8_t audio_ble_master_connect_state;      /* 0x20074f87 */
volatile uint8_t audio_ble_master_publish_flag;       /* 0x20074f88 */
volatile uint8_t audio_ble_master_link_ready;          /* 0x20074f89 */

uint8_t *audio_ble_master_state_slot;                  /* 0x200742fc */
extern uint8_t *audio_ble_master_context
    __attribute__((alias("audio_ble_master_state_slot")));
uint8_t *audio_ble_master_mode_slot;                   /* 0x20074300 */
uint8_t *audio_ble_master_state_shadow;                /* 0x20074304 */
uint8_t *audio_ble_master_payload_slot;                /* 0x20074308 */
const uint8_t *audio_ble_master_registration_slot;     /* 0x20074354 */
