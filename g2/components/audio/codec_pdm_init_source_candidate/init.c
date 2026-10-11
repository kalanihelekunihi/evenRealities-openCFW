#include <stdint.h>

/* Full public PDM initialization bodies: production 0x57b4a8..0x57b585,
 * alternate 0x57b770..0x57b86b. Product cells remain typed externs. */
extern uint8_t g2_pdm_production_initialized;    /* 0x20074fbb */
extern void *g2_pdm_production_handle;           /* 0x20074550 */
extern uint8_t g2_pdm_production_config[];       /* 0x20000928 */
extern const int16_t g2_pdm_production_irq;      /* 0x78f55c */
extern uint8_t g2_pdm_production_descriptor[];   /* 0x20000944 */
extern uint8_t g2_pdm_alternate_initialized;     /* 0x20074fba */
extern void *g2_pdm_alternate_handle;            /* 0x2007454c */
extern uint8_t g2_pdm_alternate_config[];        /* 0x20000900 */
extern const int16_t g2_pdm_alternate_irq;       /* 0x78f55a */
extern uint8_t g2_pdm_alternate_descriptor[];    /* 0x2000091c */

extern void g2_pdm_clock_enable(uint32_t group); /* 0x4c31d8 */
extern uint32_t g2_codec_pin_write(uint32_t pin, uint32_t state); /* 0x53a5be */
extern uint32_t g2_pdm_acquire(uint32_t instance, void **cell); /* 0x591fac */
extern uint32_t g2_pdm_disable(void *handle, uint32_t mode, uint32_t backup); /* 0x592046 */
extern uint32_t g2_pdm_configure(void *handle, const void *config); /* 0x5920cc */
extern uint32_t g2_pdm_prepare_clock(void *handle, uint32_t mode); /* 0x592462 */
extern uint32_t g2_pdm_prepare_dma(void *handle, uint32_t mode); /* 0x592556 */
extern void g2_codec_irq_priority(int32_t irq, uint32_t priority);
extern void g2_codec_irq_enable(int32_t irq);
extern uint32_t g2_pdm_irq_prepare(void *handle); /* 0x592230 */
extern uint32_t g2_pdm_start(void *handle, const void *descriptor); /* 0x59235e */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char production_module[] = "drv.audio.pdm.production";
static const char production_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\pdm\\drv_pdm_production.c";
static const char production_function[] = "DRV_PdmProductionInit";
static const char alternate_module[] = "drv.audio.pdm";
static const char alternate_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\pdm\\drv_pdm.c";
static const char alternate_function[] = "DRV_PdmInit";
static const char already[] = "pdm already init.";
static const char initialized[] = "PDM init";
static const char production_already_simple[] =
    "[drv.audio.pdm.production]pdm already init.";
static const char production_initialized_simple[] =
    "[drv.audio.pdm.production]PDM init";
static const char alternate_already_simple[] =
    "[drv.audio.pdm]pdm already init.";
static const char alternate_initialized_simple[] =
    "[drv.audio.pdm]PDM init";

static void enable(volatile uint8_t *initialized_cell, void **handle_cell,
                   const void *config, int32_t irq, const void *descriptor,
                   const char *module, const char *file, const char *function,
                   const char *already_simple, const char *initialized_simple,
                   uint32_t already_line, uint32_t init_line) {
    if (*initialized_cell != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, file, function,
                               already_line, already);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x10000000u, already_simple, already_simple);
        return;
    }
    *initialized_cell = 1u;
    g2_pdm_clock_enable(0u);
    (void)g2_codec_pin_write(0x8fu, 1u);
    (void)g2_pdm_acquire(0u, handle_cell);
    (void)g2_pdm_disable(*handle_cell, 0u, 0u);
    (void)g2_pdm_configure(*handle_cell, config);
    (void)g2_pdm_prepare_clock(*handle_cell, 0x10u);
    (void)g2_pdm_prepare_dma(*handle_cell, 0x18u);
    g2_codec_irq_priority(irq, 4u);
    g2_codec_irq_enable(irq);
    (void)g2_pdm_irq_prepare(*handle_cell);
    (void)g2_pdm_start(*handle_cell, descriptor);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, file, function,
                           init_line, initialized);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c000000u, initialized_simple,
                         initialized_simple);
}

void audio_pdm_enable_primary(void) {
    enable(&g2_pdm_production_initialized, &g2_pdm_production_handle,
           g2_pdm_production_config, g2_pdm_production_irq,
           g2_pdm_production_descriptor, production_module,
           production_file, production_function, production_already_simple,
           production_initialized_simple, 92u, 115u);
}

void audio_pdm_enable_alternate(void) {
    enable(&g2_pdm_alternate_initialized, &g2_pdm_alternate_handle,
           g2_pdm_alternate_config, g2_pdm_alternate_irq,
           g2_pdm_alternate_descriptor, alternate_module,
           alternate_file, alternate_function, alternate_already_simple,
           alternate_initialized_simple, 78u, 97u);
}
