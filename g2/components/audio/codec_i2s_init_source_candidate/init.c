#include <stdint.h>

/* Stock DRV_Gx8002_I2SInit 0x0057a65c..0x0057a732. The handle,
 * config and IRQ cells retain their authenticated product placements. */
extern uint8_t g2_codec_i2s_initialized;          /* 0x20074fb7 */
extern void *g2_codec_i2s_handle;                  /* 0x2007450c */
extern uint8_t g2_codec_i2s_config_base[];        /* 0x20000000 */
extern uint8_t g2_codec_i2s_dma_descriptor[];     /* 0x20000740 */
extern const int16_t g2_codec_i2s_irq_number;     /* 0x78f558 */
extern void g2_codec_clock_enable(uint32_t group, uint32_t mode);
extern uint32_t g2_codec_i2s_acquire(uint32_t instance, void **handle_cell);
extern uint32_t g2_codec_i2s_disable(void *handle, uint32_t a, uint32_t b);
extern uint32_t g2_codec_i2s_configure(void *handle, const void *config);
extern uint32_t g2_codec_i2s_prepare(void *handle);
extern uint32_t g2_codec_i2s_dma_configure(void *handle, const void *config,
                                       const void *descriptor);
extern void g2_codec_irq_priority(int32_t irq, uint32_t priority);
extern void g2_codec_irq_enable(int32_t irq);
extern uint32_t g2_codec_global_irq_enable(void);
extern int32_t g2_codec_i2s_start(void *handle, const void *config);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "drv.audio.codec";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\codec\\drv_gx8002b.c";
static const char function[] = "DRV_Gx8002_I2SInit";
static const char already[] = "gx8002b i2s already init.";
static const char simple_already[] = "[drv.audio.codec]gx8002b i2s already init.";
static const char initialized[] = "gx8002b i2s init.";
static const char simple_initialized[] = "[drv.audio.codec]gx8002b i2s init.";

void audio_i2s_enable(void) {
    if (g2_codec_i2s_initialized != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, file, function, 121u, already);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x10000000u, simple_already, simple_already);
        return;
    }

    g2_codec_i2s_initialized = 1u;
    g2_codec_clock_enable(0u, 0u);
    (void)g2_codec_i2s_acquire(0u, &g2_codec_i2s_handle);
    (void)g2_codec_i2s_disable(g2_codec_i2s_handle, 0u, 0u);
    (void)g2_codec_i2s_configure(g2_codec_i2s_handle, g2_codec_i2s_config_base);
    (void)g2_codec_i2s_prepare(g2_codec_i2s_handle);
    (void)g2_codec_i2s_dma_configure(g2_codec_i2s_handle, g2_codec_i2s_config_base,
                                      g2_codec_i2s_dma_descriptor);
    g2_codec_irq_priority(g2_codec_i2s_irq_number, 4u);
    g2_codec_irq_enable(g2_codec_i2s_irq_number);
    (void)g2_codec_global_irq_enable();
    (void)g2_codec_i2s_start(g2_codec_i2s_handle, g2_codec_i2s_config_base);

    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, file, function, 137u, initialized);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10000000u, simple_initialized, simple_initialized);
}
