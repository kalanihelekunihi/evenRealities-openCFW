/* Stock Apollo quicklist_data_mutex_init 0x4ffa70. */
#include <stdint.h>

void *audio_quicklist_storage_mutex; /* native BSS 0x200748f0 */
extern void *audio_uart_mutex_new(const void *); /* selected 0x44971c */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* selected 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* selected 0x43ce9e */

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\quicklist.c";
static const char function[] = "quicklist_data_mutex_init";
static const char message[] = "Failed to create quicklist storage mutex";
static const char compact[] = "[quicklist.page]Failed to create quicklist storage mutex";

uint32_t audio_quicklist_data_mutex_init_4ffa70(void) {
    if(audio_quicklist_storage_mutex != 0) return 0u;
    audio_quicklist_storage_mutex = audio_uart_mutex_new(0);
    if(audio_quicklist_storage_mutex != 0) return 0u;
    if((audio_log_flags() & 2u) != 0u)
        audio_log_extended(1u, module, path, function, 35u, message);
    if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x04000000u, compact, compact);
    return 8u;
}
