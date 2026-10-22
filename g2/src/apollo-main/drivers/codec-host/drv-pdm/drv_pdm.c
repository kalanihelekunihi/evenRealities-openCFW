/* PDM microphone driver, stock D:\01_workspace\s200_ap510b_iar_git\driver\pdm\drv_pdm.c.
 * Native 0x57b704..0x57ba1d; literal pool 0x57ba20..0x57ba87.
 *
 * Apollo510 PDM0 (IRQ 48, priority 4), clock/data pads GPIO50/51, GPIO143
 * driven high before the block is opened (and left high by deinit).
 * DMA ping 0x20377bc0 / pong 0x20377e40, 640 bytes (160 x 32-bit words)
 * per block. Each completed block is cut to 16-bit PCM (bits 23..8 of
 * every word) in a 320-byte scratch buffer and fed to the voice-energy
 * window (service_algo_energy_window_update) from the ISR.
 * PDM0_IRQHandler also owns the production handle (drv_pdm_production.c).
 * Ambiq HAL bodies are reconstructed elsewhere under the names reused here. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_drv_pdm.h"

/* am_hal_pdm_config_t, stock layout (IAR one-byte enums, two-byte clock
 * speed enum). Values shown are the shared image at RAM 0x20000900 and
 * 0x20000928 (defined in codec-pdm-init as 28-byte arrays). */
typedef struct {
    uint8_t clk_divider;        /* +0x00 eClkDivider 1 = MCLKDIV_1 -> CORECFG1.DIVMCLKQ */
    uint8_t pdma_clko_divider;  /* +0x01 ePDMAClkOutDivder 14 -> CORECFG0.MCLKDIV (/15) */
    uint8_t left_gain;          /* +0x02 eLeftGain 9 = +1.5 dB -> CORECFG0.PGAL */
    uint8_t right_gain;         /* +0x03 eRightGain 9 = +1.5 dB -> CORECFG0.PGAR */
    uint8_t step_size;          /* +0x04 eStepSize 0 = 0.13 dB -> CORECFG1.SELSTEP */
    uint8_t pad_05[3];
    uint32_t decimation_rate;   /* +0x08 25 -> CORECFG0.SINCRATE */
    uint8_t high_pass_enable;   /* +0x0c 0 -> CORECFG0.ADCHPD = 0 (HPF on) */
    uint8_t pad_0d[3];
    uint32_t high_pass_cutoff;  /* +0x10 3 -> CORECFG0.HPGAIN */
    uint16_t clk_speed;         /* +0x14 0x0202: CLKGEN mux, PDM0_CTRL_CLKSEL_HFRC_24MHz */
    uint8_t data_packing;       /* +0x16 1 -> CTRL.PCMPACK */
    uint8_t pcm_channels;       /* +0x17 1 = MONOL -> CORECFG1.PCMCHSET */
    uint8_t sample_delay;       /* +0x18 0 -> CORECFG1.CKODLY */
    uint8_t gain_change_delay;  /* +0x19 0 -> CORECFG0.SCYCLES */
    uint8_t soft_mute;          /* +0x1a 0 -> CORECFG0.SOFTMUTE */
    uint8_t lr_swap;            /* +0x1b 0 -> CORECFG0.LRSWAP */
} g2_pdm_config_t;
_Static_assert(sizeof(g2_pdm_config_t) == 28, "stock PDM config is 28 bytes");

/* am_hal_pdm_transfer_t. */
typedef struct {
    uint32_t target;            /* +0x00 ping */
    uint32_t target_reverse;    /* +0x04 pong */
    uint32_t total_count;       /* +0x08 bytes per block */
} g2_pdm_transfer_t;
_Static_assert(sizeof(g2_pdm_transfer_t) == 12, "stock PDM transfer is 12 bytes");

enum { SYSCTRL_WAKE = 0u, SYSCTRL_NORMALSLEEP = 1u };
#define PDM_INT_DCMP 0x08u
#define PDM_INT_DERR 0x10u
#define PDM_IRQ_PRIORITY 4u
#define PDM_FIFO_THRESHOLD 16u
#define PDM_POWER_GPIO 143u
#define PDM_DMA_BLOCK_BYTES (G2_PDM_BLOCK_SAMPLES * 4u)
#define PDM_PCM_BLOCK_BYTES (G2_PDM_BLOCK_SAMPLES * 2u)

extern uint8_t g2_pdm_alternate_initialized;     /* RAM 0x20074fba */
extern void *g2_pdm_alternate_handle;            /* RAM 0x2007454c */
extern uint8_t g2_pdm_alternate_config[];        /* RAM 0x20000900 g2_pdm_config_t */
extern uint8_t g2_pdm_alternate_descriptor[];    /* RAM 0x2000091c g2_pdm_transfer_t */
extern const int16_t g2_pdm_alternate_irq;       /* ROM 0x78f55a = 48 (PDM0_IRQn) */
extern void *g2_pdm_production_handle;           /* RAM 0x20074550 */
extern uint8_t g2_pdm_production_descriptor[];   /* RAM 0x20000944 g2_pdm_transfer_t */
extern uint8_t g2_pdm_production_bypass;         /* RAM 0x20075019, nonzero keeps product mode 1 on this handle */

