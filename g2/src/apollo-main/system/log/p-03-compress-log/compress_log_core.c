/* Compact-log ring core, stock D:\01_workspace\s200_ap510b_iar_git\platform\service\compress_log\core\compress_log.c.
 * Native 0x43c7cc..0x43c8d1 and 0x43cf02..0x43d0c7 (shared literal pool 0x43d0e0..0x43d13b).
 *
 * The ring descriptor at RAM 0x200004c8 is {base, capacity, read, write}. Writers
 * (compress_log_ring_write 0x43ca50, owned by system/log/audio-log/audio-log-format/emit.c)
 * advance `write`; the readers here advance `read` and hand 4096-byte blocks to the
 * file port (compress_log_sync_to_files 0x44a798, /log/compress_log_N.bin rotation).
 * Thread-mode readers take the recursive mutex at RAM 0x20074388; _log_get_all_buffer
 * instead masks interrupts so it also works from an exception (fault dump path). */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct {
    uint32_t base;     /* +0x0 ring storage address */
    uint32_t capacity; /* +0x4 */
    uint32_t read;     /* +0x8 */
    uint32_t write;    /* +0xc */
} g2_compress_log_ring_t;
_Static_assert(sizeof(g2_compress_log_ring_t) == 16u, "ring descriptor is four words");

#define CLOG_BLOCK_BYTES 0x1000u
#define CLOG_MAX_BATCH 9u
#define CLOG_SYNC_PERIOD_TICKS 10000u
#define CLOG_LOCK_TIMEOUT 500u
#define QUEUE_TYPE_RECURSIVE_MUTEX 4u

extern volatile uint32_t g2_audio_log_ring_state[4]; /* RAM 0x200004c8, g2_compress_log_ring_t */
extern void *audio_log_lock_state;                   /* RAM 0x20074388 recursive mutex handle */
extern uint8_t g2_compress_log_mutex_storage[];      /* RAM 0x20072998 StaticSemaphore_t */
extern volatile uint32_t g2_compress_log_last_sync_tick; /* RAM 0x2007438c */
extern uint8_t g2_compress_log_sync_block[CLOG_BLOCK_BYTES]; /* RAM 0x200d4bd8 */

extern uint64_t audio_os_mutex_alloc_static_4416f0(uint32_t kind, uint32_t memory); /* xQueueCreateMutexStatic */
extern int32_t audio_log_lock(void *mutex, uint32_t timeout);   /* 0x441750 xSemaphoreTakeRecursive */
extern void audio_log_unlock(void *mutex);                     /* 0x441710 xSemaphoreGiveRecursive */
extern uint32_t ulSetInterruptMask(void);                      /* 0x5fa0a4 */
extern void vClearInterruptMask(uint32_t mask);                /* 0x5fa0ba */
extern void stock_enter_critical(void);                        /* 0x4420d0 vPortEnterCritical */
extern void stock_exit_critical(void);                         /* 0x4420e8 vPortExitCritical */
extern void *audio_uart_checksum_copy(void *dst, const void *src, uint32_t len); /* 0x439be4 memcpy */
extern uint32_t osKernelGetTickCount(void);                    /* 0x4490cc */
extern void compress_log_sync_to_files(const uint8_t *data, uint32_t len); /* 0x44a798 */
extern uint32_t audio_log_flags(void);                         /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "S200"; /* ROM 0x78d1ec */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\compress_log\\core\\compress_log.c"; /* ROM 0x6e2b18 */
static const char get_all_fn[] = "_log_get_all_buffer"; /* ROM 0x77e988 */
static const char get_all_state[] =
    "_log get all buffer: read=%u, write=%u, capacity=%u, length=%u"; /* ROM 0x709f64 */
static const char get_all_state_short[] =
    "[S200]_log get all buffer: read=%u, write=%u, capacity=%u, length=%u"; /* ROM 0x6f92e4 */
static const char get_all_ok[] = "_log get all buffer: success, read %u bytes, ret=1"; /* ROM 0x727950 */
static const char get_all_ok_short[] =
    "[S200]_log get all buffer: success, read %u bytes, ret=1"; /* ROM 0x713360 */
