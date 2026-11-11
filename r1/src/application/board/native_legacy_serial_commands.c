/* Stock 0x6244e/0x624f4 and their nv_r1 serial-record helpers. */
#include <stdint.h>
#include "native_kv_class.h"
#include "native_product_bsn.h"

extern void *volatile r1_device_info_kv_handle;
extern uint32_t r1_nv_modules_idle_check(void);
extern uint32_t r1_legacy_bounded_reply_send(const void *, uint32_t);

/* Stock 0x5678c: accumulate every difference before returning equality. */
uint32_t r1_constant_time_compare(const uint8_t *left, const uint8_t *right,
                                   uint32_t length)
{
    uint32_t differences = 0u;
    for (uint32_t i = 0; i < length; ++i)
        differences |= (uint32_t)(left[i] ^ right[i]);
    return differences == 0u;
}

/* Stock 0x7c968: first serial string occupies bytes 0..29, length byte 30. */
uint32_t r1_kv_nv_r1_string_set_a(const void *source, uint32_t length)
{
    _Alignas(4) uint8_t record[124];
    const uint8_t *bytes = (const uint8_t *)source;
    if (length > 30u)
        length = 30u;
    (void)r1_kv_class_read(r1_device_info_kv_handle, record, sizeof(record));
    for (uint32_t i = 0; i < length; ++i)
        record[i] = bytes[i];
    record[30] = (uint8_t)length;
    (void)r1_kv_class_write(r1_device_info_kv_handle, record, sizeof(record));
    return r1_nv_modules_idle_check();
}

/* Stock 0x7c9a8: second serial string begins at byte 31, length byte 61. */
uint32_t r1_kv_nv_r1_string_set_b(const void *source, uint32_t length)
{
    _Alignas(4) uint8_t record[124];
    const uint8_t *bytes = (const uint8_t *)source;
    if (length > 30u)
        length = 30u;
    (void)r1_kv_class_read(r1_device_info_kv_handle, record, sizeof(record));
    for (uint32_t i = 0; i < length; ++i)
        record[31u + i] = bytes[i];
    record[61] = (uint8_t)length;
    (void)r1_kv_class_write(r1_device_info_kv_handle, record, sizeof(record));
    return r1_nv_modules_idle_check();
}

/* Stock 0x7ba78 reads exactly 15 bytes, even when the stored length differs.
 * An erased length (0xff) yields 15 bytes of 0xff and an optional zero size. */
void r1_product_sn_get(void *destination, uint8_t *length)
{
    _Alignas(4) uint8_t record[124];
    uint8_t *output = (uint8_t *)destination;
    (void)r1_kv_class_read(r1_device_info_kv_handle, record, sizeof(record));
    if (record[61] == 0xffu) {
        for (uint32_t i = 0; i < 15u; ++i)
            output[i] = 0xffu;
        if (length != 0)
            *length = 0u;
    } else {
        for (uint32_t i = 0; i < 15u; ++i)
            output[i] = record[31u + i];
        if (length != 0)
            *length = 15u;
    }
}

/* Stock 0x6244e: selector zero stores 21 BSN bytes and verifies their
 * readback; selector one sends 21 stored bytes. Both reply branches return
 * zero after sending, independently of the transport result. */
uint32_t r1_legacy_bsn_verify_command(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = (uint8_t *)packet;
    uint8_t readback[24] = {0};
    if (bytes[3] == 0u) {
        (void)r1_kv_nv_r1_string_set_a(bytes + 4, 21u);
        (void)r1_product_bsn_read(readback, 21u);
        bytes[4] = (uint8_t)r1_constant_time_compare(readback, bytes + 4, 21u);
        (void)r1_legacy_bounded_reply_send(packet, 5u);
    } else if (bytes[3] == 1u) {
        (void)r1_product_bsn_read(bytes + 4, 21u);
        (void)r1_legacy_bounded_reply_send(packet, 25u);
    }
    return 0u;
}

/* Stock 0x624f4 uses a 21-byte comparison even though the SN getter
 * populates only 15 bytes of its zeroed readback. */
uint32_t r1_legacy_sn_verify_command(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = (uint8_t *)packet;
    uint8_t readback[24] = {0};
    if (bytes[3] == 0u) {
        (void)r1_kv_nv_r1_string_set_b(bytes + 4, 21u);
        r1_product_sn_get(readback, 0);
        bytes[4] = (uint8_t)r1_constant_time_compare(readback, bytes + 4, 21u);
        (void)r1_legacy_bounded_reply_send(packet, 5u);
    } else if (bytes[3] == 1u) {
        r1_product_sn_get(bytes + 4, 0);
        (void)r1_legacy_bounded_reply_send(packet, 25u);
    }
    return 0u;
}
