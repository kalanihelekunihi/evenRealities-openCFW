/* Board HAL storage (S1 storage-definition pass, 2.2.6.10).
 *
 * Stock owners: the product board UART channel layer (driver\hal hal_uart,
 * four 28-byte channel records with their pin tables, UART configurations,
 * RX queue descriptors and SSRAM receive buffers), the product hal_gpio.c
 * bank IRQ table, and the product BSP (am_bsp.c shape: ITM print flag and
 * the clock-manager board info). .data values are from the decoded
 * 0x20000000 init stream (scatter record 0x75d3f4); ROM bytes are from
 * ota_s200_firmware_ota.bin. */
#include <stdint.h>

/* ---- board UART channel layer ------------------------------------------- */

typedef struct {
    uint32_t rx_pin; /* +0x0 */
    uint32_t tx_pin; /* +0x4 */
    uint32_t rx_cfg; /* +0x8 am_hal_gpio_pincfg_t */
    uint32_t tx_cfg; /* +0xc */
} g2_uart_pins_data_t;

typedef struct {
    uint32_t w0;     /* +0x0 */
    uint8_t *w1;     /* +0x4 */
    uint32_t count;  /* +0x8 */
    uint8_t *buffer; /* +0xc */
} g2_uart_queue_data_t;

typedef struct {
    uint32_t module;                       /* +0x00 */
    void *handle;                          /* +0x04 */
    const g2_uart_pins_data_t *pins;       /* +0x08 */
    const uint32_t *config;                /* +0x0c am_hal_uart_config_t */
    g2_uart_queue_data_t *rx;              /* +0x10 */
    void (*callback)(uint8_t *, uint32_t); /* +0x14 */
    uint8_t active;                        /* +0x18 */
    uint8_t tx_done;                       /* +0x19 */
    uint8_t pad[2];
} g2_uart_channel_data_t;
_Static_assert(sizeof(g2_uart_channel_data_t) == 28u, "channel record is 28 bytes");

/* ROM 0x786060 / 0x786070 / 0x786080: {RX pin, TX pin, RX cfg, TX cfg}. */
static const g2_uart_pins_data_t g2_uart1_pins = {12u, 14u, 5u, 5u};
static const g2_uart_pins_data_t g2_uart2_pins = {42u, 44u, 4u, 4u};
static const g2_uart_pins_data_t g2_uart3_pins = {73u, 69u, 5u, 5u};

/* RAM 0x20000ccc / 0x20000cdc / 0x20000cec (.data): am_hal_uart_config_t
 * {baud, 03 02 00 00, 00 00 02 02, 0}: 921600, 1000000 and 230400 baud. */
static uint32_t g2_uart1_config[4] = {921600u, 0x00000203u, 0x02020000u, 0u};
static uint32_t g2_uart2_config[4] = {1000000u, 0x00000203u, 0x02020000u, 0u};
static uint32_t g2_uart3_config[4] = {230400u, 0x00000203u, 0x02020000u, 0u};

/* SSRAM 0x200b9c20, 0x200ba020, 0x200ba420, 0x200ba820: 1 KiB receive
 * buffers. Stock places them in the initialised SSRAM image (scatter record
 * 0x75d404 -> 0x20080000), where their bytes are all zero. */
__attribute__((aligned(4))) static uint8_t g2_uart1_rx_buffer[0x400];
__attribute__((aligned(4))) static uint8_t g2_uart2_rx_buffer[0x400];
__attribute__((aligned(4))) static uint8_t g2_uart3_rx_staging[0x400];
__attribute__((aligned(4))) static uint8_t g2_uart3_rx_buffer[0x400];

/* RAM 0x20000cfc / 0x20000d0c / 0x20000d1c (.data): RX queue descriptors. */
static g2_uart_queue_data_t g2_uart1_rx_queue = {0u, 0, 0u, g2_uart1_rx_buffer};
static g2_uart_queue_data_t g2_uart2_rx_queue = {0u, 0, 0u, g2_uart2_rx_buffer};
static g2_uart_queue_data_t g2_uart3_rx_queue = {0x400u, g2_uart3_rx_staging, 0u, g2_uart3_rx_buffer};

/* RAM 0x20000d2c..0x20000d9b (.data): channels 0..3 (channel 0 unused). */
g2_uart_channel_data_t g2_uart_channels[4] = {
    {0u, 0, 0, 0, 0, 0, 0u, 0u, {0u, 0u}},
    {1u, 0, &g2_uart1_pins, g2_uart1_config, &g2_uart1_rx_queue, 0, 0u, 0u, {0u, 0u}},
    {2u, 0, &g2_uart2_pins, g2_uart2_config, &g2_uart2_rx_queue, 0, 0u, 0u, {0u, 0u}},
    {3u, 0, &g2_uart3_pins, g2_uart3_config, &g2_uart3_rx_queue, 0, 0u, 0u, {0u, 0u}},
};

/* ROM 0x78f104 = 3 (disabled pad), UART2 RX pin restore word. */
const uint32_t g2_uart2_rx_pin_config = 0x00000003u;

/* ---- product hal_gpio.c ------------------------------------------------- */

/* ROM 0x78d6cc: GPIO0 bank IRQ numbers, indexed by pin >> 5. */
const int16_t g2_gpio_bank_irq_78d6cc[4] = {56, 57, 58, 59};

/* ---- product BSP -------------------------------------------------------- */

volatile uint8_t g2_bsp_itm_print_enabled; /* RAM 0x20074f4e */

typedef struct {
    uint8_t xtal_hs_mode; /* +0x00 */
    uint8_t pad[3];
    uint32_t xtal_hs_hz;  /* +0x04 */
    uint32_t reserved_08; /* +0x08 */
    uint32_t xtal_ls_hz;  /* +0x0c */
    uint32_t ext_ref_hz;  /* +0x10 */
} g2_clkmgr_board_info_data_t;
_Static_assert(sizeof(g2_clkmgr_board_info_data_t) == 20u, "board info");

/* ROM 0x77d8f8: XTAL-HS mode 0 / 0 Hz, XTAL-LS 32768 Hz, ext ref 12 MHz. */
const g2_clkmgr_board_info_data_t g2_clkmgr_board_info_default = {
    0u, {0u, 0u, 0u}, 0u, 0u, 32768u, 12000000u,
};
