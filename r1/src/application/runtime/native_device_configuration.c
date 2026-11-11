/* Native nv_r1 accessors: 0x7b9c8, 0x7b9ec, 0x7ba08, 0x7ba24,
 * 0x7c8b0, 0x7c8e4, 0x7c910, 0x7c93c, 0x7ca10, and 0x7ca44.
 * The shared cached class has a 124-byte payload. As in stock, these helpers
 * require a valid fully populated class; cached-read status is not inspected.
 * No default record or storage owner is introduced. */
#include <stdint.h>
#include "../board/native_kv_class.h"
#include "../board/native_battery_memory.h"
extern void *volatile r1_device_info_kv_handle;
extern uint32_t r1_nv_modules_idle_check(void);
uint32_t r1_accelerometer_calibration_read(void *destination)
{
    _Alignas(4) uint8_t record[124];
    uint8_t *output = (uint8_t *)destination;
    (void)r1_kv_class_read(r1_device_info_kv_handle, record, sizeof(record));
    for (uint32_t i = 0; i < 6u; ++i)
        output[i] = record[68u + i];
    return read16(record + 72u);
}
uint32_t r1_device_info_configuration_byte70_get(void)
{
    _Alignas(4) uint8_t record[124];
    (void)r1_kv_class_read(r1_device_info_kv_handle, record, sizeof(record));
    return record[112];
}
uint32_t r1_device_info_configuration_byte78_get(void)
{
    _Alignas(4) uint8_t record[124];
    (void)r1_kv_class_read(r1_device_info_kv_handle,record,sizeof(record));
    return record[120];
}
uint32_t r1_device_info_configuration_word74_get(void)
{
    _Alignas(4) uint8_t record[124];
    (void)r1_kv_class_read(r1_device_info_kv_handle,record,sizeof(record));
    return read32(record+116);
}
/* Stock 0x7c8b0: persist the six-byte orientation calibration at offsets
 * 68..73, then drain pending NV writes. */
uint32_t r1_kv_nv_r1_field_set_a(const void *field)
{
    _Alignas(4) uint8_t record[124];
    const uint8_t *bytes = (const uint8_t *)field;
    (void)r1_kv_class_read(r1_device_info_kv_handle, record, sizeof(record));
    for (uint32_t i = 0; i < 6u; ++i)
        record[68u + i] = bytes[i];
    (void)r1_kv_class_write(r1_device_info_kv_handle, record, sizeof(record));
    return r1_nv_modules_idle_check();
}
/* Stock 0x7c93c: the system-control mode byte occupies record offset 112. */
uint32_t r1_kv_nv_r1_byte_set_c(uint32_t value)
{
    _Alignas(4) uint8_t record[124];
    (void)r1_kv_class_read(r1_device_info_kv_handle, record, sizeof(record));
    record[112] = (uint8_t)value;
    (void)r1_kv_class_write(r1_device_info_kv_handle, record, sizeof(record));
    return r1_nv_modules_idle_check();
}
void r1_kv_nv_r1_byte_set_a(uint32_t value)
{
    _Alignas(4) uint8_t record[124];
    (void)r1_kv_class_read(r1_device_info_kv_handle,record,sizeof(record));
    record[120]=(uint8_t)value;
    (void)r1_kv_class_write(r1_device_info_kv_handle,record,sizeof(record));
    (void)r1_nv_modules_idle_check();
}
void r1_kv_nv_r1_word_set_a(uint32_t value)
{
    _Alignas(4) uint8_t record[124];
    (void)r1_kv_class_read(r1_device_info_kv_handle,record,sizeof(record));
    write32(record+116,value);
    (void)r1_kv_class_write(r1_device_info_kv_handle,record,sizeof(record));
    (void)r1_nv_modules_idle_check();
}

/* Stock 0x7ca10: update the six address bytes in the same cached nv_r1
 * record, then let the NV modules drain their pending writes. */
uint32_t r1_kv_nv_r1_addr_set(const void *address)
{
    _Alignas(4) uint8_t record[124];
    const uint8_t *bytes = (const uint8_t *)address;
    (void)r1_kv_class_read(r1_device_info_kv_handle, record, sizeof(record));
    for (uint32_t i = 0; i < 6u; ++i)
        record[62u + i] = bytes[i];
    (void)r1_kv_class_write(r1_device_info_kv_handle, record, sizeof(record));
    return r1_nv_modules_idle_check();
}

/* Stock 0x7ca44: persisted model/serial-derived byte lives in the word at
 * nv_r1 offset 76. The caller supplies the full word. */
uint32_t r1_kv_nv_r1_word_set_b(uint32_t value)
{
    _Alignas(4) uint8_t record[124];
    (void)r1_kv_class_read(r1_device_info_kv_handle, record, sizeof(record));
    write32(record + 76u, value);
    (void)r1_kv_class_write(r1_device_info_kv_handle, record, sizeof(record));
    return r1_nv_modules_idle_check();
}
