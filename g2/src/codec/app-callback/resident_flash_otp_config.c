/* SPDX-License-Identifier: MIT
 * Image-A SRAM OTP configuration/status accessors, stock 0x10023ae0,
 * 0x10023b24, 0x10023b38, 0x10023b60, 0x10023b78, 0x10024250.
 * The selected flash descriptor's OTP layout is required product input.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);
extern uint8_t gx8002_resident_flash_read_status_23734(void);
extern uint8_t gx8002_resident_flash_read_status2_23770(void);
extern uint32_t gx8002_resident_flash_write_enable_2374c(void);
extern uint32_t gx8002_resident_flash_command_write_236dc(
    uint32_t, const uint8_t *, int32_t);

struct resident_otp_config {
    uint32_t field0;
    uint32_t field4;
    uint32_t region_size;
    uint32_t region_count;
    uint32_t current_region;
};
_Static_assert(sizeof(struct resident_otp_config) == 20,
               "native OTP config ABI");

static volatile struct resident_otp_config *otp_config(void)
{
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile uint32_t *const selected =
        (const volatile uint32_t *)(uintptr_t)state[3];
    return (volatile struct resident_otp_config *)(uintptr_t)selected[5];
}

static uint16_t selected_type(void)
{
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile uint32_t *const selected =
        (const volatile uint32_t *)(uintptr_t)state[3];
    return (uint16_t)(selected[1] >> 16);
}

/* Stock 0x10023AE0 (gx8002_flash_otp_status) */
int32_t gx8002_resident_flash_otp_status_23ae0(uint8_t *locked)
{
    uint32_t region = otp_config()->current_region & 7u;
    gx8002_resident_flash_wait_ready_2375c();
    uint16_t type = selected_type();
    if (type != 0x5eu && type != 0x85u) return -1;
    uint8_t status = gx8002_resident_flash_read_status2_23770();
    *locked = (uint8_t)((status >> (region + 3u)) & 1u);
    return 0;
}

/* Stock 0x10023B24 (gx8002_flash_otp_get_region) */
uint32_t gx8002_resident_flash_otp_get_region_23b24(uint32_t *count)
{
    *count = otp_config()->region_count;
    return 0u;
}

/* Stock 0x10023B38 (gx8002_flash_otp_set_region) */
int32_t gx8002_resident_flash_otp_set_region_23b38(uint32_t region)
{
    volatile struct resident_otp_config *config = otp_config();
    if (region >= config->region_count) return -1;
    config->current_region = (config->current_region & ~UINT32_C(7)) | region;
    return 0;
}

/* Stock 0x10023B60 (gx8002_flash_otp_get_current_region) */
uint32_t gx8002_resident_flash_otp_get_current_region_23b60(
    uint32_t *region)
{
    *region = otp_config()->current_region & 7u;
    return 0u;
}

/* Stock 0x10023B78 (gx8002_flash_otp_get_region_size) */
uint32_t gx8002_resident_flash_otp_get_region_size_23b78(
    uint32_t *bytes)
{
    *bytes = otp_config()->region_size;
    return 0u;
}

/* Stock 0x10024250 (gx8002_flash_otp_lock) */
int32_t gx8002_resident_flash_otp_lock_24250(void)
{
    uint32_t region = otp_config()->current_region & 7u;
    gx8002_resident_flash_wait_ready_2375c();
    uint16_t type = selected_type();
    if (type != 0x5eu && type != 0x85u) return -1;
    uint8_t statuses[2] = {
        gx8002_resident_flash_read_status_23734(),
        gx8002_resident_flash_read_status2_23770()
    };
    statuses[1] |= (uint8_t)(UINT32_C(1) << (region + 3u));
    gx8002_resident_flash_wait_ready_2375c();
    gx8002_resident_flash_write_enable_2374c();
    gx8002_resident_flash_command_write_236dc(1u, statuses, 2);
    return 0;
}
