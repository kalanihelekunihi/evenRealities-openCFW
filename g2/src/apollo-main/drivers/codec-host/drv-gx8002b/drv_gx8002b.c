/* GX8002B codec host driver, stock D:\01_workspace\s200_ap510b_iar_git\driver\codec\drv_gx8002b.c.
 * Native 0x57a46c..0x57a86f; literal pool 0x57a870..0x57a8ff.
 *
 * Power: three codec control lines through the codec GPIO selector 0x509024
 * (line 6 = shared enable mask -> GPIO134, line 7 = GPIO143, line 8 = GPIO146),
 * raised in order with 5 ms and 20 ms osDelay gaps and dropped together.
 * Audio: Apollo510 I2S0 (IRQ 44, priority 4) as RX-only slave; the GX8002B
 * drives the bit/frame clocks. The AmbiqSuite I2S config at RAM 0x20000000,
 * its data format at 0x20000728 and the ping/pong DMA descriptor at
 * 0x20000740 are initialised data owned by codec-i2s-init.
 * Ambiq HAL bodies are reconstructed elsewhere under the names reused here. */
#include <stdint.h>
#include <stdbool.h>
#include "g2_drv_gx8002b.h"

/* am_hal_i2s_config_t in the stock layout (IAR one-byte enums). Documented
 * here; the 40-byte image is defined as g2_codec_i2s_config_base. */
typedef struct {
    uint8_t mode;              /* +0x00 eMode: 0 = AM_HAL_I2S_IO_MODE_SLAVE */
    uint8_t xfer;              /* +0x01 eXfer: 0 = AM_HAL_I2S_XFER_RX */
    uint8_t pad_02[2];
    uint32_t clock;            /* +0x04 eClock 0x20b (unused: slave, no ASRC) */
    uint32_t div3;             /* +0x08 eDiv3 = 0 */
    uint32_t pad_0c;
    double nco_div;            /* +0x10 f64NcoDiv = 0 */
    uint32_t asrc;             /* +0x18 eASRC = 0 */
    const void *data_format;   /* +0x1c eData = 0x20000728 */
    const void *io_signal;     /* +0x20 eIO = 0x20073ff0 */
    const void *transfer;      /* +0x24 eTransfer, set at runtime */
} g2_i2s_config_t;
_Static_assert(sizeof(g2_i2s_config_t) == 40, "stock I2S config is 40 bytes");

/* am_hal_i2s_data_format_t at 0x20000728:
 * single phase, 2 channels, 32-bit slots, data delay 1, 16-bit samples. */
typedef struct {
    uint8_t phase;             /* +0x00 0 = single phase */
    uint32_t channels_phase1;  /* +0x04 2 */
    uint32_t channels_phase2;  /* +0x08 0 */
    uint8_t channel_len_phase1;/* +0x0c 5 = 32-bit */
    uint8_t channel_len_phase2;/* +0x0d 0 */
    uint32_t data_delay;       /* +0x10 1 */
    uint8_t sample_len_phase1; /* +0x14 2 = 16-bit */
    uint8_t sample_len_phase2; /* +0x15 0 */
    uint8_t justify;           /* +0x16 0 */
} g2_i2s_data_format_t;
_Static_assert(sizeof(g2_i2s_data_format_t) == 24, "stock I2S data format is 24 bytes");

/* am_hal_i2s_transfer_t at 0x20000740: RX ping 0x20364e18, pong 0x20365a98,
 * 800 32-bit words (3,200 bytes) per block; TX unused. */
typedef struct {
    uint32_t rx_target;         /* +0x00 */
    uint32_t rx_target_reverse; /* +0x04 */
    uint32_t rx_total_count;    /* +0x08 words */
    uint32_t tx_target;         /* +0x0c */
    uint32_t tx_target_reverse; /* +0x10 */
    uint32_t tx_total_count;    /* +0x14 */
} g2_i2s_transfer_t;
_Static_assert(sizeof(g2_i2s_transfer_t) == 24, "stock I2S transfer is 24 bytes");

enum { SYSCTRL_WAKE = 0u, SYSCTRL_NORMALSLEEP = 1u };
enum { I2S_XFER_RX = 0u };
#define I2S_INT_RXDMACPL 0x10u
#define I2S_IRQ_PRIORITY 4u

/* Codec GPIO selector lines (0x509024). */
enum { CODEC_LINE_SHARED_EN = 6u, CODEC_LINE_GPIO143 = 7u, CODEC_LINE_GPIO146 = 8u };