/* Existing g2/src names for the stock bodies (upstream name in comment). */
extern void g2_pdm_clock_enable(uint32_t group);                     /* 0x4c31d8 am_bsp_pdm_pins_enable */
extern uint32_t g2_codec_pin_write(uint32_t pin, uint32_t value);    /* 0x53a5be */
extern uint32_t g2_pdm_acquire(uint32_t instance, void **cell);      /* 0x591fac am_hal_pdm_initialize */
extern uint32_t g2_pdm_disable(void *handle, uint32_t state, uint32_t retain); /* 0x592046 am_hal_pdm_power_control */
extern uint32_t g2_pdm_configure(void *handle, const void *config);  /* 0x5920cc am_hal_pdm_configure */
extern uint32_t g2_pdm_irq_prepare(void *handle);                    /* 0x592230 am_hal_pdm_enable */
extern uint32_t g2_pdm_start(void *handle, const void *descriptor);  /* 0x59235e am_hal_pdm_dma_start */
extern uint32_t g2_pdm_prepare_clock(void *handle, uint32_t value);  /* 0x592462 am_hal_pdm_fifo_threshold_setup */
extern uint32_t g2_pdm_prepare_dma(void *handle, uint32_t mask);     /* 0x592556 am_hal_pdm_interrupt_enable */
extern uint32_t audio_pdm_interrupt_clear(const uint32_t *handle, uint32_t mask); /* 0x5925b4 am_hal_pdm_interrupt_clear */
extern void audio_uart_buffer_zero(void *destination, uint32_t length, uint32_t fill); /* 0x43c0e4 memset */
extern void audio_ble_privacy_cache_maintenance(const uint32_t *range, uint8_t clean); /* 0x475014 am_hal_cachectrl_dcache_invalidate */
extern void am_bsp_pdm_pins_disable_4c3204(uint32_t module); /* C1: stock returns void */
extern uint32_t am_hal_pdm_deinitialize_592014(void *handle);
extern uint32_t am_hal_pdm_disable_5922d6(void *handle);
extern uint32_t am_hal_pdm_interrupt_service_592484(void *handle, uint32_t status, void *transfer);
extern uint32_t am_hal_pdm_interrupt_disable_592584(void *handle, uint32_t mask);
extern uint32_t am_hal_pdm_interrupt_status_get_5925e0(void *handle, uint32_t *status, bool enabled_only);
extern uint32_t am_hal_pdm_dma_get_buffer_59262c(void *handle);
extern uint8_t productModeGet(void);                                 /* 0x4abe60 */
extern void aud_send_codec_control_message(void);                    /* 0x53c6d2, audio thread message type 3 */
extern int32_t service_algo_energy_window_update(const int16_t *pcm, uint32_t bytes); /* 0x591c26 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);   /* 0x43ce9e */

/* Driver-owned 16-bit PCM block, stock RAM 0x2006fc4c. */
static uint8_t pdm_pcm_block[PDM_PCM_BLOCK_BYTES] __attribute__((aligned(4)));

static const char module_tag[] = "drv.audio.pdm"; /* ROM 0x785d10 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\pdm\\drv_pdm.c"; /* ROM 0x714968 */
static const char init_fn[] = "DRV_PdmInit";     /* ROM 0x78a904 */
static const char deinit_fn[] = "DRV_PdmDeinit"; /* ROM 0x785d20 */
static const char already_init[] = "pdm already init."; /* ROM 0x77f130 */
static const char already_init_short[] = "[drv.audio.pdm]pdm already init."; /* ROM 0x7540b0 */
static const char init_done[] = "PDM init";      /* ROM 0x78a910 */
static const char init_done_short[] = "[drv.audio.pdm]PDM init"; /* ROM 0x776fac */
static const char already_deinit[] = "pdm already deinit."; /* ROM 0x77f144 */
static const char already_deinit_short[] = "[drv.audio.pdm]pdm already deinit."; /* ROM 0x7540d4 */
static const char deinit_done[] = "PDM deinit";  /* ROM 0x78a91c */
static const char deinit_done_short[] = "[drv.audio.pdm]PDM deinit"; /* ROM 0x76b458 */

#define PDM_LOG(level, mask, line, fn, msg, msg_short)                             \
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

