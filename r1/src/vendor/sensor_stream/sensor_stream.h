#ifndef OPENR1_RECONSTRUCTED_SENSOR_STREAM_H
#define OPENR1_RECONSTRUCTED_SENSOR_STREAM_H

/*
 * Provenance banner
 * -----------------
 * Family:         unknown_sensor_stream_framework_candidate (Bravechip B210
 *                 "ChipletRing" platform generic named sensor-stream
 *                 subscription framework: object registry, listener
 *                 registration/unregistration, 1024 Hz software-timer list,
 *                 sample-buffer dispatch, and rate retiming).
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       r1/research/decompilation/application/decompiler-output.c
 *                 (all 32 Ghidra bodies) plus literal-pool and const-vtable
 *                 reads from the byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin
 *                 (state roots 0x2001A1B0/0x2001A1BC/0x2001A2AC/0x2001A2BC,
 *                 dispatch Thumb pointer 0x0008A1E1 at 0x00089ACC, "acc"/"temp"
 *                 pooled name bytes, provider vtables 0x0009A590/0x0009A5A8).
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities or
 *                 Bravechip source.  No upstream source, version, or license
 *                 exists for this family; reduction is owner-authorized per
 *                 docs/SOURCE-ADMISSION.md ("Owner-authorized full reduction
 *                 (2026-08-14)").
 *
 * Reduced stock functions (application image extents, end-exclusive):
 *
 *   0x0005D8FE..<0x0005D90D  16   list descriptor init (align4 stride)
 *   0x0005D90E..<0x0005D949  60   list node allocate + push front
 *   0x0005D986..<0x0005D997  18   list idle check (NULL or empty -> 1)
 *   0x0007D0D8..<0x0007D153  122  sample-buffer resample/copy helper
 *   0x000896F0..<0x000897B7  200  stream object create + registry insert
 *   0x000897E8..<0x0008984B  100  register listener by stream name
 *   0x00089890..<0x00089A60  464  listener registration / buffer + timer start
 *   0x00089B08..<0x0008A1AA  562  unregistration (4 noncontiguous ranges:
 *                                  0x89B08..0x89B60, 0x89C20..0x89CFA,
 *                                  0x8A068..0x8A13E, 0x8A180..0x8A1AA)
 *   0x00089D54..<0x00089D83  48   registry lookup by stream name
 *   0x00089D88..<0x00089D93  12   "acc" singleton create (sample 0xBC)
 *   0x00089D9C..<0x00089DF7  92   registry list insert (lazy descriptor init)
 *   0x00089E50..<0x00089E87  56   clamped triple store (sinks +0xCC)
 *   0x00089E8C..<0x00089EC3  56   clamped triple store (sinks +0xC0)
 *   0x00089EC8..<0x00089ED1  10   4-word descriptor store (sinks +0x00)
 *   0x00089ED8..<0x00089EE5  14   6-word descriptor store (sinks +0x10)
 *   0x0008A03C..<0x0008A04D  18   6-word descriptor store, 4th sign-extended
 *   0x0008A1AC..<0x0008A1B7  12   "temp" singleton create (sample 2)
 *   0x0008A1C4..<0x0008A1CF  12   ticks elapsed since argument
 *   0x0008A1D0..<0x0008A1DB  12   tick source (RAM hook, else CMSIS fallback)
 *   0x0008A1E0..<0x0008A310  422  timer dispatch (2 noncontiguous ranges:
 *                                  0x8A1E0..0x8A310, 0x89BA8..0x89C1E)
 *   0x0008A310..<0x0008A363  84   timer create, list front
 *   0x0008A368..<0x0008A3BB  84   timer create, list back
 *   0x0008A3C0..<0x0008A3EB  44   timer release (remove + free)
 *   0x0008A3F0..<0x0008A3FD  14   housekeeping enable + conditional kick
 *   0x0008A404..<0x0008A457  84   timer expiry processing
 *   0x0008A45C..<0x0008A539  222  timer poll (expiry scan + drift correction)
 *   0x0008A540..<0x0008A551  18   housekeeping kick (wake hook)
 *   0x0008A55C..<0x0008A57B  32   framework init (list init, enable, 1000-tick
 *                                  keep-alive timer with `bx lr` callback)
 *   0x0008A584..<0x0008A59D  26   timer stop (set flags bit 0)
 *   0x0008A5C0..<0x0008A5CF  16   object flags bit-0 insert (timer list side)
 *   0x0008A5D0..<0x0008A5E3  20   timer period store
 *   0x0008A5E4..<0x0008A5FB  24   saturating remaining-time computation
 *
 * The registry-family list walkers (0x0005D8E6/0x0005D8EE/0x0005D998/
 * 0x0005D94A), the FreeRTOS heap (0x000855A0/0x00095D48), the CMSIS tick
 * fallback (0x0007D28C), and the nRF_LOG/RTT diagnostic path are NOT part of
 * this family; they are explicit provider bindings here.
 *
 * Correlation doc: docs/correlation/SENSOR-STREAM-REDUCTION-CORRELATION.md.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Recovered status values (positive codes shared with the interlocked B210
 * platform families; compare the rtc_device reconstruction).  Most family
 * functions return pointers/bools instead and report bad arguments as
 * NULL/false. */