extern uint8_t g2_codec_power_state;           /* RAM 0x20074fb6 */
extern uint8_t g2_codec_i2s_initialized;       /* RAM 0x20074fb7 */
extern void *g2_codec_i2s_handle;              /* RAM 0x2007450c */
extern uint8_t g2_codec_i2s_config_base[];     /* RAM 0x20000000 g2_i2s_config_t */
extern uint8_t g2_codec_i2s_dma_descriptor[];  /* RAM 0x20000740 g2_i2s_transfer_t */
extern const int16_t g2_codec_i2s_irq_number;  /* ROM 0x78f558 = 44 (I2S0_IRQn) */

/* Existing g2/src names for the stock bodies (upstream name in comment). */
extern uint32_t g2_codec_gpio_write(uint32_t line, uint32_t value);   /* 0x509024 */
extern void g2_codec_clock_enable(uint32_t group, uint32_t mode);     /* 0x4c3074 am_bsp_i2s_pins_enable */
extern void audio_clock_stop(uint32_t group, uint32_t mode);          /* 0x4c3138 am_bsp_i2s_pins_disable */
extern uint32_t g2_codec_i2s_acquire(uint32_t instance, void **handle_cell); /* 0x59005e am_hal_i2s_initialize */
extern uint32_t audio_i2s_uninitialize_selected(uint32_t *handle);    /* 0x5900ce am_hal_i2s_deinitialize */
extern uint32_t audio_i2s_power_selected(uint32_t *handle, uint32_t state, uint32_t retain); /* 0x590648 am_hal_i2s_power_control */
extern uint32_t g2_codec_i2s_configure(void *handle, const void *config); /* 0x590104 am_hal_i2s_configure */
extern uint32_t g2_codec_i2s_prepare(void *handle);                   /* 0x590b92 am_hal_i2s_enable */
extern uint32_t audio_i2s_dma_stop_selected(uint32_t *handle);        /* 0x590c62 am_hal_i2s_disable */
extern uint32_t g2_codec_i2s_dma_configure(void *handle, const void *config,
                                           const void *descriptor);   /* 0x590a24 am_hal_i2s_dma_configure */
extern int32_t g2_codec_i2s_start(void *handle, const void *config);  /* 0x5904ce am_hal_i2s_dma_transfer_start */
extern uint32_t g2_codec_global_irq_enable(void);                     /* 0x473934 am_hal_interrupt_master_enable */
extern void audio_ble_privacy_cache_maintenance(const uint32_t *range, uint8_t clean); /* 0x475014 am_hal_cachectrl_dcache_invalidate */
extern uint32_t am_hal_i2s_interrupt_status_get_590848(void *handle, uint32_t *status, bool enabled_only);
extern uint32_t am_hal_i2s_interrupt_clear_590818(void *handle, uint32_t status);
extern uint32_t am_hal_i2s_interrupt_service_5908a0(void *handle, uint32_t status, void *config);
extern uint32_t am_hal_i2s_dma_get_buffer_590b6c(void *handle, uint32_t xfer);
extern void aud_send_codec_dma_message(void);  /* 0x53c6b2, audio thread message type 2 */
extern void aud_send_message_type5(void);      /* 0x53cc8c, audio thread message type 5 */
extern int32_t osDelay(uint32_t ticks);        /* 0x449376 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);   /* 0x43ce9e */

