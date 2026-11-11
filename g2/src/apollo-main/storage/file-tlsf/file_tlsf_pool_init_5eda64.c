/* Stock TLSF backing-pool initialization, Apollo 0x5eda64. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_file_tlsf_backing_20208e70[] __asm__("g2_file_tlsf_backing_20208e70");

extern void *g2_codec_heap_pool;
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void *g2_tlsf_create_with_pool_4d06ec(void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "tlsf";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\tlsf\\tlsf_init.c";
static const char function[] = "tlsf_adapter_init";
static const char message[] = "tlsf init.";
static const char short_message[] = "[tlsf]tlsf init.";

uint32_t audio_file_tlsf_pool_init_5eda64(void) {
    void *const memory = (void *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_file_tlsf_backing_20208e70);
    audio_uart_buffer_zero(memory, 0x70800u, 0u);
    g2_codec_heap_pool = g2_tlsf_create_with_pool_4d06ec(memory, 0x70800u);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x13u, message);
    uint32_t flags = audio_log_flags();
    if ((flags & 1u) || (!(flags & 1u) && (audio_log_flags() & 4u)))
        (void)compressed_log_output(0x10000000u, short_message, short_message);
    return 0u;
}
