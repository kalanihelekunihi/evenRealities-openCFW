#include <stdint.h>

/* Native RAM 0x20074ffc; pairMgrSecAuthFlagSet/Get read and write this byte.
 * Startup initialization and final placement remain separate gates. */
uint8_t audio_ble_pair_auth_flag_20074ffc;
