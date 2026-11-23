#include <stdint.h>

/* Stock 0x44a9ae: one byte at the authenticated RAM address. Placement and
 * initialization of the state byte remain an independent image concern. */
extern volatile uint8_t compress_log_export_active_flag; /* stock 0x20074fa1, compress_log_port.c */
/* Stock 0x0044A9AE (compress_log_export_active) */
uint32_t audio_log_policy(uint32_t ignored) {
    (void)ignored;
    return compress_log_export_active_flag;
}