enum {
    SENSOR_STREAM_STATUS_OK = 0,
    SENSOR_STREAM_STATUS_BAD_ARGUMENT = 4
};

#define SENSOR_STREAM_NAME_MAX 8u          /* recovered inline name cap */
#define SENSOR_STREAM_OBJECT_BYTES 0x38u   /* recovered object allocation */
#define SENSOR_STREAM_LISTENER_PAYLOAD 0x18u
#define SENSOR_STREAM_TIMER_PAYLOAD 0x18u
#define SENSOR_STREAM_REGISTRY_PAYLOAD 8u
#define SENSOR_STREAM_TICK_HZ 1024u        /* period = 1024 / rate */
#define SENSOR_STREAM_DRIFT_WINDOW 499u    /* drift update when span > 499 */
#define SENSOR_STREAM_ZERO_TICK_LIMIT 100u /* recovered tick==0 counter cap */
#define SENSOR_STREAM_KEEPALIVE_PERIOD 1000u /* init's `bx lr` timer */

/* Object +0x28 flag bits (recovered). */
#define SENSOR_STREAM_OBJECT_FLAG_BACK_INSERT 0x01u /* timer to list back */
#define SENSOR_STREAM_OBJECT_FLAG_DISPATCH_ACTIVE 0x02u
#define SENSOR_STREAM_OBJECT_FLAG_PENDING_UNREGISTER 0x04u

/* Listener +0x14 flag bits (recovered).  Bit 0: deferred-delete mark.
 * Bits 1..15: per-sample rate accumulator (mode 1). */
#define SENSOR_STREAM_LISTENER_FLAG_DEFERRED 0x01u

/* Timer +0x14 flag bits (recovered).  Bit 0: stopped/idle.  Bit 1: active,
 * auto-release when the repeat count reaches zero. */
#define SENSOR_STREAM_TIMER_FLAG_STOPPED 0x01u
#define SENSOR_STREAM_TIMER_FLAG_ACTIVE 0x02u
#define SENSOR_STREAM_TIMER_REPEAT_FOREVER UINT32_C(0xFFFFFFFF)

/* Listener modes (recovered byte at listener +0x0E): 0 = batch delivery of a
 * full rate*sample_size chunk at buffer wrap; 1 = per-sample delivery with a
 * fractional rate accumulator.  Other values never fire. */
#define SENSOR_STREAM_MODE_BATCH 0u
#define SENSOR_STREAM_MODE_PER_SAMPLE 1u

/* Recovered shared list descriptor: +0x00 link stride (aligned payload
 * size), +0x04 head, +0x08 tail.  Links live at node + stride: previous at
 * +0, next at +4 (setters 0x00077E3C/0x00077E30, registry family). */
typedef struct {
    uint32_t stride;
    void *head;
    void *tail;
} sensor_stream_list_descriptor;

struct sensor_stream_object;
struct sensor_stream_listener;
struct sensor_stream_timer;
typedef struct sensor_stream sensor_stream;

/* Listener callback (recovered signature: (listener, data, length)).  `data`
 * points into the object's shared sample buffer. */