static const char module_tag[] = "drv.audio.codec"; /* ROM 0x785c70 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\codec\\drv_gx8002b.c"; /* ROM 0x70af24 */
static const char power_on_fn[] = "DRV_Gx8002_PowerOn";     /* ROM 0x77efb4 */
static const char power_off_fn[] = "DRV_Gx8002_PowerOff";   /* ROM 0x77efdc */
static const char i2s_init_fn[] = "DRV_Gx8002_I2SInit";     /* ROM 0x77f004 */
static const char i2s_deinit_fn[] = "DRV_Gx8002_I2SDeinit"; /* ROM 0x776c34 */
static const char reboot_fn[] = "DRV_Gx8002_Reboot";        /* ROM 0x77f040 */
static const char already_on[] = "gx8002 already power on.";  /* ROM 0x76b0a0 */
static const char already_on_short[] = "[drv.audio.codec]gx8002 already power on."; /* ROM 0x73e2f0 */
static const char powered_on[] = "gx8002 power on.";          /* ROM 0x77efc8 */
static const char powered_on_short[] = "[drv.audio.codec]gx8002 power on."; /* ROM 0x753aa4 */
static const char already_off[] = "gx8002 already power off."; /* ROM 0x76b0bc */
static const char already_off_short[] = "[drv.audio.codec]gx8002 already power off."; /* ROM 0x73e31c */
static const char powered_off[] = "gx8002 power off.";        /* ROM 0x77eff0 */
static const char powered_off_short[] = "[drv.audio.codec]gx8002 power off."; /* ROM 0x753ac8 */
static const char i2s_already_init[] = "gx8002b i2s already init."; /* ROM 0x76b0d8 */
static const char i2s_already_init_short[] = "[drv.audio.codec]gx8002b i2s already init."; /* ROM 0x73e348 */
static const char i2s_init_done[] = "gx8002b i2s init.";      /* ROM 0x77f018 */
static const char i2s_init_done_short[] = "[drv.audio.codec]gx8002b i2s init."; /* ROM 0x753aec */
static const char i2s_already_deinit[] = "gx8002b i2s already deinit."; /* ROM 0x76b0f4 */
static const char i2s_already_deinit_short[] = "[drv.audio.codec]gx8002b i2s already deinit."; /* ROM 0x7335b4 */
static const char i2s_deinit_done[] = "gx8002b i2s deinit.";  /* ROM 0x77f02c */
static const char i2s_deinit_done_short[] = "[drv.audio.codec]gx8002b i2s deinit."; /* ROM 0x7495ec */
static const char reboot_done[] = "codec reboot done";        /* ROM 0x77f054 */
static const char reboot_done_short[] = "[drv.audio.codec]codec reboot done"; /* ROM 0x753b10 */

/* Stock logging macro: extended record when flag bit 1 is set, compressed
 * record when flag bit 0 or bit 2 is set. */
#define GX_LOG(level, mask, line, fn, msg, msg_short)                              \
    do {                                                                           \
        if (audio_log_flags() & 2u)                                                \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg)); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                  \
            (void)compress_log_output((mask), (msg_short), (msg_short));           \
    } while (0)

/* CMSIS-Core inline copies emitted out of line by the stock build. */
__attribute__((noinline)) static void __NVIC_EnableIRQ(int16_t irq)
{
    if (irq >= 0)
        ((volatile uint32_t *)0xe000e100u)[(uint32_t)irq >> 5] = 1u << ((uint32_t)irq & 31u);
}

__attribute__((noinline)) static void __NVIC_DisableIRQ(int16_t irq)
{
    if (irq >= 0) {
        ((volatile uint32_t *)0xe000e180u)[(uint32_t)irq >> 5] = 1u << ((uint32_t)irq & 31u);
        __asm volatile("dsb sy\n\tisb sy" ::: "memory");
    }
}

__attribute__((noinline)) static void __NVIC_SetPriority(int16_t irq, uint32_t priority)
{
    if (irq >= 0)
        ((volatile uint8_t *)0xe000e400u)[irq] = (uint8_t)(priority << 4);
    else
        ((volatile uint8_t *)0xe000ed18u)[((uint32_t)irq & 15u) - 4u] = (uint8_t)(priority << 4);
}

/* I2S0 vector (IRQ 44). The DMA-complete notification uses the status
 * captured before service, regardless of the service result. */
void gx8002_i2s_isr(void)
{
    uint32_t status;
    (void)am_hal_i2s_interrupt_status_get_590848(g2_codec_i2s_handle, &status, true);
    (void)am_hal_i2s_interrupt_clear_590818(g2_codec_i2s_handle, status);
    (void)am_hal_i2s_interrupt_service_5908a0(g2_codec_i2s_handle, status, g2_codec_i2s_config_base);
    if (status & I2S_INT_RXDMACPL)
        aud_send_codec_dma_message();
}

void DRV_Gx8002_PowerOn(void)
{
    if (g2_codec_power_state != 0u) {
        GX_LOG(4u, 0x10000000u, 87u, power_on_fn, already_on, already_on_short);
        return;
    }
    g2_codec_power_state = 1u;
    (void)g2_codec_gpio_write(CODEC_LINE_SHARED_EN, 1u);
    (void)osDelay(5u);
    (void)g2_codec_gpio_write(CODEC_LINE_GPIO143, 1u);
    (void)osDelay(20u);
    (void)g2_codec_gpio_write(CODEC_LINE_GPIO146, 1u);
    GX_LOG(4u, 0x10000000u, 97u, power_on_fn, powered_on, powered_on_short);
}

