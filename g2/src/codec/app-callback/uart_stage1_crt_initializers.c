/* SPDX-License-Identifier: MIT
 * UART boot stage-1 initializers called by the startup dispatcher at
 * 0x100001bc (firmware_codec.bin g2-2.2.6.10, FWPK seg1 at VMA 0x10000000):
 *
 *   0x100001fc  gx8002_uart_stage1_initialize_hardware  boot mode + host sync
 *   0x10001dd8  gx8002_uart_stage1_initialize_data      empty body (rts)
 *   0x10001378  gx8002_uart_stage1_initialize_runtime   spl_clk_init
 *   0x100002c8  gx8002_uart_stage1_start_application    stage-2 download
 *
 * plus the lower bodies only these reach: 0x10001ddc (spl_board_clk_init),
 * 0x10001094 (spl_clk_trim) and 0x100019c0 (sflash_readdata).
 *
 * Written from the stock instructions, following NationalChip lvp_kws
 * (8bf9ee5c) arch/soc/grus/spl/spl_clk.c and the clk_priv.h inlines it
 * expands. Where the stock inline expansion differs from that header (the
 * PDM clock-select mask, the PLL retry step and limit) the stock behaviour
 * is kept. The clock descriptor lookup (0x10000780), the out-of-line clock
 * helpers and UART I/O are the existing uart_stage1_*.c units.
 *
 * Functions and read-only tables are named gx8002_uart_stage1_* (STAGE1
 * text); initialized data goes in .stage1.data.* sections, which the codec-a
 * link places in the stage-1 data image at its stock D-bus addresses. Shared
 * state is gx8002_uart_stage1_state (uart_stage1_state.h); 0x20002800 is the
 * stage-2 load address.
 */
#include <stdint.h>
#include <stddef.h>
#include "uart_stage1_pmu.h"
#include "uart_stage1_state.h"

#define STAGE1_REG32(address) (*(volatile uint32_t *)(uintptr_t)UINT32_C(address))

/* Lower stage-1 bodies (existing C units). */
extern void gx8002_uart_stage1_blkclr(void);                          /* 0x100004a4 */
extern void gx8002_uart_stage1_bringup(uint32_t first, uint32_t second); /* 0x100005c4 */
extern void gx8002_uart_stage1_put(uint32_t value);                   /* 0x10000584 */
extern void gx8002_uart_stage1_put_sync(uint32_t value);              /* 0x100005a0 */
extern int32_t gx8002_uart_stage1_try_get(uint8_t *out);              /* 0x10000620 */
extern uint32_t gx8002_uart_stage1_get_char(void);                    /* 0x10000640 */
extern int32_t gx8002_uart_stage1_announce(uint32_t first, uint32_t second); /* 0x1000065c */
extern void gx8002_uart_stage1_pmu_set_bit0(uint32_t value);          /* 0x10000374 */
extern void gx8002_uart_stage1_pmu_set_bit1(uint32_t value);          /* 0x1000038c */
extern void gx8002_uart_stage1_pmu_bit_modify(const uint32_t *descriptor); /* 0x10000840 */
                  /* 0x10000b90 */
extern int32_t gx8002_uart_stage1_uart_config(const uint32_t *config,
                                              uint32_t timeout_ms);   /* 0x10000c9c */
extern void gx8002_uart_stage1_pmu_dispatch(uint32_t selector, uint32_t enabled); /* 0x10000d98 */
extern void gx8002_uart_stage1_xip_read(uint32_t address, uint8_t *destination,
                                        uint32_t length);             /* 0x100018c0 */
extern void gx8002_uart_stage1_xip_write(uint32_t address, const uint8_t *source,
                                         uint32_t length);            /* 0x10001940 */
extern void gx8002_uart_stage1_announce_transfer(uint32_t first_address,
                                                 uintptr_t second_address,
                                                 uint32_t length,
                                                 uint32_t width);     /* 0x10001bf8 */
