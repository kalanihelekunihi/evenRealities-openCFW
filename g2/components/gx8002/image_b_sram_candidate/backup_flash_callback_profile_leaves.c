/* Native flash callback leaves 0x10007118 and 0x100072e8..0x1000734a.
 * The profile pointer graph is read from the live device descriptor; its
 * post-probe pointees are not fabricated as initialized data. */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_flash_descriptor_20016d60[8];
extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t, uint8_t *, uint32_t);
extern uint32_t gx8002_image_b_flash_write_10006cb0(
    uint32_t, const uint8_t *, uint32_t);
extern uint32_t gx8002_image_b_flash_program_pages_1000742c(
    uint32_t, const uint8_t *, uint32_t);
extern int32_t gx8002_image_b_flash_program_command_10006d34(
    const uint8_t *, uint32_t, uint32_t);
extern uint32_t gx8002_image_b_flash_status_apply_10006fec(
    uint32_t, uint32_t *);
extern uint32_t gx8002_image_b_flash_status_lookup_10006f04(void);

static volatile uint8_t *flash_profile(void)
{
    return (volatile uint8_t *)(uintptr_t)
        gx8002_image_b_flash_descriptor_20016d60[3];
}

static volatile uint32_t *flash_profile_child(void)
{
    volatile uint32_t *profile = (volatile uint32_t *)(uintptr_t)
        gx8002_image_b_flash_descriptor_20016d60[3];
    return (volatile uint32_t *)(uintptr_t)profile[5];
}

static uint32_t flash_profile_id(void)
{
    volatile uint8_t *profile = flash_profile();
    return (uint32_t)profile[6] | ((uint32_t)profile[7] << 8);
}

static uint8_t flash_profile_control_index(void)
{
    return (uint8_t)(flash_profile_child()[4] & 7u);
}

static void flash_wait_ready(void)
{
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
}

