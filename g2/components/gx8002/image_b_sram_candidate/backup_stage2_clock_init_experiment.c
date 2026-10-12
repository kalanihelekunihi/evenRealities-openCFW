/* Full stock image-B clock initialization CFG 0x10003294..0x100034b9.
 * Native instructions determine call order, parameters, wake branches, MMIO
 * writes and the terminal failure loop. Pinned NationalChip Grus clock
 * sources establish register roles; product RAM records remain extern.
 * This is an unselected source candidate until its children/data are linked.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_clock_mux_select_100080f4(uint32_t);
extern int32_t gx8002_image_b_clock_module_select_100035c0(uint32_t, uint32_t);
extern uint32_t gx8002_image_b_preserve_memory_10003ffc(void);
extern void gx8002_image_b_clock_config_10003788(uint32_t, uint32_t);
extern void gx8002_image_b_clock_config_flags_100038e8(uint32_t, uint32_t, uint32_t);
extern void gx8002_image_b_clock_register_apply_100035a0(const void *);
extern void gx8002_image_b_platform_gate_10003be8(uint32_t, uint32_t);
extern uint32_t gx8002_image_b_gated_status_1000401c(void);
extern void gx8002_image_b_clock_state_refresh_10003b08(void *);
extern int32_t gx8002_image_b_clock_trim_apply_100039f4(void *, uint32_t);

/* The original RAM addresses are known, but contents/producers are not yet
 * source-owned. A final linker must bind these exact live records. */
extern volatile uint8_t gx8002_image_b_clock_state_200168c0[];
extern volatile uint8_t gx8002_image_b_clock_boot_records_200168fc[];
extern volatile uint8_t gx8002_image_b_clock_trim_records_2001694c[];
extern volatile uint32_t gx8002_image_b_clock_gate_bits_20017394;

static void apply_records(volatile uint8_t *first, uint32_t count)
{
    for (uint32_t i = 0; i < count; ++i)
        gx8002_image_b_clock_register_apply_100035a0((const void *)(first + i * 8u));
}

static void configure_modules(void)
{
    static const uint8_t selection[][2] = {
        {10,1}, {6,1}, {0,2}, {1,0}, {3,0}, {4,0}, {5,0},
        {2,1}, {7,3}, {8,5}, {9,0}, {22,0}, {16,1}, {11,1},
        {19,1}, {12,1}, {13,1}, {14,1}, {15,1}
    };
    static const uint16_t config[][2] = {
        {6,2}, {0,4}, {1,3}, {3,2}, {2,2}, {7,384},
        {8,12}, {19,2}, {10,0}, {12,6}, {13,2}, {15,4}, {14,4}
    };

    for (uint32_t i = 0; i < sizeof(selection) / sizeof(selection[0]); ++i)
        (void)gx8002_image_b_clock_module_select_100035c0(selection[i][0], selection[i][1]);

    (void)gx8002_image_b_clock_config_flags_100038e8(2u, 0x01000000u, 1u);
    for (uint32_t i = 0; i < 8u; ++i)
        (void)gx8002_image_b_clock_config_10003788(config[i][0], config[i][1]);
    (void)gx8002_image_b_clock_config_flags_100038e8(16u, 0x01000000u, 1u);
    (void)gx8002_image_b_clock_config_flags_100038e8(11u, 0x00800000u, 1u);
    for (uint32_t i = 8u; i < sizeof(config) / sizeof(config[0]); ++i)
        (void)gx8002_image_b_clock_config_10003788(config[i][0], config[i][1]);
}

static void finish_clock(uint32_t wake_state)
{
    if (wake_state == 1u) {
        for (uint32_t module = 11u; module < 26u; ++module)
            gx8002_image_b_platform_gate_10003be8(
                module, (gx8002_image_b_clock_gate_bits_20017394 >> module) & 1u);
    }
    gx8002_image_b_platform_gate_10003be8(5u, 1u);
    volatile uint32_t *const pmic = (volatile uint32_t *)(uintptr_t)0xa0005084u;
    volatile uint32_t *const clock = (volatile uint32_t *)(uintptr_t)0xa0005060u;
    *pmic &= ~1u;
    *clock &= ~2u;
    (void)gx8002_image_b_clock_mux_select_100080f4(2u);
}

void gx8002_image_b_clock_init_10003294(void)
{
    (void)gx8002_image_b_clock_mux_select_100080f4(2u);
    (void)gx8002_image_b_clock_config_10003788(6u, 2u);
    const uint32_t wake_state = gx8002_image_b_preserve_memory_10003ffc();

    if (wake_state == 0u) {
        if (gx8002_image_b_gated_status_1000401c() == 1u) {
            volatile uint32_t *const trim =
                (volatile uint32_t *)(void *)(gx8002_image_b_clock_state_200168c0 + 0x38u);
            uint32_t step[5] = {0u, 10u, 15u, (uint32_t)-10, (uint32_t)-15};
            *trim = 1u;
            const uint32_t base = *(volatile uint32_t *)(void *)(gx8002_image_b_clock_state_200168c0 + 0x14u);
            uint32_t index = 0u;
            for (;;) {
                *(volatile uint32_t *)(void *)(gx8002_image_b_clock_state_200168c0 + 0x14u) = base + step[index];
                if (gx8002_image_b_clock_trim_apply_100039f4(
                        (void *)gx8002_image_b_clock_state_200168c0, 40u) == 0)
                    break;
                ++index;
                if (index == 5u)
                    for (;;) { __asm__ volatile ("" ::: "memory"); }
            }
            apply_records(gx8002_image_b_clock_trim_records_2001694c, 10u);
        } else {
            apply_records(gx8002_image_b_clock_boot_records_200168fc, 10u);
        }
    } else if (wake_state == 1u) {
        struct clock_record { uint32_t shift; uint8_t value; uint8_t padding[3]; };
        struct clock_record records[2] = {{16u, 0u, {0u}}, {0u, 1u, {0u}}};
        if (*(volatile uint32_t *)(void *)(gx8002_image_b_clock_state_200168c0 + 0x38u) == 1u)
            gx8002_image_b_clock_state_refresh_10003b08((void *)gx8002_image_b_clock_state_200168c0);
        gx8002_image_b_clock_register_apply_100035a0(records);
        gx8002_image_b_clock_register_apply_100035a0(&records[1]);
    }

    configure_modules();
    finish_clock(wake_state);
}
