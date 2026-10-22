/* Board configuration, stock D:\01_workspace\s200_ap510b_iar_git\product\s200\app\config\board_config.c
 * (log tag "BSP"). Native 0x509132..0x50938d and 0x5093ac..0x509447; literal
 * pool 0x509448..0x5094bf ("BSP" at 0x509468 sits in that pool). The board
 * info selector 0x50938e between them is ble/ble-hci/display_ble_hci_radio_mode.c.
 *
 * Hardware-version detection reads a resistor divider on GPIO 16 with ADC
 * slot 3 (single-ended channel 3): three averaged samples, then
 * mV = sample * 1190 >> 12 is binned into a hardware version code.
 * Board info (RAM 0x20074368, 4 bytes): +0 charger/PMIC family (1 nPM1300,
 * 2 BQ25180 + BQ27427), +1 hw_version, +2 u16 measured mV.
 *
 * Uses double precision (float to double for printf varargs): profile
 * g2-apollo-main-20. */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "g2_hal_i2c.h"
#include "g2_npm1300.h"
#include "g2_bq25180.h"
#include "g2_bq27427.h"

typedef struct {
    uint8_t board_type;  /* +0 1 = nPM1300, 2 = BQ25180/BQ27427 */
    uint8_t hw_version;  /* +1 3/4/5/6, 0xff unknown */
    uint16_t hw_adc_mv;  /* +2 */
} g2_board_info_t;
_Static_assert(sizeof(g2_board_info_t) == 4u, "board info is 4 bytes (0x20074368..0x2007436b)");

/* am_hal_adc_* configuration records in the stock (one-byte enum) layout. */
typedef struct {
    uint8_t clock;          /* +0 eClock */
    uint8_t repeat_trigger; /* +1 eRepeatTrigger */
    uint8_t polarity;       /* +2 ePolarity */
    uint8_t trigger;        /* +3 eTrigger */
    uint8_t clock_mode;     /* +4 eClockMode */
    uint8_t power_mode;     /* +5 ePowerMode */
    uint8_t repeat;         /* +6 eRepeat */
} g2_adc_config_t;
_Static_assert(sizeof(g2_adc_config_t) == 7u, "am_hal_adc_config_t");

typedef struct {
    uint8_t meas_to_avg;    /* +0 eMeasToAvg */
    uint32_t track_cycles;  /* +4 ui32TrkCyc */
    uint8_t precision;      /* +8 ePrecisionMode */
    uint8_t channel;        /* +9 eChannel */
    uint8_t window_compare; /* +10 bWindowCompare */
    uint8_t enabled;        /* +11 bEnabled */
} g2_adc_slot_config_t;
_Static_assert(sizeof(g2_adc_slot_config_t) == 12u, "am_hal_adc_slot_config_t");

typedef struct {
    uint8_t irtt_enable;    /* +0 bIrttEnable */
    uint8_t clk_div;        /* +1 eClkDiv */
    uint32_t count_max;     /* +4 ui32IrttCountMax */
} g2_adc_irtt_config_t;
_Static_assert(sizeof(g2_adc_irtt_config_t) == 8u, "am_hal_adc_irtt_config_t");

typedef struct {
    uint32_t sample; /* +0 ui32Sample */
    uint32_t slot;   /* +4 ui32Slot */
} g2_adc_sample_t;

#define HWID_ADC_PIN 16u
#define HWID_ADC_SLOT 3u
#define HWID_SAMPLES 3u
#define ADC_REQ_CORRECTION_TRIMS_GET 3u
#define ADC_POWER_WAKE 0u
#define ADC_POWER_DEEPSLEEP 2u
#define ADC_FIFO_REG (*(volatile uint32_t *)0x40038038u) /* ADC->FIFO, COUNT in bits 27:20 */
#define BOARD_GPIO_TABLE_ROWS 0x61u

extern g2_board_info_t audio_ble_hci_radio_mode_cells_20074368; /* RAM 0x20074368 (declared 3 bytes in
                                                                  audio/master-dispatch/ble_pointer_cells.c) */
extern const uint32_t g2_board_hwid_pin_adc_cfg_78ee8c; /* ROM 0x78ee8c am_hal_gpio_pincfg_t, ADC function */
extern const uint32_t g2_board_hwid_pin_off_cfg_78ee90; /* ROM 0x78ee90 am_hal_gpio_pincfg_t, released */
extern const uint8_t g2_board_gpio_table_686db8[];      /* ROM 0x686db8, 0x61 rows of 12 bytes */

extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);
extern int32_t board_gpio_table_init_53a454(const void *table, uint32_t rows);
extern void audio_ble_hci_boot_log_4733ee(const char *format, ...); /* debug printf */
extern uint32_t am_hal_adc_initialize_55d94c(uint32_t module, void **handle);
extern uint32_t am_hal_adc_deinitialize_55daae(void *handle);
extern uint32_t am_hal_adc_configure_55dae4(void *handle, const g2_adc_config_t *config);
extern uint32_t am_hal_adc_configure_slot_55db72(void *handle, uint32_t slot, const g2_adc_slot_config_t *config);
extern uint32_t am_hal_adc_configure_irtt_55dbf0(void *handle, const g2_adc_irtt_config_t *config);
extern uint32_t am_hal_adc_irtt_enable_55dc26(void *handle);
extern uint32_t am_hal_adc_irtt_disable_55dc5e(void *handle);
extern uint32_t am_hal_adc_control_55dc88(void *handle, uint32_t request, void *args);
extern uint32_t am_hal_adc_enable_55dddc(void *handle);
extern uint32_t am_hal_adc_disable_55de1c(void *handle);
extern uint32_t am_hal_adc_samples_read_55deec(void *handle, bool full_sample, uint32_t *in_buffer,
                                               uint32_t *in_out_count, g2_adc_sample_t *out);
extern uint32_t am_hal_adc_sw_trigger_55e070(void *handle);
extern uint32_t am_hal_adc_power_control_55e09c(void *handle, uint32_t state, bool retain);
extern uint32_t uart_channels_init_55e388(void);
extern uint32_t hal_uart_power_on_55e5bc(uint8_t uart);
extern uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t mode);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

void board_config_empty_hook_509132(void);
void board_hw_version_detect_509134(void);
int32_t board_init_5093ac(void);
int32_t board_power_init_5093d4(void);

static const char module_tag[] = "BSP"; /* ROM 0x509468 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\app\\config\\board_config.c"; /* ROM 0x6f1bdc */
static const char fn_power_init[] = "power_init"; /* ROM 0x78a538 */
static const char hw_version_fmt[] = "hw_version: %d, hw_adc_val: %d"; /* ROM 0x75e4b0 */
static const char hw_version_short[] = "[BSP]hw_version: %d, hw_adc_val: %d"; /* ROM 0x752568 */
static const char adc_init_failed[] = "Error - reservation of the ADC instance failed.\n"; /* ROM 0x72729c */
static const char adc_trims[] = "ADC correction offset = %.6f, gain = %.6f\n"; /* ROM 0x73c6ec */
static const char adc_power_failed[] = "Error - ADC power on failed.\n"; /* ROM 0x75e470 */
static const char adc_config_failed[] = "Error - configuring ADC failed.\n"; /* ROM 0x752544 */
static const char adc_slot_failed[] = "Error - configuring ADC Slot failed.\n"; /* ROM 0x747ea4 */
static const char adc_enable_failed[] = "Error - enabling ADC failed.\n"; /* ROM 0x75e490 */
static const char adc_result[] = "HwConfig ADC sample read=%d, measured voltage=%.5f mV\n"; /* ROM 0x71c578 */

/* Empty board hook called before the hardware-version probe. */
void board_config_empty_hook_509132(void)
{
}

