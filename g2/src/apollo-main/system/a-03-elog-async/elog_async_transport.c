/* EasyLogger async back end (G2 downstream glue), stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\EasyLogger-master\easylogger\src\elog_async_api.c
 * (log tag "elog.async"). Shared literal pool 0x448f40..0x44900b.
 *
 * This unit: atomic helpers 0x4488ec..0x44895d, lock-free dequeue 0x448b96,
 * level-only enqueue 0x448ccc, consumer drain 0x448dd2, crash-record recovery
 * hook 0x448e2a and elog_async_ext_flieStore_Init 0x448e48. Pool/sentinel initialisation (0x44895e, 0x4489e8, 0x448c74), node
 * allocate/free/enqueue (0x448a0c, 0x448a8e, 0x448af0) and the mode-carrying
 * enqueue 0x448d4e already live under system/log/extended-log/extended-log-runtime.
 *
 * Queue: 254 pool nodes of 0x110 bytes at RAM 0x202d3fc8 form a free list
 * (head RAM 0x20074574); pending entries form a Michael-Scott queue whose head
 * and tail words are RAM 0x20074138/0x2007413c with the static dummy node
 * 0x202e4eb8 (pool slot 255). Dequeue copies the successor's text into the old
 * head and returns the old head, which the consumer frees after output. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct g2_elog_node {
    struct g2_elog_node *next; /* +0x00 */
    uint32_t state;            /* +0x04 */
    uint16_t length;           /* +0x08 payload bytes (<= 255) */
    uint16_t level;            /* +0x0a bit 0 = deliver to the output sink */
    uint8_t mode;              /* +0x0c */
    char text[256];            /* +0x0d NUL-terminated */
    uint8_t pad[3];
} g2_elog_node_t;
_Static_assert(sizeof(g2_elog_node_t) == 0x110u, "stock elog async node stride");
_Static_assert(offsetof(g2_elog_node_t, text) == 0x0du, "payload at +0x0d");

/* Consumer statistics, RAM 0x2007342c (cleared as 0x30 bytes at init). */
typedef struct {
    uint32_t drained;          /* +0x00 nodes handed to the sink */
    uint32_t reserved[8];      /* +0x04 producer-side counters */
    uint32_t dequeue_retries;  /* +0x24 sum of extra CAS rounds */
    uint32_t dequeue_peak;     /* +0x28 largest attempt count */
    uint32_t dequeue_timeouts; /* +0x2c dequeue gave up after 10000 rounds */
} g2_elog_stats_t;
_Static_assert(sizeof(g2_elog_stats_t) == 0x30u, "stats block cleared as 0x30 bytes");

/* Output sink, RAM 0x20073b90. */
typedef struct {
    uint8_t enabled;                                /* +0x00 */
    void (*output)(const char *text, uint16_t len); /* +0x04 */
} g2_elog_sink_t;

#define ELOG_DEQUEUE_ATTEMPTS 10000
#define ELOG_DRAIN_BATCH 0x100u
#define ELOG_MAX_TEXT 0xffu

extern g2_elog_node_t *volatile g2_elog_pending_head;   /* RAM 0x20074138 */
extern g2_elog_node_t *volatile g2_elog_pending_tail;   /* RAM 0x2007413c */
extern g2_elog_node_t g2_elog_dummy_node;               /* RAM 0x202e4eb8 */
extern g2_elog_stats_t g2_elog_stats;                   /* RAM 0x2007342c */
extern volatile uint8_t g2_elog_async_enabled;          /* RAM 0x20074fc0 */
extern volatile uint8_t g2_elog_default_level;          /* RAM 0x20004546 */
extern g2_elog_sink_t g2_elog_sink;                     /* RAM 0x20073b90 */

extern uint8_t *g2_log_transport_node_allocate(void);           /* 0x448a0c */
extern void g2_log_transport_node_free(uint8_t *node);          /* 0x448a8e */
extern uint32_t g2_log_transport_node_enqueue(uint8_t *node);   /* 0x448af0, 0 = failure */
extern int32_t g2_log_transport_queue_failure(const char *fmt, ...); /* 0x4733ee raw printf */
extern uint32_t crash_record_recover_to_file_47db02(const char *log_dir); /* 0x47db02 */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern uint32_t audio_log_flags(void);                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "elog.async"; /* ROM 0x78a994 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\EasyLogger-master\\easylogger\\src\\elog_async_api.c"; /* ROM 0x6da73c */
static const char file_store_init_fn[] = "elog_async_ext_flieStore_Init"; /* ROM 0x75fd50 */
static const char crash_recovered[] = "Crash info recovered from previous reset"; /* ROM 0x73ea28 */
static const char crash_recovered_short[] = "[elog.async]Crash info recovered from previous reset"; /* ROM 0x71e9c8 */
static const char enqueue_failed[] = "error!!!!!!elog_async_ext_output: enqueue_log failed\n"; /* ROM 0x71e990 */
static const char log_dir[] = "/log"; /* ROM 0x78d50c */

/* Release store: plain store followed by DMB (atomic_store). */
void elog_atomic_store_4488ec(volatile uint32_t *object, uint32_t value)
{
    *object = value;
    __asm__ volatile("dmb sy" ::: "memory");
}

/* Acquire load: plain load followed by DMB (atomic_load). */
uint32_t elog_atomic_load_4488f4(const volatile uint32_t *object)
{
    uint32_t value = *object;
    __asm__ volatile("dmb sy" ::: "memory");
    return value;
}

/* LDREX/STREX strong compare-exchange; on failure *expected receives the
 * observed value. Returns 1 when the swap happened. */
