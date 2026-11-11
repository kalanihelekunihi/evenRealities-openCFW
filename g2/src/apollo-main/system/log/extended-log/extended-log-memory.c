#include <stdint.h>

/* Value contract of optimized stock strlen at 0x44a43c..0x44a472. */
uint32_t g2_log_candidate_module_length(const uint8_t *module)
{
    const uint8_t *p = module;
    while (*p != 0u) p++;
    return (uint32_t)(p - module);
}
__typeof__(g2_log_candidate_module_length) g2_log_module_length
    __attribute__((alias("g2_log_candidate_module_length")));
__typeof__(g2_log_candidate_module_length) audio_string_length
    __attribute__((alias("g2_log_candidate_module_length")));

/* g2_log_candidate_stack_fill (stock fill 0x43c0e4) is an alias of
 * audio_uart_buffer_zero in drivers/peripherals/ring-init/ring_init.c. */