extern void gx8002_uart_stage1_postamble(void);                       /* 0x10001d9c */

/* Clock module numbers (GX_CLOCK_MODULE) used below. */
enum {
    STAGE1_CLOCK_PMU = 1,
    STAGE1_CLOCK_HW_I2C = 5,
    STAGE1_CLOCK_SRAM = 6,
    STAGE1_CLOCK_OSC_REF = 9,
    STAGE1_CLOCK_SCPU = 10,
    STAGE1_CLOCK_FLASH_SPI = 13,
    STAGE1_CLOCK_UART0_UART1 = 16,
    STAGE1_CLOCK_UART0 = 17,
    STAGE1_CLOCK_I2C0_I2C1 = 19,
    STAGE1_CLOCK_MODULE_MAX = 26,
};

/* ---------------------------------------------------------------------- */
/* 0x100001fc: boot mode and host synchronization.                         */

/* "OK", stock stage-1 rodata 0x10001e5c. */
static const uint8_t gx8002_uart_stage1_sync_pattern[] = {'O', 'K', 0};

void gx8002_uart_stage1_initialize_hardware(void)
{
    gx8002_uart_stage1_blkclr();
    if ((STAGE1_REG32(0xa0010068) & 15u) != 0u)
        return;

    /* Boot info: device 0 (UART) and the UART select nibble that
     * gx8002_uart_stage1_bringup reads back. */
    volatile uint32_t *const boot_info = gx8002_uart_stage1_state.boot_info;
    const uint32_t uart_select = (STAGE1_REG32(0xa0010068) >> 4) & 15u;
    boot_info[0] = 0;
    boot_info[1] = uart_select;
    gx8002_uart_stage1_bringup(1u, 0u);

    gx8002_uart_stage1_put_sync('w');
    gx8002_uart_stage1_put_sync('f');
    gx8002_uart_stage1_put_sync('b');

    /* Wait for the host to send "OK"; a mismatch restarts the match. */
    uint32_t matched = 0;
    while (gx8002_uart_stage1_sync_pattern[matched] != 0u) {
        uint8_t received;
        if (gx8002_uart_stage1_try_get(&received) != 0)
            continue;
        if (received == gx8002_uart_stage1_sync_pattern[matched])
            ++matched;
        else
            matched = 0;
    }

    /* Four host bytes, stored bytewise into host_word (read back as a word
     * by start_application, the handshake and stage 2). */
    volatile uint8_t *const host_word =
        (volatile uint8_t *)&gx8002_uart_stage1_state.host_word;
    for (uint32_t i = 0; i < 4u; ++i)
        host_word[i] = (uint8_t)gx8002_uart_stage1_get_char();

    gx8002_uart_stage1_put_sync('O');
    gx8002_uart_stage1_put_sync('K');
}

/* ---------------------------------------------------------------------- */
/* 0x100002c8: receive the stage-2 image into 0x20002800 and verify it.     */

void gx8002_uart_stage1_start_application(void)
{
    if (gx8002_uart_stage1_state.flags[0] == 3u)
        gx8002_uart_stage1_bringup(0u, gx8002_uart_stage1_state.host_word);

    /* Little-endian checksum, then little-endian length. */
    uint32_t checksum = 0;
    for (uint32_t i = 0; i < 4u; ++i)
        checksum |= (gx8002_uart_stage1_get_char() & 0xffu) << (8u * i);
    uint32_t length = 0;
    for (uint32_t i = 0; i < 4u; ++i)
        length |= (gx8002_uart_stage1_get_char() & 0xffu) << (8u * i);

    const volatile uint8_t *const image =
        (const volatile uint8_t *)(uintptr_t)UINT32_C(0x20002800);
    for (;;) {
        (void)gx8002_uart_stage1_announce(UINT32_C(0x20002800), length);
        uint32_t sum = 0;
        for (uint32_t i = 0; i < length; ++i)
            sum += image[i];
        if (sum == checksum)
            break;
        gx8002_uart_stage1_put('E');
    }
    gx8002_uart_stage1_put('O');
    /* The stock body also returns 0 in r0; the dispatcher ignores it. */
}

