/* Nordic GAP identity calls backed by R1's source-built Cordio ATT group. */
#if defined(R1_CORDIO_RTC0)
#include <string.h>

#include "ble.h"
#include "nrf_error.h"
#include "r1_gap_service.h"

enum { R1_NAME_CAPACITY = 32 };

uint32_t sd_ble_gap_device_name_set(ble_gap_conn_sec_mode_t const *permission,
                                    uint8_t const *name, uint16_t length)
{
    if (permission == 0 || name == 0)
        return NRF_ERROR_INVALID_ADDR;
    if (permission->sm != 1u || permission->lv != 1u)
        return NRF_ERROR_NOT_SUPPORTED;
    if (length > R1_NAME_CAPACITY) return NRF_ERROR_DATA_SIZE;
    return r1_cordio_gap_name_set(name, length) ? NRF_SUCCESS : NRF_ERROR_INVALID_STATE;
}

uint32_t sd_ble_gap_device_name_get(uint8_t *name, uint16_t *length)
{
    if (length == 0) return NRF_ERROR_INVALID_ADDR;
    uint16_t actual;
    bool fits = r1_cordio_gap_name_read(name, name == 0 ? 0u : *length,
                                        &actual);
    *length = actual;
    return fits ? NRF_SUCCESS : NRF_ERROR_DATA_SIZE;
}

uint32_t sd_ble_gap_appearance_set(uint16_t appearance)
{
    r1_cordio_gap_appearance_set(appearance);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_appearance_get(uint16_t *appearance)
{
    if (appearance == 0) return NRF_ERROR_INVALID_ADDR;
    *appearance = r1_cordio_gap_appearance_get();
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_ppcp_set(ble_gap_conn_params_t const *params)
{
    if (params == 0 || ((uintptr_t)params & 1u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    uint16_t min = params->min_conn_interval;
    uint16_t max = params->max_conn_interval;
    uint16_t latency = params->slave_latency;
    uint16_t timeout = params->conn_sup_timeout;
    if (min < 6u || max > 3200u || min > max || latency > 499u ||
        timeout < 10u || timeout > 3200u ||
        (uint32_t)timeout * 4u <= (uint32_t)(latency + 1u) * max)
        return NRF_ERROR_INVALID_PARAM;
    r1_cordio_gap_ppcp_set((const uint8_t *)params);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_ppcp_get(ble_gap_conn_params_t *params)
{
    if (params == 0 || ((uintptr_t)params & 1u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    r1_cordio_gap_ppcp_get((uint8_t *)params);
    return NRF_SUCCESS;
}
#endif