uint32_t gx8002_image_b_flash_callback_10007118(void)
{
    uint8_t status;
    uint32_t last_result;
    do {
        last_result = gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
    return last_result;
}

int32_t gx8002_image_b_flash_callback_1000715c(void)
{
    uint8_t index = flash_profile_control_index();
    flash_wait_ready();
    uint32_t id = flash_profile_id();
    if (id != 94u && id != 133u) return -1;
    uint8_t pair[2];
    (void)gx8002_image_b_flash_read_10006c30(5u, &pair[0], 1u);
    (void)gx8002_image_b_flash_read_10006c30(53u, &pair[1], 1u);
    pair[1] = (uint8_t)(pair[1] | (uint8_t)(1u << (index + 3u)));
    (void)gx8002_image_b_flash_program_command_10006d34(pair, 2u, 1u);
    return 0;
}

int32_t gx8002_image_b_flash_callback_100071d4(uint8_t *out)
{
    uint8_t index = flash_profile_control_index();
    flash_wait_ready();
    uint32_t id = flash_profile_id();
    if (id != 94u && id != 133u) return -1;
    uint8_t second_status;
    (void)gx8002_image_b_flash_read_10006c30(53u, &second_status, 1u);
    *out = (uint8_t)((second_status >> (index + 3u)) & 1u);
    return 0;
}

uint32_t gx8002_image_b_flash_callback_1000723c(void)
{
    uint32_t id = flash_profile_id();
    if (id != 94u && id != 133u) return 0u;

    volatile uint32_t *child = flash_profile_child();
    uint32_t index = child[4] & 7u;
    uint32_t base = child[0];
    uint32_t stride = child[1];
    volatile uint8_t *descriptor =
        (volatile uint8_t *)(void *)gx8002_image_b_flash_descriptor_20016d60;
    descriptor[0x10u] = 68u;
    flash_wait_ready();
    (void)gx8002_image_b_flash_write_10006cb0(6u, (const uint8_t *)0, 0u);

    /* Native bmaski 29 followed by 32-bit add and lsli 3 is equivalent
     * to (word-1)*8 modulo 2^32. Register lsr uses its low five bits. */
    uint32_t shift = (gx8002_image_b_flash_descriptor_20016d60[2] +
                      UINT32_C(0x1fffffff)) << 3;
    uint32_t word = base + index * stride;
    descriptor[0x11u] = (uint8_t)(word >> (shift & 31u));
    descriptor[0x12u] = (uint8_t)(word >> ((shift - 8u) & 31u));
    descriptor[0x13u] = (uint8_t)(word >> ((shift - 16u) & 31u));
    descriptor[0x14u] = (uint8_t)(word >> ((shift - 24u) & 31u));
    (void)gx8002_image_b_flash_write_10006cb0(
        descriptor[0x10u], (const uint8_t *)(const void *)(descriptor + 0x11u), 3u);
    flash_wait_ready();
    return 0u;
}

void gx8002_image_b_flash_callback_100075d0(
    uint32_t address, uint32_t length, uint32_t *first, uint32_t *last_end)
{
    *first = 0u;
    if ((int32_t)gx8002_image_b_flash_descriptor_20016d60[0] < 0)
        return;
    uint32_t pages = gx8002_image_b_flash_descriptor_20016d60[1] >> 12;
    if (pages == 0u) return;
    uint32_t extent = pages << 12;
    uint32_t found = 0u;

    for (uint32_t start = 0u; start < extent; start += 4096u) {
        uint32_t end = start + 4096u;
        if (address >= start && address < end) {
            *first = start;
            *last_end = 0u;
            found = 1u;
            break;
        }
    }
    if (found == 0u) return;

    uint32_t final_address = address + length - 1u;
    for (uint32_t start = 0u; start < extent; start += 4096u) {
        uint32_t end = start + 4096u;
        if (final_address >= start && final_address < end) {
            *last_end = end;
            return;
        }
    }
}

int32_t gx8002_image_b_flash_callback_10006fc8(void)
{
    volatile uint32_t *profile = (volatile uint32_t *)(uintptr_t)
        gx8002_image_b_flash_descriptor_20016d60[3];
    uint32_t nested = profile[4];
    if (nested == 0u) return -1;
    return (*(volatile uint32_t *)(uintptr_t)nested != 0u) ? 1 : -1;
}

int32_t gx8002_image_b_flash_callback_10006fac(uint32_t *out)
{
    *out = 0u;
    uint32_t match = gx8002_image_b_flash_status_lookup_10006f04();
    *out = match;
    return match == UINT32_MAX ? -1 : 0;
}

uint32_t gx8002_image_b_flash_callback_100070f8(uint32_t requested)
{
    uint32_t matched_value;
    return gx8002_image_b_flash_status_apply_10006fec(requested,
                                                        &matched_value);
}

uint32_t gx8002_image_b_flash_callback_10007108(void)
{
    uint32_t matched_value;
    return gx8002_image_b_flash_status_apply_10006fec(0u, &matched_value);
}

int32_t gx8002_image_b_flash_callback_100074c0(
    uint32_t address, const uint8_t *source, uint32_t length)
{
    if (length == 0u) return 0;
    if (gx8002_image_b_flash_descriptor_20016d60[1] < address + length)
        return -22;
    return (int32_t)gx8002_image_b_flash_program_pages_1000742c(
        address, source, length);
}

uint32_t gx8002_image_b_flash_callback_100072e8(uint32_t *out)
{
    *out = flash_profile_child()[3];
    return 0u;
}

uint32_t gx8002_image_b_flash_callback_100072fc(uint32_t value)
{
    volatile uint32_t *child = flash_profile_child();
    if (value >= child[3]) return UINT32_MAX;
    child[4] = (child[4] & ~UINT32_C(7)) | value;
    return 0u;
}

uint32_t gx8002_image_b_flash_callback_10007324(uint32_t *out)
{
    *out = flash_profile_child()[4] & 7u;
    return 0u;
}

uint32_t gx8002_image_b_flash_callback_1000733c(uint32_t *out)
{
    *out = flash_profile_child()[2];
    return 0u;
}