typedef void (*sensor_stream_listener_callback)(
    struct sensor_stream_listener *listener, const uint8_t *data,
    uint32_t length);

/* Recovered 0x20-byte listener node (0x18 payload + two link words).
 * Allocated by the list push; the node allocation IS the listener record. */
typedef struct sensor_stream_listener {
    struct sensor_stream_object *owner;   /* +0x00 */
    char name[SENSOR_STREAM_NAME_MAX];    /* +0x04 capped, tail not cleared */
    uint8_t reserved_0c;                  /* +0x0C */
    uint8_t rate;                         /* +0x0D requested rate ("ord") */
    uint8_t mode;                         /* +0x0E */
    uint8_t reserved_0f;                  /* +0x0F */
    sensor_stream_listener_callback callback; /* +0x10 */
    uint16_t flags;                       /* +0x14 */
    uint16_t reserved_16;                 /* +0x16 */
    struct sensor_stream_listener *link_previous; /* +0x18 (stride +0) */
    struct sensor_stream_listener *link_next;     /* +0x1C (stride +4) */
} sensor_stream_listener;

/* Timer callback.  Stock stores the raw dispatch address and invokes it with
 * the timer node; the reconstruction passes the explicit framework state as
 * the first argument (observable behavior unchanged). */
typedef void (*sensor_stream_timer_callback)(
    sensor_stream *framework, struct sensor_stream_timer *timer);

/* Recovered 0x20-byte timer node (0x18 payload + two link words). */
typedef struct sensor_stream_timer {
    uint32_t period;                      /* +0x00 ticks between expiries */
    uint32_t last;                        /* +0x04 tick of last expiry */
    sensor_stream_timer_callback callback;/* +0x08 */
    void *context;                        /* +0x0C stream object for dispatch */
    uint32_t repeat;                      /* +0x10 0xFFFFFFFF = forever */
    uint32_t flags;                       /* +0x14 */
    struct sensor_stream_timer *link_previous; /* +0x18 */
    struct sensor_stream_timer *link_next;     /* +0x1C */
} sensor_stream_timer;

/* Recovered provider operations vtable (const in flash; +0x00 open, +0x04
 * close, +0x08 read).  All hooks receive the object's stored context. */
typedef void (*sensor_stream_provider_open_fn)(void *context);
typedef void (*sensor_stream_provider_close_fn)(void *context);
typedef uint32_t (*sensor_stream_provider_read_fn)(uint8_t *destination,
                                                   uint32_t length,
                                                   void *context);
typedef struct {
    sensor_stream_provider_open_fn open;   /* +0x00 optional */
    sensor_stream_provider_close_fn close; /* +0x04 optional */
    sensor_stream_provider_read_fn read;   /* +0x08 mandatory for dispatch */
} sensor_stream_provider_ops;

/* Recovered 0x38-byte stream object. */
typedef struct sensor_stream_object {
    char name[SENSOR_STREAM_NAME_MAX];    /* +0x00 inline, NUL-padded */
    uint32_t reserved_08;                 /* +0x08 */
    const sensor_stream_provider_ops *provider; /* +0x0C */
    uint8_t rate;                         /* +0x10 current aggregate rate */
    uint8_t reserved_11[3];               /* +0x11 */
    uint8_t *sample_buffer;               /* +0x14 rate*sample_size*2 bytes */
    uint32_t cursor;                      /* +0x18 write cursor / valid bytes */
    uint16_t sample_size;                 /* +0x1C */
    uint16_t reserved_1e;                 /* +0x1E */
    sensor_stream_timer *timer;           /* +0x20 */
    void *context;                        /* +0x24 provider hook context */
    uint8_t flags;                        /* +0x28 */
    uint8_t reserved_29[3];               /* +0x29 */
    sensor_stream_list_descriptor listeners; /* +0x2C */
} sensor_stream_object;

/* Recovered 0x10-byte registry node (8-byte payload + links); payload word 0
 * is never initialized by stock. */
typedef struct {
    uint32_t reserved_00;                 /* +0x00 */
    sensor_stream_object *object;         /* +0x04 */
    void *link_previous;                  /* +0x08 */
    void *link_next;                      /* +0x0C */
} sensor_stream_registry_node;

