/* Vendor UUID registration and encoding for a C-built R1 BLE service layer.
 * The stock-compatible build keeps the Nordic S140 SVC implementation. */
#include "ble.h"
#include "nrf_error.h"
#include "sdk_config.h"
#include <string.h>

#if defined(SVCALL_AS_NORMAL_FUNCTION)
_Static_assert(NRF_SDH_BLE_VS_UUID_COUNT == 1 || NRF_SDH_BLE_VS_UUID_COUNT == 2,
               "R1 vendor UUID allocation differs from pinned payload configs");
_Static_assert(sizeof(ble_uuid128_t) == 16, "Nordic UUID byte layout");

static ble_uuid128_t vendor_bases[NRF_SDH_BLE_VS_UUID_COUNT];
static uint8_t vendor_count;

static int same_base(ble_uuid128_t const *left, ble_uuid128_t const *right)
{
    for (unsigned i = 0; i < 16; ++i) {
        if (i != 12 && i != 13 && left->uuid128[i] != right->uuid128[i])
            return 0;
    }
    return 1;
}

uint32_t sd_ble_uuid_vs_add(ble_uuid128_t const *base, uint8_t *type)
{
    if (base == NULL || type == NULL) return NRF_ERROR_INVALID_ADDR;

    uint32_t interrupt_mask = __get_PRIMASK();
    __disable_irq();
    for (uint8_t i = 0; i < vendor_count; ++i) {
        if (same_base(base, &vendor_bases[i])) {
            *type = (uint8_t)(BLE_UUID_TYPE_VENDOR_BEGIN + i);
            __set_PRIMASK(interrupt_mask);
            return NRF_SUCCESS;
        }
    }
    if (vendor_count == NRF_SDH_BLE_VS_UUID_COUNT) {
        __set_PRIMASK(interrupt_mask);
        return NRF_ERROR_NO_MEM;
    }
    ble_uuid128_t *slot = &vendor_bases[vendor_count];
    memcpy(slot, base, sizeof(*slot));
    slot->uuid128[12] = 0;
    slot->uuid128[13] = 0;
    *type = (uint8_t)(BLE_UUID_TYPE_VENDOR_BEGIN + vendor_count);
    ++vendor_count;
    __set_PRIMASK(interrupt_mask);
    return NRF_SUCCESS;
}

uint32_t sd_ble_uuid_encode(ble_uuid_t const *uuid, uint8_t *length,
                            uint8_t *encoded)
{
    if (uuid == NULL || length == NULL) return NRF_ERROR_INVALID_ADDR;
    if (uuid->type == BLE_UUID_TYPE_BLE) {
        if (encoded != NULL) {
            encoded[0] = (uint8_t)uuid->uuid;
            encoded[1] = (uint8_t)(uuid->uuid >> 8);
        }
        *length = 2;
        return NRF_SUCCESS;
    }
    if (uuid->type < BLE_UUID_TYPE_VENDOR_BEGIN)
        return NRF_ERROR_INVALID_PARAM;

    uint32_t interrupt_mask = __get_PRIMASK();
    __disable_irq();
    unsigned index = (unsigned)uuid->type - BLE_UUID_TYPE_VENDOR_BEGIN;
    if (index >= vendor_count) {
        __set_PRIMASK(interrupt_mask);
        return NRF_ERROR_INVALID_PARAM;
    }
    if (encoded != NULL) {
        memcpy(encoded, vendor_bases[index].uuid128, 16);
        encoded[12] = (uint8_t)uuid->uuid;
        encoded[13] = (uint8_t)(uuid->uuid >> 8);
    }
    *length = 16;
    __set_PRIMASK(interrupt_mask);
    return NRF_SUCCESS;
}

/* The future C stack manager calls this before a new BLE enable cycle. */
void r1_ble_uuid_registry_reset(void)
{
    uint32_t interrupt_mask = __get_PRIMASK();
    __disable_irq();
    vendor_count = 0;
    __set_PRIMASK(interrupt_mask);
}
#endif
