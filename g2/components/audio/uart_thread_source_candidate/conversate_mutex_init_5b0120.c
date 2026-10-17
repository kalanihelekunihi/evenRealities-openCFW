/* Native conversate_action_mutex_init_internal 0x5b0120..0x5b01c9. */
#include <stdint.h>

struct conversate_mutex_attr {
    const char *name;
    uint32_t flags;
    void *cb_mem;
    uint32_t cb_size;
};
_Static_assert(sizeof(struct conversate_mutex_attr) == 16u,
               "CMSIS mutex attribute ABI");

extern uint32_t audio_conversate_action_mutex_20074398;
extern void *audio_uart_mutex_new(const void *); /* native 0x44971c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const struct conversate_mutex_attr attr = {
    "ConversateActionMutex", 0u, 0, 0u
};
static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate.c";
static const char function[] = "conversate_action_mutex_init_internal";
static const char failed[] = "Failed to create conversate action mutex";
static const char failed_short[] =
    "[conversate]Failed to create conversate action mutex";
static const char created[] =
    "Conversate action mutex created successfully with priority inherit";
static const char created_short[] =
    "[conversate]Conversate action mutex created successfully with priority inherit";

uint32_t audio_conversate_mutex_init_5b0120(void) {
    if (audio_conversate_action_mutex_20074398 != 0u) return 0u;
    audio_conversate_action_mutex_20074398 =
        (uint32_t)(uintptr_t)audio_uart_mutex_new(&attr);
    if (audio_conversate_action_mutex_20074398 == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 70u, failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, failed_short, failed_short);
        return UINT32_MAX;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 73u, created);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10000000u, created_short, created_short);
    return 0u;
}