void DRV_Gx8002_PowerOff(void)
{
    if (g2_codec_power_state == 0u) {
        GX_LOG(4u, 0x10000000u, 103u, power_off_fn, already_off, already_off_short);
        return;
    }
    g2_codec_power_state = 0u;
    (void)g2_codec_gpio_write(CODEC_LINE_SHARED_EN, 0u);
    (void)g2_codec_gpio_write(CODEC_LINE_GPIO143, 0u);
    (void)g2_codec_gpio_write(CODEC_LINE_GPIO146, 0u);
    GX_LOG(4u, 0x10000000u, 110u, power_off_fn, powered_off, powered_off_short);
}

uint8_t gx8002_power_state_get(void)
{
    return g2_codec_power_state;
}

void DRV_Gx8002_I2SInit(void)
{
    if (g2_codec_i2s_initialized != 0u) {
        GX_LOG(4u, 0x10000000u, 121u, i2s_init_fn, i2s_already_init, i2s_already_init_short);
        return;
    }
    g2_codec_i2s_initialized = 1u;
    g2_codec_clock_enable(0u, 0u);
    (void)g2_codec_i2s_acquire(0u, &g2_codec_i2s_handle);
    (void)audio_i2s_power_selected(g2_codec_i2s_handle, SYSCTRL_WAKE, false);
    (void)g2_codec_i2s_configure(g2_codec_i2s_handle, g2_codec_i2s_config_base);
    (void)g2_codec_i2s_prepare(g2_codec_i2s_handle);
    (void)g2_codec_i2s_dma_configure(g2_codec_i2s_handle, g2_codec_i2s_config_base,
                                     g2_codec_i2s_dma_descriptor);
    __NVIC_SetPriority(g2_codec_i2s_irq_number, I2S_IRQ_PRIORITY);
    __NVIC_EnableIRQ(g2_codec_i2s_irq_number);
    (void)g2_codec_global_irq_enable();
    (void)g2_codec_i2s_start(g2_codec_i2s_handle, g2_codec_i2s_config_base);
    GX_LOG(4u, 0x10000000u, 137u, i2s_init_fn, i2s_init_done, i2s_init_done_short);
}

void DRV_Gx8002_I2SDeinit(void)
{
    if (g2_codec_i2s_initialized == 0u) {
        GX_LOG(4u, 0x10000000u, 143u, i2s_deinit_fn, i2s_already_deinit, i2s_already_deinit_short);
        return;
    }
    g2_codec_i2s_initialized = 0u;
    __NVIC_DisableIRQ(g2_codec_i2s_irq_number);
    audio_clock_stop(0u, 0u);
    (void)audio_i2s_power_selected(g2_codec_i2s_handle, SYSCTRL_NORMALSLEEP, false);
    (void)audio_i2s_dma_stop_selected(g2_codec_i2s_handle);
    (void)audio_i2s_uninitialize_selected(g2_codec_i2s_handle);
    GX_LOG(4u, 0x10000000u, 153u, i2s_deinit_fn, i2s_deinit_done, i2s_deinit_done_short);
}

/* The range starts from the ROM template 0x78d474 {0, 3200}. Stock leaves
 * the buffer address in R0 on return; callers do not use it. */
void gx8002_i2s_rx_buffer_get(uint8_t **buffer, uint32_t *length)
{
    uint32_t range[2] = { 0u, G2_GX8002_I2S_BLOCK_BYTES }; /* am_hal_cachectrl_range_t */
    range[0] = am_hal_i2s_dma_get_buffer_590b6c(g2_codec_i2s_handle, I2S_XFER_RX);
    audio_ble_privacy_cache_maintenance(range, 0u);
    *buffer = (uint8_t *)(uintptr_t)range[0];
    *length = range[1];
}

void gx8002_audio_thread_notify(void)
{
    aud_send_message_type5();
}

void DRV_Gx8002_Reboot(uint8_t skip_boot_wait)
{
    DRV_Gx8002_PowerOff();
    (void)osDelay(100u);
    DRV_Gx8002_PowerOn();
    if (skip_boot_wait == 0u)
        (void)osDelay(1500u);
    GX_LOG(3u, 0x0c000000u, 185u, reboot_fn, reboot_done, reboot_done_short);
}