/* ---------------------------------------------------------------------- */
/* 0x10001dd8: stock body is a bare return.                                */

void gx8002_uart_stage1_initialize_data(void)
{
}

/* ---------------------------------------------------------------------- */
/* 0x100019c0: sflash_readdata(offset, to, len).                            */

/* JEDEC id of the attached NOR, 0xffffff until probed (stock 0x20002270). */
__attribute__((section(".stage1.data.flash_id")))
static uint32_t gx8002_uart_stage1_flash_id = UINT32_C(0x00ffffff);

static void gx8002_uart_stage1_flash_wait_ready(uint8_t *status)
{
    do {
        gx8002_uart_stage1_xip_read(0x05u, status, 1u);
    } while ((*status & 1u) != 0u);
}

/* First use: read the JEDEC id and set the status-2 QE bit (bit 1) unless
 * it is already set; ids 0x1c3812/0x1c3813 are left alone. 0x100018c0 always returns 0, so the stock check of
 * its result after the id read is never taken and is omitted. */
static void gx8002_uart_stage1_flash_probe(void)
{
    STAGE1_REG32(0xa0300090) = 1;
    STAGE1_REG32(0xa2000008) = 0;
    STAGE1_REG32(0xa200002c) = 0;
    STAGE1_REG32(0xa20000f0) = 1;
    STAGE1_REG32(0xa2000014) = 2;
    STAGE1_REG32(0xa200001c) = 31;
    STAGE1_REG32(0xa2000008) = 1;

    uint8_t id[4];
    gx8002_uart_stage1_xip_read(0x9fu, id, 3u);
    const uint32_t jedec = ((uint32_t)id[0] << 16) | ((uint32_t)id[1] << 8) | id[2];
    gx8002_uart_stage1_flash_id = jedec;

    uint8_t status[2];
    if (jedec == UINT32_C(0x854012) ||
        jedec - UINT32_C(0x856013) < 2u) {
        /* Write status 1 and 2 together (command 0x01, two bytes). */
        uint8_t status2;
        gx8002_uart_stage1_xip_read(0x05u, &status[0], 1u);
        gx8002_uart_stage1_xip_read(0x35u, &status2, 1u);
        if ((status2 & 2u) != 0u)
            return;
        status[1] = (uint8_t)(status2 | 2u);
        gx8002_uart_stage1_flash_wait_ready(&status2);
        gx8002_uart_stage1_xip_write(0x06u, NULL, 0u);
        gx8002_uart_stage1_xip_write(0x01u, status, 2u);
        gx8002_uart_stage1_flash_wait_ready(&status2);
    } else if (jedec - UINT32_C(0x1c3812) >= 2u) {
        /* Every other id but 0x1c3812/0x1c3813 (which need no QE write):
         * write status 2 alone (command 0x31). */
        gx8002_uart_stage1_xip_read(0x35u, &status[0], 1u);
        if ((status[0] & 2u) != 0u)
            return;
        const uint8_t status2 = (uint8_t)(status[0] | 2u);
        gx8002_uart_stage1_flash_wait_ready(&status[0]);
        gx8002_uart_stage1_xip_write(0x06u, NULL, 0u);
        gx8002_uart_stage1_xip_write(0x31u, &status2, 1u);
        gx8002_uart_stage1_flash_wait_ready(&status[0]);
    }
}