/* Recovered housekeeping block (stock 0x2001A2BC): timer list descriptor
 * plus scheduler bookkeeping. */
typedef void (*sensor_stream_wake_fn)(void *context);
typedef struct {
    sensor_stream_list_descriptor timers; /* +0x00 */
    uint8_t enabled;                      /* +0x0C */
    uint8_t drift_correction;             /* +0x0D 100 - busy% (0 when >= 101) */
    uint8_t released;                     /* +0x0E release-during-poll mark */
    uint8_t created;                      /* +0x0F create-during-poll mark */
    uint32_t next_wakeup;                 /* +0x10 minimum remaining ticks */
    uint8_t poll_active;                  /* +0x14 reentrancy guard */
    uint8_t reserved_15[3];               /* +0x15 */
    uint32_t reserved_18;                 /* +0x18 */
    uint32_t drift_accumulator;           /* +0x1C busy ticks in window */
    uint32_t drift_mark;                  /* +0x20 window start tick */
    uint32_t zero_tick_counter;           /* +0x24 tick==0 quirk counter */
    sensor_stream_wake_fn wake;           /* +0x28 optional wake hook */
    void *wake_context;                   /* +0x2C */
} sensor_stream_housekeeping;

/* Recovered sink staging block (stock 0x2001A1BC..0x2001A293).  These are
 * plain staging stores bound by R1 product code as generic callbacks. */
typedef struct {
    uint32_t descriptor4[4];       /* +0x00 stock 0x2001A1BC (0x00089EC8) */
    uint32_t descriptor6[6];       /* +0x10 stock 0x2001A1CC (0x00089ED8) */
    uint32_t descriptor6s[6];      /* +0x28 stock 0x2001A1E4 (0x0008A03C) */
    uint32_t reserved_40[32];      /* +0x40..+0xBF */
    int32_t clamped_primary[3];    /* +0xC0..+0xC8 (0x00089E8C) */
    int32_t clamped_secondary[3];  /* +0xCC..+0xD4 (0x00089E50) */
} sensor_stream_sink_block;

/* Provider bindings.  Every dependency the stock code called directly is an
 * explicit, bindable seam; an unbound mandatory provider fails explicitly
 * (NULL / false / no-op) instead of faulting.
 *
 *   allocate/free                FreeRTOS heap (0x000855A0 / 0x00095D48)
 *   list_first/next/remove/push_back_allocate
 *                                generic-registry family list walkers
 *                                (0x0005D8E6 / 0x0005D8EE / 0x0005D998 /
 *                                0x0005D94A; still blocked)
 *   tick_fallback                CMSIS-FreeRTOS tick (0x0007D28C), used when
 *                                no RAM tick hook is installed
 *   diagnostic                   optional nRF_LOG/RTT path; receives the
 *                                recovered message, first string argument
 *                                (or NULL), and first integer argument
 *   fault                        optional app fault path for the cases where
 *                                stock hangs in a privileged loop */
typedef void *(*sensor_stream_alloc_fn)(uint32_t size);
typedef void (*sensor_stream_free_fn)(void *pointer);
typedef void *(*sensor_stream_list_first_fn)(
    sensor_stream_list_descriptor *descriptor);
typedef void *(*sensor_stream_list_next_fn)(
    sensor_stream_list_descriptor *descriptor, void *node);
typedef void (*sensor_stream_list_remove_fn)(
    sensor_stream_list_descriptor *descriptor, void *node);
typedef void *(*sensor_stream_list_push_back_allocate_fn)(
    sensor_stream_list_descriptor *descriptor);
typedef uint32_t (*sensor_stream_tick_fn)(void);
typedef void (*sensor_stream_diagnostic_fn)(const char *message,
                                            const char *detail,
                                            uint32_t value);
typedef void (*sensor_stream_fault_fn)(void);

