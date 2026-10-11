/* Native dmGetConnParamPtr 0x46efcc. */
#include <stdint.h>
extern uint8_t *audio_ble_dm_conn_cell; /* pointer cell RAM 0x20074328 */
void *audio_ble_dm_conn_params(void) {return audio_ble_dm_conn_cell;}