uint8_t elog_atomic_cas_4488fc(volatile uint32_t *object, uint32_t *expected, uint32_t desired)
{
    uint32_t want = *expected;
    uint32_t seen;
    uint32_t failed;
    do {
        __asm__ volatile("ldrex %0, [%1]" : "=&r"(seen) : "r"(object) : "memory");
        if (seen != want)
            break;
        __asm__ volatile("strex %0, %2, [%1]" : "=&r"(failed) : "r"(object), "r"(desired) : "memory");
    } while (failed != 0u);
    __asm__ volatile("dmb sy" ::: "memory");
    uint8_t ok = seen == *expected;
    if (!ok)
        *expected = seen;
    return ok;
}

/* Pointer-typed wrappers of the two accessors above. */
void elog_atomic_store_ptr_448930(void *volatile *object, void *value)
{
    elog_atomic_store_4488ec((volatile uint32_t *)(void *)object, (uint32_t)(uintptr_t)value);
}

void *elog_atomic_load_ptr_448938(void *volatile *object)
{
    return (void *)(uintptr_t)elog_atomic_load_4488f4((const volatile uint32_t *)(void *)object);
}

/* Pointer compare-exchange through a local copy of *expected. */
uint8_t elog_atomic_cas_ptr_448940(void *volatile *object, void **expected, void *desired)
{
    uint32_t local = (uint32_t)(uintptr_t)*expected;
    uint8_t ok = elog_atomic_cas_4488fc((volatile uint32_t *)(void *)object, &local, (uint32_t)(uintptr_t)desired);
    if (!ok)
        *expected = (void *)(uintptr_t)local;
    return ok;
}

/* Michael-Scott dequeue. Returns NULL when empty or after 10000 rounds. */
g2_elog_node_t *elog_async_dequeue_448b96(void)
{
    void *volatile *const head_slot = (void *volatile *)(void *)&g2_elog_pending_head;
    void *volatile *const tail_slot = (void *volatile *)(void *)&g2_elog_pending_tail;
    void *head;
    void *tail;
    g2_elog_node_t *next;
    int32_t attempts = 0;

    for (;;) {
        head = elog_atomic_load_ptr_448938(head_slot);
        tail = elog_atomic_load_ptr_448938(tail_slot);
        next = (g2_elog_node_t *)elog_atomic_load_ptr_448938((void *volatile *)head);
        attempts++;
        if (attempts > ELOG_DEQUEUE_ATTEMPTS) {
            g2_elog_stats.dequeue_timeouts++;
            return NULL;
        }
        if (head != elog_atomic_load_ptr_448938(head_slot))
            continue;
        if (head == tail) {
            if (next == NULL)
                return NULL;
            (void)elog_atomic_cas_ptr_448940(tail_slot, &tail, next); /* help a lagging tail */
            continue;
        }
        if (next == NULL)
            continue;
        if (elog_atomic_cas_ptr_448940(head_slot, &head, next) != 0u)
            break;
    }

    g2_elog_stats.dequeue_retries += (uint32_t)attempts - 1u;
    if (g2_elog_stats.dequeue_peak < (uint32_t)attempts)
        g2_elog_stats.dequeue_peak = (uint32_t)attempts;

    g2_elog_node_t *out = (g2_elog_node_t *)head;
    /* Stock has identical code on both sides of a head == dummy test. */
    if (out == &g2_elog_dummy_node) {
        audio_uart_checksum_copy(out->text, next->text, (uint32_t)next->length + 1u);
        out->length = next->length;
        out->level = next->level;
    } else {
        audio_uart_checksum_copy(out->text, next->text, (uint32_t)next->length + 1u);
        out->length = next->length;
        out->level = next->level;
    }
    return out;
}

/* Enqueue a text record without touching the mode byte; level 0 selects the
 * default level. Always returns 0. */
uint32_t elog_async_enqueue_log_448ccc(const char *text, uint32_t length, uint8_t level)
{
    if (g2_elog_async_enabled != 0u && text != NULL && length != 0u) {
        if (level == 0u)
            level = g2_elog_default_level;
        if (length > ELOG_MAX_TEXT)
            length = ELOG_MAX_TEXT;
        g2_elog_node_t *node = (g2_elog_node_t *)(void *)g2_log_transport_node_allocate();
        if (node != NULL) {
            audio_uart_checksum_copy(node->text, text, length);
            node->text[length] = '\0';
            node->length = (uint16_t)length;
            node->level = level;
            if (g2_log_transport_node_enqueue((uint8_t *)node) == 0u) {
                g2_log_transport_node_free((uint8_t *)node);
                (void)g2_log_transport_queue_failure(enqueue_failed);
            }
        }
    }
    return 0u;
}

/* Hand up to 256 pending records to the sink; returns how many were taken. */
uint32_t elog_async_drain_448dd2(void)
{
    if (g2_elog_async_enabled == 0u)
        return 0u;
    uint32_t taken = 0u;
    for (uint32_t i = 0u; i < ELOG_DRAIN_BATCH; i++) {
        g2_elog_node_t *node = elog_async_dequeue_448b96();
        if (node == NULL)
            break;
        if ((node->level & 1u) != 0u && g2_elog_sink.enabled != 0u && g2_elog_sink.output != NULL)
            g2_elog_sink.output(node->text, node->length);
        g2_log_transport_node_free((uint8_t *)node);
        taken++;
        g2_elog_stats.drained++;
    }
    return taken;
}

/* Append a retained crash record to /log/hardfault.txt; non-zero if one was found. */
uint32_t elog_crash_record_recover_448e2a(void)
{
    return crash_record_recover_to_file_47db02(log_dir);
}

void elog_async_ext_flieStore_Init(void)
{
    if (elog_crash_record_recover_448e2a() == 0u)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module_tag, source_file, file_store_init_fn, 0x3fau, crash_recovered);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x08000000u, crash_recovered_short, crash_recovered_short);
}
