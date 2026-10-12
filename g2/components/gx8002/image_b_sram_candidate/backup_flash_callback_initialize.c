/* Native image-B flash interface initializer 0x10007d78..0x10007efe.
 * Label flow follows the original JEDEC classification branch graph. In
 * particular some rejected IDs revisit a status setter without a timeout;
 * that native behavior is not replaced with an invented failure policy. */
#include <stdint.h>

extern int32_t gx8002_image_b_platform_write_1001574c(uint32_t, const void *);
extern void gx8002_image_b_platform_gate_10003be8(uint32_t, uint32_t);
extern void gx8002_image_b_request_irq_10004844(
    uint32_t, int32_t (*)(int32_t, void *), uint32_t);
extern uint32_t gx8002_image_b_flash_interrupt_10007138(void);
extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t, uint8_t *, uint32_t);
extern int32_t gx8002_image_b_flash_probe_10007c90(void);
extern void gx8002_image_b_flash_protection_initialize_10007f80(void);
extern uint32_t gx8002_image_b_flash_set_status_bit_10007370(void);
extern uint32_t gx8002_image_b_flash_set_second_status_bit_100073b4(void);
extern uint32_t gx8002_image_b_flash_set_configuration_bit_100073f0(void);
extern int32_t gx8002_image_b_flash_program_command_10006d34(
    const uint8_t *, uint32_t, uint32_t);
extern volatile uint32_t gx8002_image_b_flash_descriptor_20016d60[8];
extern uintptr_t gx8002_image_b_flash_probe_callback_20016d80[31];

/* Native bodies 0x10006d90 and 0x100074ec are separately tracked callable
 * contracts; the initializer only installs their typed function addresses. */
extern uint32_t gx8002_image_b_flash_callback_low_read_10006d90(
    uint32_t, const uint32_t *, uint32_t);
extern uint32_t gx8002_image_b_flash_callback_low_write_100074ec(
    uint32_t, uint32_t *, uint32_t);

static volatile uint32_t *const flash =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
static volatile uint32_t *const clock_gate =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300090);
static volatile uint32_t *const flash_aux =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2800070);

uint32_t gx8002_image_b_flash_callback_10007d78(void)
{
    uint32_t zero = 0u;
    (void)gx8002_image_b_platform_write_1001574c(9u, &zero);
    gx8002_image_b_platform_gate_10003be8(13u, 1u);
    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    flash[0x08u / 4u] = 0u;
    *clock_gate = 1u;
    flash[0x2cu / 4u] = 78u;
    *flash_aux = 1u;
    flash[0x14u / 4u] = 4u;
    flash[0x1cu / 4u] = 31u;
    flash[0x08u / 4u] = 1u;
    gx8002_image_b_request_irq_10004844(
        15u,
        (int32_t (*)(int32_t, void *))(uintptr_t)
            &gx8002_image_b_flash_interrupt_10007138,
        0u);

    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
    if (gx8002_image_b_flash_probe_10007c90() != 0) return 0u;

    gx8002_image_b_flash_protection_initialize_10007f80();
    flash[0x08u / 4u] = 0u;
    flash[0x14u / 4u] = 2u;
    volatile uint8_t *profile = (volatile uint8_t *)(uintptr_t)
        gx8002_image_b_flash_descriptor_20016d60[3];
    uint32_t id = *(volatile uint32_t *)(void *)(profile + 4u);

    if (id > UINT32_C(0x856014)) goto high_ids;
    if (id >= UINT32_C(0x856013)) goto set_first_status;
    if (id <= UINT32_C(0x1c3813)) goto low_ids;
    if (id == UINT32_C(0x684015)) {
        (void)gx8002_image_b_flash_set_second_status_bit_100073b4();
        (void)gx8002_image_b_flash_set_status_bit_10007370();
        goto install_callbacks;
    }
    goto mid_ids;

high_ids:
    if (id == UINT32_C(0xc84215)) goto set_first_status;
    if (id > UINT32_C(0xc84215)) goto highest_ids;
    if (id == UINT32_C(0xba6015)) goto set_first_status;
    if (id <= UINT32_C(0xba6015)) goto b360_id;
    if (id != UINT32_C(0xc22017)) goto c840_id;
    (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    if ((status & 64u) != 0u) goto install_callbacks;
    goto set_status_64;

mid_ids:
    if (id == UINT32_C(0x854012)) goto set_first_status;
    if (id != UINT32_C(0x1c7017)) goto set_second_status;
    if (id != UINT32_C(0x204016)) goto install_callbacks;
    (void)gx8002_image_b_flash_set_configuration_bit_100073f0();
    goto install_callbacks;

low_ids:
    if (id >= UINT32_C(0x1c3812)) goto repeat_classification;
    if (id == UINT32_C(0x0b4014)) goto set_first_status;
    if (id < UINT32_C(0x0b4014)) goto set_second_status;
    if (id + UINT32_C(0xfff4bfea) >= 2u) goto set_second_status;
    goto set_first_status;

highest_ids:
    if (id == UINT32_C(0xcd7015)) goto set_first_status;
    if (id <= UINT32_C(0xcd7015)) goto special_high_ids;
    if (id == UINT32_C(0xef4015)) goto set_first_status;
    goto set_second_status;

special_high_ids:
    if (id + UINT32_C(0xff379feb) >= 2u) goto set_second_status;
    goto set_first_status;

b360_id:
    if (id != UINT32_C(0xb36014)) goto set_second_status;
    goto set_first_status;

c840_id:
    if (id != UINT32_C(0xc84015)) goto set_second_status;
    goto set_first_status;

set_first_status:
    (void)gx8002_image_b_flash_set_status_bit_10007370();
    goto repeat_classification;

set_second_status:
    (void)gx8002_image_b_flash_set_second_status_bit_100073b4();

repeat_classification:
    if (id != UINT32_C(0x1c7017)) goto set_second_status;
    if (id != UINT32_C(0x204016)) goto install_callbacks;
    (void)gx8002_image_b_flash_set_configuration_bit_100073f0();
    goto install_callbacks;

set_status_64:
    status = (uint8_t)(status | 64u);
    (void)gx8002_image_b_flash_program_command_10006d34(&status, 1u, 1u);
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);

install_callbacks:
    gx8002_image_b_flash_descriptor_20016d60[6] =
        (uint32_t)(uintptr_t)&gx8002_image_b_flash_callback_low_read_10006d90;
    gx8002_image_b_flash_descriptor_20016d60[7] =
        (uint32_t)(uintptr_t)&gx8002_image_b_flash_callback_low_write_100074ec;
    return (uint32_t)(uintptr_t)
        gx8002_image_b_flash_probe_callback_20016d80;
}
