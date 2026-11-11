/* Stock R1 Goodix transport: 509b0, 509bc, 5084c, 6f90e, 6f8fa.
 * These are native board callbacks, not the unbound SDK demo gh3026 hooks.
 * The shared request persists between calls; volatile accesses preserve the
 * observed write widths/order, including retention of a null write buffer.
 */
#include <stdint.h>
#include "../registry/stock_registry.h"

typedef struct {
    uint8_t address, reserved_01;
    uint16_t code;
    uint32_t write_buffer;
    uint16_t write_length, reserved_0a;
    uint32_t read_buffer;
    uint16_t read_length, reserved_12;
} r1_goodix_i2c_request;
_Static_assert(sizeof(r1_goodix_i2c_request) == 20, "native request extent");
_Static_assert(__builtin_offsetof(r1_goodix_i2c_request, read_buffer) == 12,
               "native read buffer offset");

/* Cached cells belong to native_peripheral_bindings.c: bus 200076cc,
 * reset 200076d8. The shared request's final placement is 200076dc. */
extern generic_device_registry_device *volatile r1_ppg_bus_device;
extern generic_device_registry_device *volatile r1_ppg_irq_device;
extern generic_device_registry_device *volatile r1_ppg_reset_device;
/* Native callback word at 200076d4, between the independently owned IRQ and
 * reset handles. Its producer and target signature are not inferred here. */
volatile uintptr_t r1_goodix_irq_callback
    __attribute__((section(".r1.goodix.irq.callback"), aligned(4)));
volatile r1_goodix_i2c_request r1_goodix_i2c_request_storage
    __attribute__((section(".r1.goodix.i2c.request"), aligned(4))) = {
        .address = 0x24, .write_length = 1, .read_length = 1
    };

void r1_goodix_i2c_open(void) {
    (void)r1_stock_dispatch_08(r1_ppg_bus_device);
}

/* Native 509a4, 50ae0 and 50af0. Reset uses the output device's slot 18,
 * with the second argument word explicitly zero in both stock wrappers. */
void r1_goodix_i2c_close(void) {
    (void)r1_stock_dispatch_0c(r1_ppg_bus_device);
}
void r1_goodix_power_enable(void) {
    (void)r1_stock_dispatch_18(r1_ppg_reset_device, 1, 0);
}
void r1_goodix_power_disable(void) {
    (void)r1_stock_dispatch_18(r1_ppg_reset_device, 0, 0);
}

/* Native 50ab0/50abc. Opening may replace either cached word. */
uint32_t r1_goodix_irq_close(void) {
    return r1_stock_dispatch_0c(r1_ppg_irq_device);
}
uint32_t r1_goodix_irq_prepare(void) {
    uint32_t status = r1_stock_dispatch_08(r1_ppg_irq_device);
    uintptr_t callback = r1_goodix_irq_callback;
    if (callback != 0)
        return r1_stock_dispatch_20(r1_ppg_irq_device, 1, callback);
    return status;
}

void r1_goodix_i2c_write_request(uint32_t address, uint32_t code,
                               const void *buffer, uint32_t length) {
    r1_goodix_i2c_request_storage.code = (uint16_t)code;
    r1_goodix_i2c_request_storage.address = (uint8_t)address;
    if (buffer != 0)
        r1_goodix_i2c_request_storage.write_buffer = (uintptr_t)buffer;
    r1_goodix_i2c_request_storage.write_length = (uint16_t)length;
    (void)r1_stock_dispatch_14(r1_ppg_bus_device, 0,
                             (uintptr_t)&r1_goodix_i2c_request_storage, 0);
}

void r1_goodix_i2c_read_request(uint32_t address, uint32_t code,
                              void *buffer, uint32_t length) {
    r1_goodix_i2c_request_storage.code = (uint16_t)code;
    r1_goodix_i2c_request_storage.address = (uint8_t)address;
    r1_goodix_i2c_request_storage.read_length = (uint16_t)length;
    r1_goodix_i2c_request_storage.read_buffer = (uintptr_t)buffer;
    (void)r1_stock_dispatch_10(r1_ppg_bus_device, 0,
                             (uintptr_t)&r1_goodix_i2c_request_storage, 0);
}

uint8_t r1_goodix_i2c_write(uint8_t address, const uint8_t *buffer,
                          uint16_t length) {
    r1_goodix_i2c_write_request(address, 0, buffer, length);
    return 1;
}

uint8_t r1_goodix_i2c_read(uint8_t address, const uint8_t *command,
                         uint16_t command_length, uint8_t *buffer,
                         uint16_t length) {
    (void)command_length; /* Stock unconditionally reads one command halfword. */
    uint16_t code = *(const volatile uint16_t *)(const void *)command;
    r1_goodix_i2c_read_request(address, (uint16_t)((code << 8) | (code >> 8)),
                             buffer, length);
    return 1; /* Native callbacks discard the registry operation status. */
}

/* Exact SDK HAL types; aliases share the checked native bodies. The generated
 * demo-user unit omits only its three superseded I2C definitions. */
extern __typeof__(r1_goodix_i2c_open) hal_gh3x2x_i2c_init
    __attribute__((alias("r1_goodix_i2c_open")));
extern __typeof__(r1_goodix_i2c_write) hal_gh3x2x_i2c_write
    __attribute__((alias("r1_goodix_i2c_write")));
extern __typeof__(r1_goodix_i2c_read) hal_gh3x2x_i2c_read
    __attribute__((alias("r1_goodix_i2c_read")));