typedef struct {
    sensor_stream_alloc_fn allocate;
    sensor_stream_free_fn free;
    sensor_stream_list_first_fn list_first;
    sensor_stream_list_next_fn list_next;
    sensor_stream_list_remove_fn list_remove;
    sensor_stream_list_push_back_allocate_fn list_push_back_allocate;
    sensor_stream_tick_fn tick_fallback;
    sensor_stream_diagnostic_fn diagnostic; /* optional */
    sensor_stream_fault_fn fault;           /* optional */
} sensor_stream_providers;

/* Explicit framework state.  Field order mirrors the recovered RAM roots:
 * registry descriptor at stock 0x2001A1B0, sink block at 0x2001A1BC, tick
 * hook word at 0x2001A2AC+8, housekeeping at 0x2001A2BC. */
struct sensor_stream {
    sensor_stream_list_descriptor registry;
    sensor_stream_sink_block sinks;
    sensor_stream_tick_fn tick_hook; /* stock: RAM word at 0x2001A2AC+8 */
    sensor_stream_housekeeping housekeeping;
    sensor_stream_providers providers;
    const sensor_stream_provider_ops *acc_provider;  /* stock const 0x9A590 */
    const sensor_stream_provider_ops *temp_provider; /* stock const 0x9A5A8 */
};

/* Zeroes the state, binds providers, then runs the recovered 0x0008A55C
 * sequence: timer-list descriptor init (stride 0x18), housekeeping enable
 * with kick, and a 1000-tick keep-alive timer whose stock callback is the
 * `bx lr` stub at 0x0008A558.  Returns SENSOR_STREAM_STATUS_BAD_ARGUMENT
 * when the keep-alive timer cannot be created (stock hangs). */
uint32_t sensor_stream_initialize(sensor_stream *framework,
                                  const sensor_stream_providers *providers);

/* Binds the provider vtables used by the two singleton create wrappers
 * (stock: const vtables 0x0009A590 "acc" -> R1 motion adapter hooks and
 * 0x0009A5A8 "temp" -> R1 product hooks). */
void sensor_stream_bind_singleton_providers(
    sensor_stream *framework, const sensor_stream_provider_ops *acc_provider,
    const sensor_stream_provider_ops *temp_provider);

/* Installs the RAM tick hook (stock: writable word at 0x2001A2AC+8; when
 * non-NULL it overrides the CMSIS fallback). */
void sensor_stream_set_tick_hook(sensor_stream *framework,
                                 sensor_stream_tick_fn hook);

/* Installs the housekeeping wake hook (stock: words at 0x2001A2BC+0x28/2C,
 * written outside this family). */
void sensor_stream_set_wake_callback(sensor_stream *framework,
                                     sensor_stream_wake_fn wake,
                                     void *context);

/* 0x0005D8FE: descriptor init; stride = (payload + 3) & ~3, head/tail NULL. */
void sensor_stream_list_descriptor_init(
    sensor_stream_list_descriptor *descriptor, uint32_t payload_size);

/* 0x0005D90E: allocate stride+8 node and push front; returns the node or
 * NULL on allocation failure.  The two one-instruction link stores (stock
 * 0x00077E30/0x00077E3C, registry family) are inlined; no registry-family
 * function is reconstructed as a callable unit. */
void *sensor_stream_list_push_front_allocate(
    sensor_stream *framework, sensor_stream_list_descriptor *descriptor);

/* 0x0005D986: idle check; true when the descriptor is NULL or both link
 * heads are NULL. */
bool sensor_stream_list_idle(const sensor_stream_list_descriptor *descriptor);

/* 0x0007D0D8: nearest-neighbour resample/copy.  Copies min(target,
 * round(min(valid_bytes/element, source) * target / source)) elements,
 * source index (i * source) / target clamped to valid-1, element-bytes each.
 * Returns bytes copied; 0 for any NULL/zero argument. */
uint32_t sensor_stream_resample_copy(const uint8_t *source,
                                     uint32_t source_samples,
                                     uint32_t source_bytes,
                                     uint8_t *destination,
                                     uint32_t target_samples,
                                     uint32_t element_bytes);

/* 0x000896F0: create a stream object.  Stock hard-faults on NULL name, NULL
 * provider, or zero sample size; the reconstruction calls the optional fault
 * hook and returns NULL.  On allocation failure logs "obj malloc fail" and
 * returns NULL.  Registry-insert failure is logged but the object is still
 * returned (recovered quirk). */
