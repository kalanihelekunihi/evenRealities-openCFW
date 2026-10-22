/* Production-test PDM microphone driver,
 * stock D:\01_workspace\s200_ap510b_iar_git\driver\pdm\drv_pdm_production.c.
 * Native 0x57b444..0x57b6a5; literal pool 0x57b6a8..0x57b703.
 *
 * Same PDM0 block, pads, GPIO143 enable, configuration image and IRQ (48,
 * priority 4) as drv_pdm.c, but its own handle and DMA ping 0x20347a00 /
 * pong 0x20349300 with 6,400 bytes (1,600 x 32-bit words) per block. The
 * interrupt is serviced by PDM0_IRQHandler in drv_pdm.c. The getter cuts a
 * block to 1,600 16-bit samples in a 3,200-byte scratch buffer. */
#include <stdint.h>
#include <stdbool.h>
#include "g2_drv_pdm.h"

enum { SYSCTRL_WAKE = 0u, SYSCTRL_NORMALSLEEP = 1u };
#define PDM_INT_DCMP 0x08u
#define PDM_INT_DERR 0x10u
#define PDM_IRQ_PRIORITY 4u
#define PDM_FIFO_THRESHOLD 16u
#define PDM_POWER_GPIO 143u
#define PDM_DMA_BLOCK_BYTES (G2_PDM_PRODUCTION_BLOCK_SAMPLES * 4u)
#define PDM_PCM_BLOCK_BYTES (G2_PDM_PRODUCTION_BLOCK_SAMPLES * 2u)

extern uint8_t g2_pdm_production_initialized;    /* RAM 0x20074fbb */
extern void *g2_pdm_production_handle;           /* RAM 0x20074550 */
extern uint8_t g2_pdm_production_config[];       /* RAM 0x20000928, am_hal_pdm_config_t (see drv_pdm.c) */
extern uint8_t g2_pdm_production_descriptor[];   /* RAM 0x20000944, am_hal_pdm_transfer_t */
extern const int16_t g2_pdm_production_irq;      /* ROM 0x78f55c = 48 (PDM0_IRQn) */

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
extern uint32_t am_hal_pdm_interrupt_disable_592584(void *handle, uint32_t mask);
extern uint32_t am_hal_pdm_dma_get_buffer_59262c(void *handle);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);   /* 0x43ce9e */

/* Driver-owned 16-bit PCM block, stock RAM 0x20062a20. */
static uint8_t pdm_production_pcm_block[PDM_PCM_BLOCK_BYTES] __attribute__((aligned(4)));

static const char module_tag[] = "drv.audio.pdm.production"; /* ROM 0x76b474 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\pdm\\drv_pdm_production.c"; /* ROM 0x7025d0 */
static const char init_fn[] = "DRV_PdmProductionInit";     /* ROM 0x776fc4 */
static const char deinit_fn[] = "DRV_PdmProductionDeinit"; /* ROM 0x776fdc */
static const char already_init[] = "pdm already init."; /* ROM 0x77f158 */
static const char already_init_short[] = "[drv.audio.pdm.production]pdm already init."; /* ROM 0x73e844 */
static const char init_done[] = "PDM init";      /* ROM 0x78a928 */
static const char init_done_short[] = "[drv.audio.pdm.production]PDM init"; /* ROM 0x7540f8 */
static const char already_deinit[] = "pdm already deinit."; /* ROM 0x77f16c */
static const char already_deinit_short[] = "[drv.audio.pdm.production]pdm already deinit."; /* ROM 0x733af4 */
static const char deinit_done[] = "PDM deinit";  /* ROM 0x78a934 */
static const char deinit_done_short[] = "[drv.audio.pdm.production]PDM deinit"; /* ROM 0x749c2c */

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

void DRV_PdmProductionInit(void)
{
    if (g2_pdm_production_initialized != 0u) {
        PDM_LOG(4u, 0x10000000u, 92u, init_fn, already_init, already_init_short);
        return;
    }
    g2_pdm_production_initialized = 1u;
    g2_pdm_clock_enable(0u);
    (void)g2_codec_pin_write(PDM_POWER_GPIO, 1u);
    (void)g2_pdm_acquire(0u, &g2_pdm_production_handle);
    (void)g2_pdm_disable(g2_pdm_production_handle, SYSCTRL_WAKE, false);
    (void)g2_pdm_configure(g2_pdm_production_handle, g2_pdm_production_config);
    (void)g2_pdm_prepare_clock(g2_pdm_production_handle, PDM_FIFO_THRESHOLD);
    (void)g2_pdm_prepare_dma(g2_pdm_production_handle, PDM_INT_DERR | PDM_INT_DCMP);
    __NVIC_SetPriority(g2_pdm_production_irq, PDM_IRQ_PRIORITY);
    __NVIC_EnableIRQ(g2_pdm_production_irq);
    (void)g2_pdm_irq_prepare(g2_pdm_production_handle);
    (void)g2_pdm_start(g2_pdm_production_handle, g2_pdm_production_descriptor);
    PDM_LOG(3u, 0x0c000000u, 115u, init_fn, init_done, init_done_short);
}

void DRV_PdmProductionDeinit(void)
{
    if (g2_pdm_production_initialized == 0u) {
        PDM_LOG(4u, 0x10000000u, 121u, deinit_fn, already_deinit, already_deinit_short);
        return;
    }
    g2_pdm_production_initialized = 0u;
    (void)audio_pdm_interrupt_clear(g2_pdm_production_handle, PDM_INT_DERR | PDM_INT_DCMP);
    (void)am_hal_pdm_interrupt_disable_592584(g2_pdm_production_handle, PDM_INT_DERR | PDM_INT_DCMP);
    __NVIC_DisableIRQ(g2_pdm_production_irq);
    (void)am_bsp_pdm_pins_disable_4c3204(0u);
    (void)am_hal_pdm_disable_5922d6(g2_pdm_production_handle);
    (void)g2_pdm_disable(g2_pdm_production_handle, SYSCTRL_NORMALSLEEP, false);
    (void)am_hal_pdm_deinitialize_592014(g2_pdm_production_handle);
    PDM_LOG(3u, 0x0c000000u, 137u, deinit_fn, deinit_done, deinit_done_short);
}

/* The range starts from the ROM template 0x78d49c {0, 6400}. */
void drv_pdm_production_buffer_get(uint8_t **buffer, uint32_t *length)
{
    const uint32_t *raw = (const uint32_t *)(uintptr_t)
        am_hal_pdm_dma_get_buffer_59262c(g2_pdm_production_handle);
    uint32_t range[2] = { 0u, PDM_DMA_BLOCK_BYTES }; /* am_hal_cachectrl_range_t */
    range[0] = (uint32_t)(uintptr_t)raw;
    audio_ble_privacy_cache_maintenance(range, 0u);
    audio_uart_buffer_zero(pdm_production_pcm_block, PDM_PCM_BLOCK_BYTES, 0u);
    for (uint32_t i = 0; i < G2_PDM_PRODUCTION_BLOCK_SAMPLES; i++) {
        pdm_production_pcm_block[2u * i] = (uint8_t)(raw[i] >> 8);
        pdm_production_pcm_block[2u * i + 1u] = (uint8_t)(raw[i] >> 16);
    }
    *buffer = pdm_production_pcm_block;
    *length = PDM_PCM_BLOCK_BYTES;
}