static const char sync_fn[] = "svc_compress_log_sync_to_files"; /* ROM 0x75e7f0 */
static const char sync_done[] = "[CLOG] svc_compress_log_sync_to_files: synced %u blocks to flash"; /* ROM 0x700f80 */
static const char sync_done_short[] =
    "[S200][CLOG] svc_compress_log_sync_to_files: synced %u blocks to flash"; /* ROM 0x6f932c */
static const char force_fn[] = "svc_compress_log_force_sync_to_files"; /* ROM 0x74841c */
static const char force_start[] = "svc compress log force sync to files: start force sync"; /* ROM 0x71cd90 */
static const char force_start_short[] =
    "[S200]svc compress log force sync to files: start force sync"; /* ROM 0x709fa4 */
static const char force_max[] = "svc compress log force sync to files: max batch reached, count=%u"; /* ROM 0x700fc4 */
static const char force_max_short[] =
    "[S200]svc compress log force sync to files: max batch reached, count=%u"; /* ROM 0x6f9374 */
static const char force_done[] =
    "svc compress log force sync: done, blocks=%u, remaining=%u, total=%u bytes"; /* ROM 0x6f25a8 */
static const char force_done_short[] =
    "[S200]svc compress log force sync: done, blocks=%u, remaining=%u, total=%u bytes"; /* ROM 0x6e6dfc */

static inline uint32_t current_ipsr(void)
{
    uint32_t ipsr;
    __asm volatile("mrs %0, ipsr" : "=r"(ipsr));
    return ipsr;
}

static inline g2_compress_log_ring_t *ring(void)
{
    return (g2_compress_log_ring_t *)(uintptr_t)g2_audio_log_ring_state;
}

/* Copy `len` bytes out of the ring at `read`, wrapping once; returns the new read index. */
static uint32_t ring_copy_out(uint8_t *dst, uint32_t base, uint32_t capacity, uint32_t read, uint32_t len)
{
    uint32_t until_end = capacity - read;
    if (until_end >= len) {
        (void)audio_uart_checksum_copy(dst, (const void *)(uintptr_t)(base + read), len);
    } else {
        (void)audio_uart_checksum_copy(dst, (const void *)(uintptr_t)(base + read), until_end);
        (void)audio_uart_checksum_copy(dst + until_end, (const void *)(uintptr_t)base, len - until_end);
    }
    return (len >= until_end) ? len - until_end : read + len;
}

/* Lazily creates the static recursive mutex; a creation failure masks interrupts and traps. */
void compress_log_mutex_init(void)
{
    if (audio_log_lock_state != NULL)
        return;
    audio_log_lock_state = (void *)(uintptr_t)(uint32_t)audio_os_mutex_alloc_static_4416f0(
        QUEUE_TYPE_RECURSIVE_MUTEX, (uint32_t)(uintptr_t)g2_compress_log_mutex_storage);
    if (audio_log_lock_state == NULL) {
        (void)ulSetInterruptMask();
        *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
        for (;;) {
        }
    }
}

/* Thread-mode exact read; succeeds only when strictly more than len+1 bytes are queued. */
uint32_t compress_log_ring_read_locked(uint8_t *dst, uint16_t len)
{
    g2_compress_log_ring_t *r = ring();
    uint32_t base = r->base;
    uint32_t capacity = r->capacity;

    if (current_ipsr() != 0u || audio_log_lock_state == NULL)
        return 0u;
    if (audio_log_lock(audio_log_lock_state, CLOG_LOCK_TIMEOUT) != 1)
        return 0u;

    uint32_t read = r->read;
    uint32_t write = r->write;
    if (capacity < read || capacity < write) {
        audio_log_unlock(audio_log_lock_state);
        return 0u;
    }
    uint32_t used = (read < write) ? write - read - 1u : write + (capacity - read) - 1u;
    if ((uint32_t)len >= used) {
        audio_log_unlock(audio_log_lock_state);
        return 0u;
    }
    r->read = ring_copy_out(dst, base, capacity, read, len);
    audio_log_unlock(audio_log_lock_state);
    return 1u;
}

