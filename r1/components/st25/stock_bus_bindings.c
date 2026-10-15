/* R1-owned board callbacks: authenticated stock entries 0x44C58/64/6E/78/84/8A
 * and registration root 0x44BEC. Original provider bodies stay upstream. */
#include <stddef.h>
#include "stock_bus_bindings.h"
#include "st25dvxxkc.h"

_Static_assert(offsetof(ST25DVxxKC_IO_t, Write) == 12, "stock Write callback offset");
_Static_assert(offsetof(ST25DVxxKC_IO_t, Read) == 16, "stock Read callback offset");
_Static_assert(offsetof(ST25DVxxKC_IO_t, GetTick) == 20, "stock tick callback offset");

ST25DVxxKC_Object_t r1_st25_device
    __attribute__((section(".r1.st25.object"), aligned(4)));
ST25DVxxKC_Drv_t *r1_st25_active_driver
    __attribute__((section(".r1.st25.active_driver"), aligned(4)));

int32_t r1_st25dvxxkc_bus_tick_get(void) {
    return (int32_t)*(volatile uint32_t *)(uintptr_t)UINT32_C(0x40011504);
}

int32_t r1_st25dvxxkc_bus_initialize(void) {
    r1_i2c5_nfc_resource_acquire();
    return 0;
}

int32_t r1_st25dvxxkc_bus_deinitialize(void) {
    r1_i2c5_nfc_resource_release();
    return 0;
}

int32_t r1_st25dvxxkc_bus_is_ready(uint16_t address, uint32_t trials) {
    (void)address;
    (void)trials;
    r1_st25_delay_ms(10);
    return 0;
}

int32_t r1_st25dvxxkc_bus_read(uint16_t address, uint16_t reg, uint8_t *data, uint16_t length) {
    return r1_i2c5_read_transfer((uint8_t)address, reg, data, length);
}

int32_t r1_st25dvxxkc_bus_write(uint16_t address, uint16_t reg, const uint8_t *data, uint16_t length) {
    return r1_i2c5_write_transfer((uint8_t)address, reg, data, length);
}

int32_t r1_st25dvxxkc_register_provider(void) {
    const ST25DVxxKC_IO_t io = {
        .Init = r1_st25dvxxkc_bus_initialize,
        .DeInit = r1_st25dvxxkc_bus_deinitialize,
        .IsReady = r1_st25dvxxkc_bus_is_ready,
        .Write = r1_st25dvxxkc_bus_write,
        .Read = r1_st25dvxxkc_bus_read,
        .GetTick = r1_st25dvxxkc_bus_tick_get,
        .DeviceAddress = 0
    };
    if (ST25DVxxKC_RegisterBusIO(&r1_st25_device, &io) == 0) {
        r1_st25_active_driver = &St25Dvxxkc_Drv;
        if (r1_st25_active_driver->Init != NULL &&
            r1_st25_active_driver->Init(&r1_st25_device) == 0)
            return 0;
        r1_st25_active_driver = NULL;
    }
    return -1;
}