int32_t gx8002_uart_stage1_sflash_read(uint32_t offset, void *to, uint32_t length)
{
    volatile uint32_t *const spi = (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    uint8_t *destination = (uint8_t *)to;

    gx8002_uart_stage1_pmu_dispatch(STAGE1_CLOCK_FLASH_SPI, 1u);
    if (gx8002_uart_stage1_flash_id == UINT32_C(0x00ffffff))
        gx8002_uart_stage1_flash_probe();

    uint8_t status;
    gx8002_uart_stage1_flash_wait_ready(&status);

    while (length != 0u) {
        const uint32_t chunk =
            (int32_t)length < 0x10000 ? length : UINT32_C(0x10000);
        while ((spi[0x28 / 4] & 1u) != 0u) { }
        spi[0x4c / 4] = 0;
        spi[0x08 / 4] = 0;
        spi[0x10 / 4] = 0;
        spi[0x00 / 4] = UINT32_C(0x800807);
        spi[0x04 / 4] = chunk - 1u;
        spi[0x18 / 4] = 0;
        spi[0x54 / 4] = 7;
        if (gx8002_uart_stage1_flash_id - UINT32_C(0x1c3812) < 2u) {
            spi[0xf4 / 4] = UINT32_C(0x40003219);
            spi[0x08 / 4] = 1;
            spi[0x64 / 4] = 0xebu;            /* quad I/O fast read */
        } else {
            spi[0xf4 / 4] = UINT32_C(0x40004218);
            spi[0x08 / 4] = 1;
            spi[0x64 / 4] = 0x6bu;            /* quad output fast read */
        }
        spi[0x64 / 4] = offset;
        spi[0x10 / 4] = 1;
        spi[0x4c / 4] = 1;
        gx8002_uart_stage1_announce_transfer((uint32_t)(uintptr_t)destination,
                                             (uintptr_t)UINT32_C(0xa2000060),
                                             chunk, 10u);
        gx8002_uart_stage1_postamble();
        spi[0x4c / 4] = 0;
        while (spi[0x24 / 4] != 0u) { }
        while ((spi[0x28 / 4] & 1u) != 0u) { }
        length -= chunk;
        offset += chunk;
        destination += chunk;
    }

    gx8002_uart_stage1_pmu_dispatch(STAGE1_CLOCK_FLASH_SPI, 0u);
    return 0;
}

/* ---------------------------------------------------------------------- */
/* 0x10001094: spl_clk_trim.                                               */

/* struct grus_cfg at flash 0xff000, magic "GRUS" (GRUS_CFG_MAGIC). */
struct gx8002_uart_stage1_grus_cfg {
    uint32_t magic;
    uint32_t version;
    uint32_t trim_32k_value;
    uint32_t trim_1m_value;
    uint32_t trim_24m_value;
    uint8_t reserved[43];
    uint8_t xor_result;
};
_Static_assert(sizeof(struct gx8002_uart_stage1_grus_cfg) == 64, "grus_cfg ABI");

/* {source offset, select} pairs, stock 0x200021b8..0x200021d7:
 * low  {CLOCK_SOURCE_1M, 0}, {CLOCK_SOURCE_1M_12M, 1};
 * high {CLOCK_SOURCE_24M, 0}, {CLOCK_SOURCE_24M_PLL, 0}. */
__attribute__((section(".stage1.data.trim_sources")))
static const uint32_t gx8002_uart_stage1_trim_low_sources[2][2] = {
    {28u, 0u}, {18u, 1u},
};
__attribute__((section(".stage1.data.trim_sources")))
static const uint32_t gx8002_uart_stage1_trim_high_sources[2][2] = {
    {16u, 0u}, {0u, 0u},
};

int32_t gx8002_uart_stage1_clk_trim(void)
{
    struct gx8002_uart_stage1_grus_cfg cfg __attribute__((aligned(16)));

    gx8002_uart_stage1_pmu_dispatch(STAGE1_CLOCK_OSC_REF, 1u);
    (void)gx8002_uart_stage1_sflash_read(UINT32_C(0xff000), &cfg, sizeof cfg);
    if (cfg.magic != UINT32_C(0x47525553))
        return -1;
    const uint8_t *const bytes = (const uint8_t *)&cfg;
    uint8_t xor_result = bytes[0];
    for (uint32_t i = 1; i < sizeof cfg - 1u; ++i)
        xor_result ^= bytes[i];
    if (xor_result != cfg.xor_result)
        return -1;

    STAGE1_REG32(0xa0004024) = cfg.trim_32k_value;
    STAGE1_REG32(0xa0004028) = cfg.trim_1m_value;
    gx8002_uart_stage1_pmu_bit_modify(gx8002_uart_stage1_trim_low_sources[0]);
    gx8002_uart_stage1_pmu_bit_modify(gx8002_uart_stage1_trim_low_sources[1]);
    STAGE1_REG32(0xa000402c) = cfg.trim_24m_value;
    gx8002_uart_stage1_pmu_bit_modify(gx8002_uart_stage1_trim_high_sources[0]);
    gx8002_uart_stage1_pmu_bit_modify(gx8002_uart_stage1_trim_high_sources[1]);
    (void)gx8002_uart_stage1_raila(STAGE1_CLOCK_SCPU, 1u);    /* MODULE_SOURCE_24M_PLL */
    (void)gx8002_uart_stage1_raila(STAGE1_CLOCK_SRAM, 1u);    /* MODULE_SOURCE_24M_PLL */
    (void)gx8002_uart_stage1_raila(STAGE1_CLOCK_FLASH_SPI, 1u);    /* MODULE_SOURCE_24M_PLL */
    gx8002_uart_stage1_pmu_dispatch(STAGE1_CLOCK_OSC_REF, 0u);
    return 0;
}

/* ---------------------------------------------------------------------- */
/* 0x10001ddc: spl_board_clk_init for this board.                           */

/* GX_CLOCK_PLL, stock 0x20002478: enable, in 32768, fvco 98304000,
 * out 48000000, div_in 0, div_fb 2999, icpsel 2, bwsel_lpf 0,
 * vco_subband 3, div_out 0, itrim 0, vco_trim 4, 2nd3nd_lpf 0, lock_tiehi 0.
 * div_fb is adjusted at run time, so the object is writable. */
__attribute__((section(".stage1.data.pll")))
static uint32_t gx8002_uart_stage1_pll[14] = {
    1u, 32768u, 98304000u, 48000000u, 0u, 2999u, 2u, 0u, 3u, 0u, 0u, 4u, 0u, 0u,
};
#define STAGE1_PLL_DIV_FB 5

/* {CLOCK_SOURCE_PLL_DTO, 0}, {CLOCK_SOURCE_24M_PLL, 1}, stock 0x200024b0. */
__attribute__((section(".stage1.data.board_sources")))
static const uint32_t gx8002_uart_stage1_board_high_sources[2][2] = {
    {17u, 0u}, {0u, 1u},
};

void gx8002_uart_stage1_board_clk_init(void)
{
    if (gx8002_uart_stage1_clk_trim() != 0)
        return;
    gx8002_uart_stage1_pmu_set_bit0(1u);      /* spl_osc_set_all_trim_state(1) */

    for (;;) {
        if (gx8002_uart_stage1_pll[STAGE1_PLL_DIV_FB] > 3071u)
            continue;                         /* stock: spins here for good */
        if (gx8002_uart_stage1_uart_config(gx8002_uart_stage1_pll, 40u) == 0)
            break;                            /* spl_clk_set_pll_no_block */
        gx8002_uart_stage1_pll[STAGE1_PLL_DIV_FB] += 5u;
    }

    gx8002_uart_stage1_railb(STAGE1_CLOCK_SRAM, 2u);            /* set_div */
    gx8002_uart_stage1_pmu_bit_modify(gx8002_uart_stage1_board_high_sources[0]);
    gx8002_uart_stage1_pmu_bit_modify(gx8002_uart_stage1_board_high_sources[1]);
    gx8002_uart_stage1_railc(STAGE1_CLOCK_UART0_UART1, UINT32_C(0x1000000), 1u); /* set_dto */
    (void)gx8002_uart_stage1_raila(STAGE1_CLOCK_UART0_UART1, 1u);  /* 24M_PLL */
    (void)gx8002_uart_stage1_raila(STAGE1_CLOCK_I2C0_I2C1, 1u);
}

/* ---------------------------------------------------------------------- */
/* 0x10001378: spl_clk_init. The stock body expands the clk_priv.h inlines   */
/* with constant arguments; calling the out-of-line copies (railb = set_div, */
/* railc = set_dto, raila = set_module, bit_modify = set_source,            */
/* pmu_dispatch = set_gate_enable) gives the same register sequence.        */

/* clock_source_table[] of spl_clk.c, stock 0x200021d8: {source, select}. */
__attribute__((section(".stage1.data.clock_sources")))
static const uint32_t gx8002_uart_stage1_clock_sources[10][2] = {
    {18u, 0u}, /* CLOCK_SOURCE_1M_12M */
    {14u, 0u}, /* CLOCK_SOURCE_32K */
    {16u, 0u}, /* CLOCK_SOURCE_24M */
    {0u, 0u},  /* CLOCK_SOURCE_24M_PLL */
    {15u, 0u}, /* CLOCK_SOURCE_32K_PLL */
    {27u, 0u}, /* CLOCK_SOURCE_1M_INPUT */
    {28u, 0u}, /* CLOCK_SOURCE_1M */
    {29u, 0u}, /* CLOCK_SOURCE_OSC_PLL */
    {26u, 0u}, /* CLOCK_SOURCE_PIN_IN */
    {17u, 0u}, /* CLOCK_SOURCE_PLL_DTO */
};

void gx8002_uart_stage1_initialize_runtime(void)
{
    gx8002_uart_stage1_pmu_set_bit1(0u);      /* spl_osc_set_32k_trim_state(0) */
    gx8002_uart_stage1_pmu_set_bit0(0u);      /* spl_osc_set_all_trim_state(0) */

    for (uint32_t module = 0; module < STAGE1_CLOCK_MODULE_MAX; ++module) {
        gx8002_uart_stage1_railb(module, 0u);         /* spl_clk_set_div(i, 0) */
        gx8002_uart_stage1_railc(module, 0u, 0u);     /* spl_clk_set_dto(i, 0, 0) */
    }

    /* _clk_init */
    for (uint32_t i = 0; i < 10u; ++i)
        gx8002_uart_stage1_pmu_bit_modify(gx8002_uart_stage1_clock_sources[i]);
    for (uint32_t module = 0; module < STAGE1_CLOCK_MODULE_MAX; ++module)
        (void)gx8002_uart_stage1_raila(module, 0u);   /* MODULE_SOURCE_1M_12M */

    gx8002_uart_stage1_board_clk_init();

    /* _gate_init */
    STAGE1_REG32(0xa0010100) = 1;             /* PMU_CFG_SRAM_GATE_ADDR */
    STAGE1_REG32(0xa0010104) &= ~UINT32_C(1); /* PMU_CFG_CLK_GATE */
    STAGE1_REG32(0xa0005084) &= ~UINT32_C(1); /* HW_I2C + 0x84: 32k xtal off */
    STAGE1_REG32(0xa00050c8) = 0;             /* HW_I2C + 0xc8 */
    for (uint32_t module = 0; module < STAGE1_CLOCK_MODULE_MAX; ++module) {
        const uint32_t enable = module == STAGE1_CLOCK_PMU ||
            module == STAGE1_CLOCK_HW_I2C || module == STAGE1_CLOCK_SRAM ||
            module == STAGE1_CLOCK_SCPU || module == STAGE1_CLOCK_UART0;
        gx8002_uart_stage1_pmu_dispatch(module, enable);  /* set_gate_enable */
    }
}
