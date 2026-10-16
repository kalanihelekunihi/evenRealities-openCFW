/* Cordio dmConnExecCback 0x4b62ea: five optional callbacks at dmConnCb+0x90. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[]; /* RAM 0x200712a4 */

void audio_ble_dm_conn_exec_callback_4b62ea(void *event)
{
    void (**callbacks)(void *) =
        (void (**)(void *))(void *)(audio_dm_connection_records + 0x90u);
    for (uint32_t i = 0u; i < 5u; ++i)
        if (callbacks[i] != 0)
            callbacks[i](event);
}