sensor_stream_object *sensor_stream_object_create(
    sensor_stream *framework, const char *name, uint32_t sample_size,
    const sensor_stream_provider_ops *provider, void *context);

/* 0x00089D9C: insert into the registry list (lazy descriptor init with
 * stride 8).  Returns false (+ "list insert fail" diagnostic) when the
 * push-back allocation fails or the provider is unbound. */
bool sensor_stream_object_insert(sensor_stream *framework,
                                 sensor_stream_object *object);

/* 0x00089D54: registry lookup by stream name; NULL when not found, when the
 * registry is uninitialized (stride 0, recovered guard), or when the list
 * providers are unbound. */
sensor_stream_object *sensor_stream_object_lookup(sensor_stream *framework,
                                                  const char *name);

/* 0x000897E8: resolve stream by name then register; NULL (+ "register not
 * find obj:%s") when the stream is unknown. */
sensor_stream_listener *sensor_stream_register_by_name(
    sensor_stream *framework, const char *stream_name,
    const char *listener_name, sensor_stream_listener_callback callback,
    uint32_t rate, uint8_t mode);

/* 0x00089890: register a listener.  Rate ("ord") is capped at 1 with the
 * recovered "only support 1 ord" diagnostic.  The first listener sets the
 * object rate, allocates the rate*sample_size*2 buffer, invokes the optional
 * provider open hook, and starts the timer at 1024/rate ticks (front or back
 * insertion per object flags bit 0).  A later higher-rate listener resizes
 * the buffer through the resample helper and retimes the timer.  NULL
 * object/name hard-faults in stock; the reconstruction calls the fault hook
 * and returns NULL. */
sensor_stream_listener *sensor_stream_listener_register(
    sensor_stream *framework, sensor_stream_object *object,
    const char *listener_name, sensor_stream_listener_callback callback,
    uint32_t rate, uint8_t mode);

/* 0x00089B08: unregister by stream name + exact listener pointer.  Unknown
 * stream logs "unregister not find obj:%s"; unknown listener logs "%s not
 * found in %s, skip unregister".  During dispatch the listener is marked
 * (flags bit 0) and removal is deferred (object flags bit 2).  Otherwise the
 * listener is removed immediately; remaining listeners shrink the buffer to
 * the maximum remaining rate and retime the timer, and an empty list frees
 * the buffer, releases the timer, and invokes the optional provider close
 * hook with the stored context. */
void sensor_stream_listener_unregister(sensor_stream *framework,
                                       const char *stream_name,
                                       sensor_stream_listener *listener);

/* 0x0008A1E0: timer dispatch callback.  Validates provider read hook,
 * buffer, rate, and sample size; resets a stale cursor; reads one sample at
 * the cursor; advances/wraps the cursor; walks the listener list under
 * dispatch flag bit 1 (skipping deferred-delete entries); delivers per mode;
 * then clears bit 1 and, when pending-unregister bit 2 is set, removes the
 * marked listeners and rebalances or releases the stream. */
void sensor_stream_timer_dispatch(sensor_stream *framework,
                                  sensor_stream_timer *timer);

/* 0x0008A310 / 0x0008A368: create a timer at the list front/back.  Repeat
 * starts at 0xFFFFFFFF (forever), flags gain bit 1, the creation tick is
 * recorded, the created mark is set, and the housekeeping is kicked.  Stock
 * hard-faults on allocation failure; the reconstruction calls the fault hook
 * and returns NULL. */
sensor_stream_timer *sensor_stream_timer_create_front(
    sensor_stream *framework, sensor_stream_timer_callback callback,
    uint32_t period, void *context);
sensor_stream_timer *sensor_stream_timer_create_back(
    sensor_stream *framework, sensor_stream_timer_callback callback,
    uint32_t period, void *context);

/* 0x0008A3C0: remove the timer from the list, set the released mark, free. */
void sensor_stream_timer_release(sensor_stream *framework,
                                 sensor_stream_timer *timer);

/* 0x0008A3F0: store the enable byte; kick when nonzero. */
void sensor_stream_housekeeping_enable(sensor_stream *framework,
                                       uint32_t enable);

