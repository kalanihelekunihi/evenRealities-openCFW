#include <stdint.h>

/* Native RAM 0x2007408c: state byte, tick word at +4, retry byte at +8.
 * The C body owns the 12-byte accessed prefix; final object span is open. */
uint8_t audio_ble_ring_policy_state_2007408c[12];

/* Native reset path 0x49f6ae clears these distinct RAM cells. */
uint32_t audio_ble_ring_policy_deadline_200748fc;
uint8_t audio_ble_ring_policy_pending_2007500b;