void DRV_PdmInit(void)
{
    if (g2_pdm_alternate_initialized != 0u) {
        PDM_LOG(4u, 0x10000000u, 78u, init_fn, already_init, already_init_short);
        return;
    }
    g2_pdm_alternate_initialized = 1u;
    g2_pdm_clock_enable(0u);
    (void)g2_codec_pin_write(PDM_POWER_GPIO, 1u);
    (void)g2_pdm_acquire(0u, &g2_pdm_alternate_handle);
    (void)g2_pdm_disable(g2_pdm_alternate_handle, SYSCTRL_WAKE, false);
    (void)g2_pdm_configure(g2_pdm_alternate_handle, g2_pdm_alternate_config);
    (void)g2_pdm_prepare_clock(g2_pdm_alternate_handle, PDM_FIFO_THRESHOLD);
    (void)g2_pdm_prepare_dma(g2_pdm_alternate_handle, PDM_INT_DERR | PDM_INT_DCMP);
    __NVIC_SetPriority(g2_pdm_alternate_irq, PDM_IRQ_PRIORITY);
    __NVIC_EnableIRQ(g2_pdm_alternate_irq);
    (void)g2_pdm_irq_prepare(g2_pdm_alternate_handle);
    (void)g2_pdm_start(g2_pdm_alternate_handle, g2_pdm_alternate_descriptor);
    PDM_LOG(3u, 0x0c000000u, 97u, init_fn, init_done, init_done_short);
}

void DRV_PdmDeinit(void)
{
    if (g2_pdm_alternate_initialized == 0u) {
        PDM_LOG(4u, 0x10000000u, 103u, deinit_fn, already_deinit, already_deinit_short);
        return;
    }
    g2_pdm_alternate_initialized = 0u;
    (void)audio_pdm_interrupt_clear(g2_pdm_alternate_handle, PDM_INT_DERR | PDM_INT_DCMP);
    (void)am_hal_pdm_interrupt_disable_592584(g2_pdm_alternate_handle, PDM_INT_DERR | PDM_INT_DCMP);
    __NVIC_DisableIRQ(g2_pdm_alternate_irq);
    (void)am_bsp_pdm_pins_disable_4c3204(0u);
    (void)am_hal_pdm_disable_5922d6(g2_pdm_alternate_handle);
    (void)g2_pdm_disable(g2_pdm_alternate_handle, SYSCTRL_NORMALSLEEP, false);
    (void)am_hal_pdm_deinitialize_592014(g2_pdm_alternate_handle);
    PDM_LOG(3u, 0x0c000000u, 115u, deinit_fn, deinit_done, deinit_done_short);
}

/* PDM0 vector (IRQ 48, vector slot 0x438100). Product mode 1 without the
 * bypass byte services the production handle and posts a type-3 audio
 * thread message; otherwise the normal block is converted and measured
 * in interrupt context. */
void PDM0_IRQHandler(void)
{
    uint32_t status;
    if (productModeGet() == 1u && g2_pdm_production_bypass == 0u) {
        (void)am_hal_pdm_interrupt_status_get_5925e0(g2_pdm_production_handle, &status, true);
        (void)audio_pdm_interrupt_clear(g2_pdm_production_handle, status);
        (void)am_hal_pdm_interrupt_service_592484(g2_pdm_production_handle, status,
                                                  g2_pdm_production_descriptor);
        if (status & PDM_INT_DCMP)
            aud_send_codec_control_message();
        return;
    }
    (void)am_hal_pdm_interrupt_status_get_5925e0(g2_pdm_alternate_handle, &status, true);
    (void)audio_pdm_interrupt_clear(g2_pdm_alternate_handle, status);
    (void)am_hal_pdm_interrupt_service_592484(g2_pdm_alternate_handle, status,
                                              g2_pdm_alternate_descriptor);
    if (status & PDM_INT_DCMP) {
        uint8_t *pcm = NULL;
        uint32_t length = 0u;
        drv_pdm_buffer_get(&pcm, &length);
        (void)service_algo_energy_window_update((const int16_t *)(void *)pcm, length);
    }
}

/* The range starts from the ROM template 0x78d494 {0, 640}. */
void drv_pdm_buffer_get(uint8_t **buffer, uint32_t *length)
{
    const uint32_t *raw = (const uint32_t *)(uintptr_t)
        am_hal_pdm_dma_get_buffer_59262c(g2_pdm_alternate_handle);
    uint32_t range[2] = { 0u, PDM_DMA_BLOCK_BYTES }; /* am_hal_cachectrl_range_t */
    range[0] = (uint32_t)(uintptr_t)raw;
    audio_ble_privacy_cache_maintenance(range, 0u);
    audio_uart_buffer_zero(pdm_pcm_block, PDM_PCM_BLOCK_BYTES, 0u);
    for (uint32_t i = 0; i < G2_PDM_BLOCK_SAMPLES; i++) {
        pdm_pcm_block[2u * i] = (uint8_t)(raw[i] >> 8);
        pdm_pcm_block[2u * i + 1u] = (uint8_t)(raw[i] >> 16);
    }
    *buffer = pdm_pcm_block;
    *length = PDM_PCM_BLOCK_BYTES;
}