/* 0x0008A404: expiry processing.  Returns false when the timer is stopped.
 * On expiry the repeat count decrements when positive, the expiry tick is
 * recorded, and the callback runs unless the repeat count was already zero.
 * An exhausted timer (repeat 0) is released when flags bit 1 is set, else
 * stopped (bit 0), unless a release already happened this pass. */
bool sensor_stream_timer_expire(sensor_stream *framework,
                                sensor_stream_timer *timer);

/* 0x0008A45C: poll the timer list.  Returns 1 when disabled or re-entered;
 * otherwise processes expiries (restarting the scan when a callback created
 * or released a timer), computes the minimum remaining time across active
 * timers, accumulates busy ticks, every >499-tick window stores the
 * 100 - busy% drift byte, and returns the minimum (0xFFFFFFFF when no active
 * timer). */
uint32_t sensor_stream_timer_poll(sensor_stream *framework);

/* 0x0008A540: clear next-wakeup and invoke the optional wake hook. */
void sensor_stream_housekeeping_kick(sensor_stream *framework);

/* 0x0008A584: mark the timer stopped (flags bit 0). */
void sensor_stream_timer_stop(sensor_stream *framework,
                              sensor_stream_timer *timer);

/* 0x0008A5C0: object flags bit-0 insert (selects timer list side).  Stock
 * silently ignores a NULL object; kept. */
void sensor_stream_object_set_back_insert(sensor_stream *framework,
                                          sensor_stream_object *object,
                                          uint32_t value);

/* 0x0008A5D0: store the timer period. */
void sensor_stream_timer_set_period(sensor_stream *framework,
                                    sensor_stream_timer *timer,
                                    uint32_t period);

/* 0x0008A5E4: remaining ticks; 0 once elapsed >= period (saturating). */
uint32_t sensor_stream_timer_remaining(sensor_stream *framework,
                                       const sensor_stream_timer *timer);

/* 0x0008A1C4: ticks elapsed since `then` (32-bit wrap arithmetic). */
uint32_t sensor_stream_ticks_elapsed(sensor_stream *framework, uint32_t then);

/* 0x0008A1D0: tick source; RAM hook when installed, else the bound CMSIS
 * fallback, else 0 (explicit degradation; stock always linked the fallback). */
uint32_t sensor_stream_tick_now(sensor_stream *framework);

/* 0x00089D88 / 0x0008A1AC: fixed-configuration singleton creates for "acc"
 * (sample size 0xBC) and "temp" (sample size 2).  The stock vtables belong
 * to the R1 motion adapter and R1 product code; bind them through
 * sensor_stream_bind_singleton_providers.  NULL when unbound. */
sensor_stream_object *sensor_stream_acc_object_create(
    sensor_stream *framework);
sensor_stream_object *sensor_stream_temp_object_create(
    sensor_stream *framework);

/* 0x00089EC8 / 0x00089ED8 / 0x0008A03C: staging descriptor stores into the
 * sink block; the 0x8A03C variant sign-extends its fourth word from int8. */
void sensor_stream_sink_store4(sensor_stream *framework, uint32_t word0,
                               uint32_t word1, uint32_t word2, uint32_t word3);
void sensor_stream_sink_store6(sensor_stream *framework, uint32_t word0,
                               uint32_t word1, uint32_t word2, uint32_t word3,
                               uint32_t word4, uint32_t word5);
void sensor_stream_sink_store6_sign_extended(
    sensor_stream *framework, uint32_t word0, uint32_t word1, uint32_t word2,
    uint32_t word3, uint32_t word4, uint32_t word5);

/* 0x00089E8C / 0x00089E50: clamped triple stores (max(0, *source)) into the
 * sink block primary (+0xC0) and secondary (+0xCC) triples. */
void sensor_stream_sink_triple_clamped_primary(sensor_stream *framework,
                                               const int32_t *first,
                                               const int32_t *second,
                                               const int32_t *third);
void sensor_stream_sink_triple_clamped_secondary(sensor_stream *framework,
                                                 const int32_t *first,
                                                 const int32_t *second,
                                                 const int32_t *third);

#endif
