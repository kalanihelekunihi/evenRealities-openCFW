/* Product BLE slave runtime pointer cells. Native RAM 0x20074328..0x20074350.
 * These are uninitialized storage; selected APP_SlaveHanderInit 0x46ed94
 * writes the registration/profile/context slots, while appSlaveConnOpen
 * 0x46de78 writes the current DM connection pointer. Absolute placement
 * and boot-time zeroing remain linker/startup obligations. */
#include <stdint.h>
uint8_t *audio_ble_dm_conn_cell;
uint8_t *audio_ble_profile_connection_context;
uint8_t *audio_ble_slave_mode_context;
uint8_t *audio_ble_slave_subcontext;