/* Exact read usable from thread or exception context (critical section or BASEPRI mask). */
uint32_t _log_get_all_buffer(uint8_t *dst, uint16_t len)
{
    g2_compress_log_ring_t *r = ring();
    uint32_t base = r->base;
    uint32_t capacity = r->capacity;
    uint32_t read = r->read;
    uint32_t write = r->write;
    uint32_t mask = 0u;

    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, get_all_fn, 0x7au, get_all_state,
                           read, write, capacity, (uint32_t)len);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0d000000u, get_all_state_short, get_all_state_short,
                                  read, write, capacity, (uint32_t)len);

    if (capacity < read || capacity < write)
        return 0u;
    uint32_t used = (write < read) ? write + (capacity - read) : write - read;
    if (used < (uint32_t)len)
        return 0u;

    if (current_ipsr() == 0u)
        stock_enter_critical();
    else
        mask = ulSetInterruptMask();
    r->read = ring_copy_out(dst, base, capacity, read, len);
    if (current_ipsr() == 0u)
        stock_exit_critical();
    else
        vClearInterruptMask(mask);

    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, get_all_fn, 0x97u, get_all_ok, (uint32_t)len);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, get_all_ok_short, get_all_ok_short, (uint32_t)len);
    return 1u;
}

/* Every 10000 ticks, drains at most nine full 4096-byte blocks to flash. */
void svc_compress_log_sync_to_files(void)
{
    uint32_t now = osKernelGetTickCount();
    if (g2_compress_log_last_sync_tick + CLOG_SYNC_PERIOD_TICKS >= now)
        return;
    g2_compress_log_last_sync_tick = now;

    uint8_t blocks = 0u;
    do {
        if (compress_log_ring_read_locked(g2_compress_log_sync_block, CLOG_BLOCK_BYTES) == 0u)
            break;
        blocks++;
        compress_log_sync_to_files(g2_compress_log_sync_block, CLOG_BLOCK_BYTES);
    } while (blocks < CLOG_MAX_BATCH);

    if (blocks != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, sync_fn, 0x1e8u, sync_done, (uint32_t)blocks);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x10400000u, sync_done_short, sync_done_short, (uint32_t)blocks);
    }
}

/* Drains full blocks (at most nine), then whatever remainder the ring still holds. */
void svc_compress_log_force_sync_to_files(void)
{
    uint8_t blocks = 0u;

    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, force_fn, 0x1f2u, force_start);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c000000u, force_start_short, force_start_short);

    for (;;) {
        if (compress_log_ring_read_locked(g2_compress_log_sync_block, CLOG_BLOCK_BYTES) == 0u)
            break;
        blocks++;
        compress_log_sync_to_files(g2_compress_log_sync_block, CLOG_BLOCK_BYTES);
        if (blocks >= CLOG_MAX_BATCH) {
            if (audio_log_flags() & 2u)
                audio_log_extended(4u, module_tag, source_file, force_fn, 0x1f8u, force_max, (uint32_t)blocks);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compress_log_output(0x10400000u, force_max_short, force_max_short, (uint32_t)blocks);
            break;
        }
    }

    g2_compress_log_ring_t *r = ring();
    uint32_t total = (uint32_t)blocks * CLOG_BLOCK_BYTES;
    uint32_t read = r->read;
    uint32_t remaining = (r->write < read) ? r->write + (r->capacity - read) : r->write - read;
    if (remaining != 0u &&
        _log_get_all_buffer(g2_compress_log_sync_block, (uint16_t)remaining) != 0u) {
        compress_log_sync_to_files(g2_compress_log_sync_block, remaining & 0xffffu);
        total += remaining & 0xffffu;
    }

    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, force_fn, 0x20cu, force_done,
                           (uint32_t)blocks, remaining, total);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0cc00000u, force_done_short, force_done_short,
                                  (uint32_t)blocks, remaining, total);
}
