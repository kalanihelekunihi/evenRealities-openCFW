/* R1-owned fixed-state integration of recovered i2c_5 clients.
 * Entries 0x50510/0x50534 and board resource operations 0x504C0/0x504D8.
 * Registry dispatch bodies are consumed from the existing reconstructed module.
 * See YHM2710-I2C5-RESOURCE-BOUNDARY.md for source/electrical distinctions. */
#include <stddef.h>
#include "stock_transport.h"
#include "../registry/stock_registry.h"

_Static_assert(sizeof(uintptr_t) == 4, "stock pointer ABI");
_Static_assert(offsetof(r1_i2c5_stock_state, bus) == 4, "stock bus handle offset");
_Static_assert(offsetof(r1_i2c5_stock_state, request) == 8, "stock request offset");
_Static_assert(sizeof(generic_device_registry_request_block) == 20, "stock shared request extent");
_Static_assert(offsetof(generic_device_registry_request_block, buffer) == 4, "write buffer");
_Static_assert(offsetof(generic_device_registry_request_block, data) == 12, "read buffer");
_Static_assert(offsetof(generic_device_registry_request_block, length2) == 16, "read length");

r1_i2c5_stock_state r1_i2c5_state
    __attribute__((section(".r1.i2c5.state"), aligned(4))) = {
        .request={.command=0xa6,.length=1,.length2=1}
    };

int32_t r1_i2c5_read_transfer(uint8_t address, uint16_t reg, uint8_t *data, uint16_t length) {
    generic_device_registry_request_block *request = &r1_i2c5_state.request;
    request->code = reg;
    request->command = address;
    request->length2 = length;
    request->data = (uintptr_t)data;
    return (int32_t)r1_stock_dispatch_10(
        r1_i2c5_state.bus, 0, (uintptr_t)request, 0);
}

int32_t r1_i2c5_write_transfer(uint8_t address, uint16_t reg, const uint8_t *data, uint16_t length) {
    generic_device_registry_request_block *request = &r1_i2c5_state.request;
    request->code = reg;
    request->command = address;
    /* Stock intentionally preserves the previous buffer pointer for NULL. */
    if (data != NULL)
        request->buffer = (uintptr_t)data;
    request->length = length;
    return (int32_t)r1_stock_dispatch_14(
        r1_i2c5_state.bus, 0, (uintptr_t)request, 0);
}

void r1_i2c5_nfc_resource_release(void) {
    (void)r1_stock_dispatch_0c(r1_i2c5_state.bus);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x50000808) = UINT32_C(0x400);
}

void r1_i2c5_nfc_resource_acquire(void) {
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x50000808) = UINT32_C(0x400);
    r1_st25_delay_ms(10);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x5000080c) = UINT32_C(0x400);
    r1_st25_delay_ms(10);
    (void)r1_stock_dispatch_08(r1_i2c5_state.bus);
}

/* The ADC cache sits immediately after the shared request at stock 0x20006854. */
generic_device_registry_device *r1_vnfc_rect_adc_device
    __attribute__((section(".r1.vnfc.adc"), aligned(4)));

void r1_vnfc_rect_adc_handle_cache(void) {
    r1_vnfc_rect_adc_device = r1_stock_registry_find("vnfc_rect_adc");
}

void r1_i2c5_nfc_resource_registration(void) {
    if (r1_i2c5_state.gpo == NULL)
        r1_i2c5_state.gpo = r1_stock_registry_find("nfc_gpo_irq");
    /* Unlike GPO and bus, stock refreshes this cache on every invocation. */
    r1_vnfc_rect_adc_handle_cache();
    if (r1_i2c5_state.bus == NULL)
        r1_i2c5_state.bus = r1_stock_registry_find("i2c_5");
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x50000a28) = UINT32_C(0x30f);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x50000808) = UINT32_C(0x400);
}
