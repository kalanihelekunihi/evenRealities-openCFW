/* Stock 0x62a5c: legacy device information and flash geometry. */
#include <stdint.h>
#include "native_product_bsn.h"

extern void r1_product_sn_get(void *, uint8_t *);
extern uint32_t r1_temperature_calibration_read(void *);
extern uint32_t r1_accelerometer_calibration_read(void *);
extern uint32_t r1_device_info_configuration_byte70_get(void);
extern uint32_t r1_device_info_configuration_word74_get(void);
extern uint32_t r1_device_info_configuration_byte78_get(void);
extern uint32_t r1_legacy_bounded_reply_send(const void *, uint32_t);

static void put_word(uint8_t *destination, uint32_t value)
{
    for (uint32_t i = 0; i < 4u; ++i)
        destination[i] = (uint8_t)(value >> (8u * i));
}

/* The helper accepts the three stock register words so a host probe can
 * exercise every selector without mapping Nordic information flash. */
uint32_t r1_legacy_device_info_build_body(uint32_t handle, void *packet,
                                           uint32_t bootloader_address,
                                           uint32_t flash_page_size,
                                           uint32_t flash_page_count)
{
    (void)handle;
    uint8_t *bytes = (uint8_t *)packet;
    uint8_t geometry[20] = {0};
    uint32_t flash_limit = bootloader_address == UINT32_MAX
                               ? flash_page_size * flash_page_count
                               : bootloader_address;
    put_word(geometry, bootloader_address);
    put_word(geometry + 4u, flash_page_size);
    put_word(geometry + 8u, flash_page_count);
    put_word(geometry + 12u, flash_limit);
    put_word(geometry + 16u, flash_limit - 36u * flash_page_size);

    switch (bytes[3]) {
    case 0u:
        for (uint32_t i = 4u; i < 36u; ++i)
            bytes[i] = 0u;
        (void)r1_product_bsn_read(bytes + 4u, 30u);
        return r1_legacy_bounded_reply_send(packet, 25u);
    case 1u:
        for (uint32_t i = 4u; i < 36u; ++i)
            bytes[i] = 0u;
        r1_product_sn_get(bytes + 4u, 0);
        return r1_legacy_bounded_reply_send(packet, 25u);
    case 2u:
        (void)r1_temperature_calibration_read(bytes + 4u);
        (void)r1_accelerometer_calibration_read(bytes + 10u);
        return r1_legacy_bounded_reply_send(packet, 13u);
    case 3u: {
        uint8_t response[43] = {0};
        for (uint32_t i = 0; i < 4u; ++i)
            response[i] = bytes[i];
        for (uint32_t i = 4u; i < 40u; ++i)
            response[i] = 0xffu;
        response[40] = (uint8_t)r1_device_info_configuration_byte70_get();
        response[41] = (uint8_t)r1_device_info_configuration_word74_get();
        response[42] = (uint8_t)r1_device_info_configuration_byte78_get();
        return r1_legacy_bounded_reply_send(response, sizeof(response));
    }
    case 4u:
        for (uint32_t i = 0; i < sizeof(geometry); ++i)
            bytes[4u + i] = geometry[i];
        return r1_legacy_bounded_reply_send(packet, 24u);
    default:
        return 0u;
    }
}

uint32_t r1_legacy_device_info_build(uint32_t handle, void *packet)
{
    const volatile uint32_t *custom =
        (const volatile uint32_t *)(uintptr_t)0x10001014u;
    const volatile uint32_t *device =
        (const volatile uint32_t *)(uintptr_t)0x10000010u;
    uint32_t bootloader_address = *custom;
    uint32_t flash_page_size = device[0];
    uint32_t flash_page_count = device[1];
    return r1_legacy_device_info_build_body(handle, packet,
                                             bootloader_address,
                                             flash_page_size,
                                             flash_page_count);
}