void board_hw_version_detect_509134(void)
{
    void *adc;
    uint32_t count = 1u;
    g2_adc_sample_t sample;
    float trims[4];

    (void)am_hal_gpio_pinconfig_480f0c(HWID_ADC_PIN, g2_board_hwid_pin_adc_cfg_78ee8c);
    if (am_hal_adc_initialize_55d94c(0u, &adc) != 0u)
        audio_ble_hci_boot_log_4733ee(adc_init_failed);

    trims[0] = 0.0f;
    trims[1] = 0.0f;
    trims[2] = 0.0f;
    trims[3] = -123.456f; /* HAL validity marker */
    (void)am_hal_adc_control_55dc88(adc, ADC_REQ_CORRECTION_TRIMS_GET, trims);
    audio_ble_hci_boot_log_4733ee(adc_trims, (double)trims[0], (double)trims[1]);

    if (am_hal_adc_power_control_55e09c(adc, ADC_POWER_WAKE, false) != 0u)
        audio_ble_hci_boot_log_4733ee(adc_power_failed);

    /* Stock copies this record from ROM 0x78d104 (0x0401, 30). */
    g2_adc_irtt_config_t irtt = { .irtt_enable = 1u, .clk_div = 4u, .count_max = 30u };
    (void)am_hal_adc_configure_irtt_55dbf0(adc, &irtt);

    g2_adc_config_t config;
    config.clock = 2u;
    config.polarity = 0u;
    config.trigger = 7u;
    config.clock_mode = 1u;
    config.power_mode = 0u;
    config.repeat = 1u;
    config.repeat_trigger = 1u;
    if (am_hal_adc_configure_55dae4(adc, &config) != 0u)
        audio_ble_hci_boot_log_4733ee(adc_config_failed);

    g2_adc_slot_config_t slot;
    slot.meas_to_avg = 7u;
    slot.track_cycles = 32u;
    slot.precision = 0u;
    slot.channel = 3u;
    slot.window_compare = 0u;
    slot.enabled = 1u;
    if (am_hal_adc_configure_slot_55db72(adc, HWID_ADC_SLOT, &slot) != 0u)
        audio_ble_hci_boot_log_4733ee(adc_slot_failed);

    if (am_hal_adc_enable_55dddc(adc) != 0u)
        audio_ble_hci_boot_log_4733ee(adc_enable_failed);
    (void)am_hal_adc_irtt_enable_55dc26(adc);
    (void)am_hal_adc_sw_trigger_55e070(adc);

    uint8_t matched = 0u;
    while (matched < HWID_SAMPLES) {
        while (((ADC_FIFO_REG >> 20) & 0xffu) == 0u) {
        }
        count = 1u;
        (void)am_hal_adc_samples_read_55deec(adc, false, NULL, &count, &sample);
        if (sample.slot == HWID_ADC_SLOT)
            matched++;
        if (matched < HWID_SAMPLES)
            continue;

        (void)am_hal_adc_irtt_disable_55dc5e(adc);
        (void)am_hal_adc_disable_55de1c(adc);
        float mv = (float)((sample.sample * 1190u) >> 12);
        g2_board_info_t *info = &audio_ble_hci_radio_mode_cells_20074368;
        /* IAR folds each "mv > N" into ">= nextafterf(N)" (pool 0x509448..). */
        if (mv > 950.0f && mv < 1050.0f) {
            info->board_type = 1u;
            info->hw_version = 6u;
        } else if (mv > 550.0f && mv < 650.0f) {
            info->board_type = 1u;
            info->hw_version = 3u;
        } else if (mv > 300.0f && mv < 400.0f) {
            info->board_type = 1u;
            info->hw_version = 4u;
        } else if (mv > 100.0f && mv < 250.0f) {
            info->board_type = 1u;
            info->hw_version = 5u;
        } else {
            info->board_type = 1u;
            info->hw_version = 0xffu;
        }
        info->hw_adc_mv = (uint16_t)(int32_t)mv;
        audio_ble_hci_boot_log_4733ee(adc_result, sample.sample, (double)mv);
    }

    (void)am_hal_adc_power_control_55e09c(adc, ADC_POWER_DEEPSLEEP, false);
    (void)am_hal_adc_deinitialize_55daae(adc);
    (void)am_hal_gpio_pinconfig_480f0c(HWID_ADC_PIN, g2_board_hwid_pin_off_cfg_78ee90);
}

int32_t board_init_5093ac(void)
{
    (void)board_gpio_table_init_53a454(g2_board_gpio_table_686db8, BOARD_GPIO_TABLE_ROWS);
    board_config_empty_hook_509132();
    board_hw_version_detect_509134();
    (void)uart_channels_init_55e388();
    (void)HAL_I2CInit();
    (void)hal_uart_power_on_55e5bc(1u);
    return 0;
}

/* power_init: bring up the charger / fuel-gauge family the board reports. */
int32_t board_power_init_5093d4(void)
{
    const g2_board_info_t *info = (const g2_board_info_t *)(const void *)audio_ble_hci_radio_mode_state_50938e(3u);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module_tag, source_file, fn_power_init, 0x18eu, hw_version_fmt,
                           (uint32_t)info->hw_version, (uint32_t)info->hw_adc_mv);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x08800000u, hw_version_short, hw_version_short,
                                  (uint32_t)info->hw_version, (uint32_t)info->hw_adc_mv);
    if (info->board_type == 1u) {
        npmx_main_driver_init_512644();
    } else if (info->board_type == 2u) {
        (void)DRV_Bq25180HwInit();
        (void)DRV_Bq27427HwInit();
    }
    return 0;
}
