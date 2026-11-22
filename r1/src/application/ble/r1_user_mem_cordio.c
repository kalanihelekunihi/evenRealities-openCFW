/* No Nordic user-memory request is issued by the Cordio R1 source profile. */
#if defined(R1_CORDIO_RTC0)
#include "ble.h"
#include "nrf_error.h"
#include "cordio_ble_event_bridge.h"

uint32_t sd_ble_user_mem_reply(uint16_t conn_handle,
                                ble_user_mem_block_t const *block)
{
    if (r1_cordio_conn_id_from_nordic(conn_handle) == 0u)
        return BLE_ERROR_INVALID_CONN_HANDLE;
    if (block != 0 && (block->p_mem == 0 || block->len == 0u))
        return NRF_ERROR_INVALID_LENGTH;
    /* R1 sets NRF_BLE_QWR_MAX_ATTR=0. Its registered user attributes use
     * simple write callbacks and reject ATT prepare writes. Cordio owns its
     * ATT queue and never publishes BLE_EVT_USER_MEM_REQUEST, so there is
     * no Nordic application-memory request to answer. */
    return NRF_ERROR_INVALID_STATE;
}
#endif
