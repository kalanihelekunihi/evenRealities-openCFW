#ifndef OPENR1_RECONSTRUCTED_GENERIC_DEVICE_REGISTRY_H
#define OPENR1_RECONSTRUCTED_GENERIC_DEVICE_REGISTRY_H

/*
 * Provenance banner
 * -----------------
 * Family:         unknown_generic_device_registry_candidate (Bravechip B210
 *                 "ChipletRing" platform name-based device registry, its
 *                 operation-table dispatchers, the companion offset-based
 *                 intrusive subscriber list, and the static request-block
 *                 client wrappers that dispatch through the registry).
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       r1/research/decompilation/application/decompiler-output.c
 *                 (Ghidra bodies for the original 40 inventory entries)
 *                 cross-checked against
 *                 fresh Capstone/GNU objdump Thumb disassembly of the
 *                 byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin
 *                 (dispatch tail-calls, subscriber-list argument recovery,
 *                 and every literal-pool state root were re-verified against
 *                 the binary because Ghidra could not recover them).
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities or
 *                 Bravechip source.  No upstream source, version, or license
 *                 exists for this family; reduction is owner-authorized per
 *                 docs/SOURCE-ADMISSION.md ("Owner-authorized full reduction
 *                 (2026-08-14)").
 *
 * Reduced stock functions (application image extents, end-exclusive):
 *
 *   0x00044BE0..<0x00044BEC  12   arg reorder + command-0xAE read veneer
 *   0x000509BC..<0x000509DB  32   static request fill + slot 0x14 dispatch
 *   0x00050ABC..<0x00050AD9  30   record-B slot 0x08 + gated slot 0x20 cycle
 *   0x00050DF0..<0x00050E17  40   zeroed 0x40 time block + slot 0x14 dispatch
 *   0x00050F34..<0x00050F57  36   request block A slot 0x10, inverted return
 *   0x00050F5C..<0x00050F81  38   request block A slot 0x14, inverted return
 *   0x00050510..<0x0005052E  30   bus block fill + slot 0x10 dispatch
 *   0x00050534..<0x00050554  32   bus block fill + slot 0x14 dispatch
 *   0x0005B2F8..<0x0005B327  48   flash sector-erase loop (8-bit counter)
 *   0x0005D1EA..<0x0005D1F3  52*  bus-read caller composition
 *   0x0005D1F4..<0x0005D21D  42   bus read-modify-write of register bit 0
 *   0x0005D21E..<0x0005D241  68*  bus-write caller composition; delay(5)
 *   0x0005D8CC..<0x0005D8E5  26   BKDR-style byte hash (multiplier 0x83)
 *   0x0005D8E6..<0x0005D8ED  8    guarded list-head getter
 *   0x0005D8EE..<0x0005D8F5  8    unguarded offset-list next getter
 *   0x0005D8F6..<0x0005D8FD  8    guarded list-tail getter
 *   0x0005D94A..<0x0005D985  60   pool-allocate node + append at tail
 *   0x0005D998..<0x0005D9FF  104  offset-list node remove (no free)
 *   0x0005DA00..<0x0005DA2B  44   mutex-guarded subscriber port-op pair
 *   0x0005DA30..<0x0005DA45  22   current flagged subscriber's task getter
 *   0x0005DB14..<0x0005DBB1  158  subscriber insert (name cap 7, task bind)
 *   0x0005DBBC..<0x0005DBE9  46   subscriber flag clear + tick refresh
 *   0x0005DBEA..<0x0005DC05  28   subscriber flag bit1 set
 *   0x0005E1FC..<0x0005E221  38   single 0x1000 sector erase, sector < 2
 *   0x0006F90E..<0x0006F91F  18   ops-table veneer -> 0x000509BC, return 1
 *   0x000734E8..<0x00073577  144  enabled-gated module sync scan + flush
 *   0x00077214..<0x0007721B  8    slot 0x0C dispatch thunk
 *   0x00077E30..<0x00077E3B  12   offset-list next store
 *   0x00077E3C..<0x00077E45  10   offset-list prev store
 *   0x00085CBA..<0x00085CCB  18   dispatcher slot 0x0C (missing -> 6)
 *   0x00085CCC..<0x00085CDD  18   dispatcher slot 0x18 (missing -> 7)
 *   0x00085CE0..<0x00085D01  34   registry find by name (strcmp walk)
 *   0x00085D08..<0x00085D19  18   dispatcher slot 0x00 (missing -> 5)
 *   0x00085D1A..<0x00085D2B  18   dispatcher slot 0x08 (missing -> 5)
 *   0x00085D2C..<0x00085D45  26   dispatcher slot 0x10 (missing -> 2)
 *   0x00085D46..<0x00085D57  18   dispatcher slot 0x20 (missing -> 9)
 *   0x00085D58..<0x00085DA1  74   registry register (dup reject, append)
 *   0x00085DA8..<0x00085DC1  26   dispatcher slot 0x14 (missing -> 3)
 *   0x00087AF8..<0x00087B15  30   3-word message pack + slot 0x10 dispatch
 *   0x0009338C..<0x000933AF  36   request block B slot 0x10, inverted return
 *   0x00096FB0..<0x00096FD5  38   string/length message + slot 0x14 dispatch
 *   0x00097730..<0x00097741  18   registry mutex acquire (0xFFFFFFFF wait)
 *   0x00097748..<0x00097755  14   registry mutex release
 *
 *   * The legacy Ghidra inventory assigned noncontiguous 52/68-byte extents
 *     to 0x0005D1EA/0x0005D21E.  The three tail-called helpers at
 *     0x00044BE0, 0x00050510, and 0x00050534 are now authenticated as exact
 *     manual supplements and implemented as separate C functions.
 *
 * Correlation doc: docs/correlation/GENERIC-DEVICE-REGISTRY-REDUCTION-CORRELATION.md.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Recovered positive status scheme.  The registry family owns codes
 * {1,2,3,5,6,7,9} (null device / per-slot missing operation), interlocked
 * gap-free with the software-TWI family codes {4,8,10,11,12} into one
 * 0..12 enum (see the boundary doc).  0 is success. */
enum {
    GENERIC_DEVICE_REGISTRY_STATUS_OK = 0,
    GENERIC_DEVICE_REGISTRY_STATUS_DEVICE_NULL = 1,
    GENERIC_DEVICE_REGISTRY_STATUS_SLOT_10_MISSING = 2,
    GENERIC_DEVICE_REGISTRY_STATUS_SLOT_14_MISSING = 3,
    GENERIC_DEVICE_REGISTRY_STATUS_SLOT_00_MISSING = 5,
    GENERIC_DEVICE_REGISTRY_STATUS_SLOT_08_MISSING = 5,
    GENERIC_DEVICE_REGISTRY_STATUS_SLOT_0C_MISSING = 6,
    GENERIC_DEVICE_REGISTRY_STATUS_SLOT_18_MISSING = 7,
    GENERIC_DEVICE_REGISTRY_STATUS_SLOT_20_MISSING = 9
};

#define GENERIC_DEVICE_REGISTRY_OPS_SLOTS 9u /* nine words, 0x00..0x20 */
#define GENERIC_DEVICE_REGISTRY_SUBSCRIBER_LINK_OFFSET 28u /* links at node + 28 */
#define GENERIC_DEVICE_REGISTRY_SUBSCRIBER_NAME_MAX 7u
#define GENERIC_DEVICE_REGISTRY_SECTOR_SIZE 0x1000u
#define GENERIC_DEVICE_REGISTRY_FLASH_BASE_WORD 13u /* record word at +0x34 */
#define GENERIC_DEVICE_REGISTRY_BUS_COMMAND 0xAEu
#define GENERIC_DEVICE_REGISTRY_BUS_DELAY_MS 5u /* Nordic delay argument */
#define GENERIC_DEVICE_REGISTRY_BUS_RMW_REGISTER 0x0Du
#define GENERIC_DEVICE_REGISTRY_MUTEX_WAIT_FOREVER UINT32_C(0xFFFFFFFF)

struct generic_device_registry_device;

/* Operation-table entry.  The stock dispatchers are tail calls: the device
 * record stays in r0 and the caller's r1..r3 pass through untouched, so an
 * operation receives (device, arg1, arg2, arg3). */
typedef uint32_t (*generic_device_registry_operation)(
    struct generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3);

/* Recovered nine-word operation table (stock: slots at byte offsets
 * 0x00, 0x04, 0x08, 0x0C, 0x10, 0x14, 0x18, 0x1C, 0x20; slots 0x04 and
 * 0x1C have no recovered dispatcher).  Slot names are intentionally not
 * guessed (boundary doc). */
typedef struct {
    generic_device_registry_operation slot[GENERIC_DEVICE_REGISTRY_OPS_SLOTS];
} generic_device_registry_ops;

/* Recovered 24-byte registry record:
 *   +0x00 non-null device name, +0x04 non-null operation table,
 *   +0x08..+0x13 private words, +0x14 next record. */
typedef struct generic_device_registry_device {
    const char *name;                            /* +0x00 */
    const generic_device_registry_ops *ops;      /* +0x04 */
    uintptr_t priv[3];                           /* +0x08..+0x13 */
    struct generic_device_registry_device *next; /* +0x14 */
} generic_device_registry_device;

enum {
    GENERIC_DEVICE_REGISTRY_SLOT_00 = 0, /* +0x00 */
    GENERIC_DEVICE_REGISTRY_SLOT_08 = 2, /* +0x08 */
    GENERIC_DEVICE_REGISTRY_SLOT_0C = 3, /* +0x0C */
    GENERIC_DEVICE_REGISTRY_SLOT_10 = 4, /* +0x10 */
    GENERIC_DEVICE_REGISTRY_SLOT_14 = 5, /* +0x14 */
    GENERIC_DEVICE_REGISTRY_SLOT_18 = 6, /* +0x18 */
    GENERIC_DEVICE_REGISTRY_SLOT_20 = 8  /* +0x20 */
};

/* Recovered offset-based intrusive doubly-linked-list descriptor: nodes are
 * addressed as absolute pointers and the link pair lives at byte offset
 * link_offset inside each node (prev at +0, next at +4 relative to it).
 * Stock: list descriptor at 0x20015408 with link_offset 28. */
typedef struct {
    uintptr_t link_offset; /* +0x00 byte offset of the link pair in a node */
    void *head;            /* +0x04 */
    void *tail;            /* +0x08 */
} generic_device_registry_link_list;

/* Recovered subscriber-registry root (stock 0x20015404): the port object
 * whose +0x08 word is the (operation, word) port call, then the embedded
 * list descriptor. */
typedef struct {
    void *port_object;                          /* +0x00 */
    generic_device_registry_link_list list;     /* +0x04 */
} generic_device_registry_subscriber_root;

/* Recovered 0x24-byte subscriber node (0x1C data + 8-byte link pair):
 *   +0x00 root back-pointer, +0x04 current-task handle, +0x08 name[8]
 *   (7 characters + NUL), +0x10 flags (bit0 set by the non-family poller,
 *   bit1 disable), +0x14 port tick word, +0x18 subscribe parameter,
 *   +0x1C prev, +0x20 next. */
typedef struct generic_device_registry_subscriber {
    generic_device_registry_subscriber_root *root; /* +0x00 */
    void *task;                                    /* +0x04 */
    char name[8];                                  /* +0x08 */
    uint32_t flags;                                /* +0x10 */
    uint32_t tick;                                 /* +0x14 */
    uintptr_t parameter;                           /* +0x18 */
    uintptr_t prev;                                /* +0x1C (link_offset 28) */
    uintptr_t next;                                /* +0x20 */
} generic_device_registry_subscriber;

/* Recovered static request block carried by dispatch slots 0x10/0x14
 * (boundary doc: {u8 cmd = 0xAE, u16 reg, buf, len, data, len2}).  Not all
 * writers fill every field; each wrapper documents what it writes. */
typedef struct {
    uint8_t command;      /* +0x00 */
    uint8_t reserved_01;
    uint16_t code;        /* +0x02 register/command word */
    uintptr_t buffer;     /* +0x04 */
    uint16_t length;      /* +0x08 */
    uint8_t reserved_0a[2];
    uintptr_t data;       /* +0x0C */
    uint16_t length2;     /* +0x10 */
    uint8_t reserved_12[2];
} generic_device_registry_request_block; /* 0x14 bytes */

/* Recovered 0x40-byte time request block (0x00050DF0): zeroed on the stack,
 * epoch at +0x2C, uint16 UTC offset at +0x30; matches the rtc_device
 * family's shared time block. */
typedef struct {
    uint8_t reserved_00[0x2C];
    uint32_t epoch_seconds;      /* +0x2C */
    uint16_t utc_offset_minutes; /* +0x30 */
    uint8_t reserved_32[0x0E];
} generic_device_registry_time_block; /* 0x40 bytes */

/* Recovered flash-client operation table slice: erase at +0x30, called as
 * erase(address, 0x1000). */
typedef void (*generic_device_registry_erase_operation)(uint32_t address,
                                                        uint32_t length);
typedef struct {
    uintptr_t reserved[12];                            /* +0x00..+0x2C */
    generic_device_registry_erase_operation erase;     /* +0x30 */
} generic_device_registry_flash_ops;

/* Recovered sync-flush table slice (0x000734E8): word at +0x18 called with
 * (1, 0) after the module scan. */
typedef struct {
    uintptr_t reserved[6]; /* +0x00..+0x14 */
    uint32_t (*flush)(uintptr_t arg1, uintptr_t arg2); /* +0x18 */
} generic_device_registry_sync_ops;

/* Provider bindings.  Every dependency the stock code called directly is an
 * explicit, bindable seam; an unbound mandatory provider fails explicitly
 * (per-function failure value) instead of faulting.  Stock attribution:
 *   allocate        0x000855A0  FreeRTOS heap_4 pvPortMalloc
 *   current_task    0x0009879C  xTaskGetCurrentTaskHandle (Nordic port)
 *   mutex_acquire   0x0007D488  CMSIS-FreeRTOS osMutexAcquire
 *   mutex_release   0x0007D536  CMSIS-FreeRTOS osMutexRelease
 *   port_op         *(object+8) subscriber port call f(operation, word)
 *   delay_ms        0x00078510  Nordic busy-wait delay (arg 5)
 *   sector_count    0x0008FE14  R1 flash geometry (record +0x38 >> 12)
 *   sync_one_class  0x00091780  R1 per-module sync, (record, index) -> status
 *   log_level       0x000914EC  R1 log-level flags getter
 *   log_r1          0x00091638  R1 logger (0x0C800000 marker form)
 *   log_nordic      0x000799D6  Nordic/SEGGER logger (packed-id form) */
typedef void *(*generic_device_registry_alloc_fn)(size_t size);
typedef void *(*generic_device_registry_current_task_fn)(void);
typedef uint32_t (*generic_device_registry_mutex_acquire_fn)(void *mutex,
                                                             uint32_t wait);
typedef void (*generic_device_registry_mutex_release_fn)(void *mutex);
typedef uint32_t (*generic_device_registry_port_op_fn)(uintptr_t operation,
                                                       uint32_t *word);
typedef void (*generic_device_registry_delay_fn)(uint32_t milliseconds);
typedef uint32_t (*generic_device_registry_sector_count_fn)(void);
typedef uint32_t (*generic_device_registry_sync_one_class_fn)(
    const uint8_t *module_record, uint16_t index);
typedef uint32_t (*generic_device_registry_log_level_fn)(void);
typedef void (*generic_device_registry_log_r1_fn)(uint32_t marker,
                                                  const char *prefix,
                                                  const char *format,
                                                  const char *name,
                                                  uint32_t status);
typedef void (*generic_device_registry_log_nordic_fn)(uint32_t packed_id,
                                                      const char *format,
                                                      const char *name,
                                                      uint32_t status);

typedef struct {
    generic_device_registry_alloc_fn allocate;
    generic_device_registry_current_task_fn current_task;
    generic_device_registry_mutex_acquire_fn mutex_acquire;
    generic_device_registry_mutex_release_fn mutex_release;
    generic_device_registry_port_op_fn port_op;
    generic_device_registry_delay_fn delay_ms;
    generic_device_registry_sector_count_fn sector_count;
    generic_device_registry_sync_one_class_fn sync_one_class;
    generic_device_registry_log_level_fn log_level;
    generic_device_registry_log_r1_fn log_r1;
    generic_device_registry_log_nordic_fn log_nordic;
} generic_device_registry_providers;

/* R1 board wiring recovered as fixed .bss slots.  Stock addresses are
 * noted per field; the reconstruction keeps them as bindable pointers. */
typedef struct {
    generic_device_registry_device *ctrl_device;      /* 0x200076CC: 0x000509BC/0x0006F90E target */
    generic_device_registry_device *ctrl_record_b;    /* 0x200076D0: 0x00050ABC target */
    uintptr_t ctrl_flag;                              /* 0x200076D4: 0x00050ABC slot 0x20 gate */
    generic_device_registry_device *time_device;      /* 0x20007380: 0x00050DF0 target (`sys rtc`) */
    generic_device_registry_device *request_device_a; /* 0x200076F8: 0x00050F34/0x00050F5C target */
    generic_device_registry_device *bus_device;       /* 0x2000683C: 0x0005D1EA/0x0005D21E target */
    generic_device_registry_device *request_device_b; /* 0x200067FC: 0x0009338C target */
    generic_device_registry_device *message_device;   /* 0x200077C0: 0x00087AF8/0x00096FB0 target */
    generic_device_registry_device *slot_0c_device;   /* 0x20006838: 0x00077214 target */
    const uint32_t *flash_all_record;    /* 0x200067B4 +4: base at word 13 (+0x34) */
    const generic_device_registry_flash_ops *flash_all_ops; /* +8 */
    const uint32_t *flash_sector_record; /* 0x20006908 +4 */
    const generic_device_registry_flash_ops *flash_sector_ops; /* +8 */
    uint8_t flash_sector_ready;          /* 0x20006908 +0 flag byte */
    const generic_device_registry_sync_ops *sync_ops;  /* 0x20006970 +4 */
    const uint8_t *const *module_begin;  /* 0x20007DE8 module table begin */
    const uint8_t *const *module_end;    /* 0x20007E04 module table end */
    void *subscriber_mutex;              /* 0x20016738 CMSIS mutex handle */
    uint8_t subscriber_initialized;      /* 0x20016730 +0 flag byte */
} generic_device_registry_wiring;

/* Module state.  Stock: registry head at 0x20007680, subscriber root at
 * 0x20015404, current subscriber at 0x20016734, and the per-callsite static
 * request blocks. */
typedef struct {
    generic_device_registry_device *head;               /* 0x20007680 */
    generic_device_registry_subscriber_root subscribers; /* 0x20015404 */
    generic_device_registry_subscriber *subscriber_current; /* 0x20016734 */
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    /* Recovered per-callsite static blocks (not thread-safe in stock). */
    generic_device_registry_request_block ctrl_block;     /* 0x200076DC */
    generic_device_registry_request_block request_block_a; /* 0x200076FC */
    generic_device_registry_request_block bus_block;      /* 0x20006840 */
    generic_device_registry_request_block request_block_b; /* 0x2000680C */
    uintptr_t message_a[3]; /* 0x2001E560 (0x00096FB0) */
    uintptr_t message_b[3]; /* 0x2001E56C (0x00087AF8) */
} generic_device_registry;

/* Zeroes the module, installs the recovered subscriber descriptor
 * (link_offset 28), and binds providers.  NULL providers leave every
 * provider-dependent path failing explicitly. */
void generic_device_registry_initialize(
    generic_device_registry *registry,
    const generic_device_registry_providers *providers);

/* Installs the R1 board wiring (device pointers, client states, mutex
 * handle, subscriber-initialized flag). */
void generic_device_registry_bind_wiring(
    generic_device_registry *registry,
    const generic_device_registry_wiring *wiring);

/* --- Core registry ------------------------------------------------------- */

/* 0x00085CE0: walk the global list, strcmp each record name, return the
 * matching record or NULL. */
generic_device_registry_device *generic_device_registry_find(
    generic_device_registry *registry, const char *name);

/* 0x00085D58: reject NULL record/name/ops and duplicate names; append to
 * the list, clear the record's next pointer, return 1 on success else 0. */
uint32_t generic_device_registry_register(
    generic_device_registry *registry,
    generic_device_registry_device *device);

/* Seven dispatchers (0x00085D08/0x00085D1A/0x00085CBA/0x00085D2C/
 * 0x00085DA8/0x00085CCC/0x00085D46).  A NULL record returns 1; a NULL
 * operation-table slot returns the recovered per-slot status; otherwise the
 * slot is tail-invoked and its return value passed through. */
uint32_t generic_device_registry_dispatch_slot_00(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3);
uint32_t generic_device_registry_dispatch_slot_08(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3);
uint32_t generic_device_registry_dispatch_slot_0c(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3);
uint32_t generic_device_registry_dispatch_slot_10(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3);
uint32_t generic_device_registry_dispatch_slot_14(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3);
uint32_t generic_device_registry_dispatch_slot_18(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3);
uint32_t generic_device_registry_dispatch_slot_20(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3);

/* --- Offset-based intrusive list (subscriber machinery) ------------------- */

/* 0x00077E30 / 0x00077E3C: guarded stores of the next/prev link word at
 * node + list->link_offset (+4 / +0).  A NULL node is a no-op. */
void generic_device_registry_list_set_next(
    generic_device_registry_link_list *list, void *node, uintptr_t value);
void generic_device_registry_list_set_prev(
    generic_device_registry_link_list *list, void *node, uintptr_t value);

/* 0x0005D8E6 / 0x0005D8F6: guarded head/tail getters (NULL -> NULL).
 * 0x0005D8EE: unguarded next getter in stock; the reconstruction returns
 * NULL for NULL list/node instead of faulting. */
void *generic_device_registry_list_head(
    const generic_device_registry_link_list *list);
void *generic_device_registry_list_next(
    const generic_device_registry_link_list *list, const void *node);
void *generic_device_registry_list_tail(
    const generic_device_registry_link_list *list);

/* 0x0005D8CC: BKDR-style hash, h = h * 0x83 + byte, 32-bit wrap. */
uint32_t generic_device_registry_hash(const void *bytes, uint32_t length);

/* 0x0005D94A: allocate link_offset + 8 bytes through `allocate`, link the
 * node at the tail (next = NULL, prev = old tail), fix the old tail's next,
 * and set the head when the list was empty.  Returns NULL on allocation
 * failure.  The node is NOT zeroed by this helper (stock memset it at the
 * callsite). */
void *generic_device_registry_list_append_alloc(
    generic_device_registry_link_list *list,
    generic_device_registry_alloc_fn allocate);

/* 0x0005D998: unlink a node (head/tail/middle cases); the node storage is
 * not freed (stock behavior). */
void generic_device_registry_list_remove(
    generic_device_registry_link_list *list, void *node);

/* --- Registry mutex guards ------------------------------------------------ */

/* 0x00097730 / 0x00097748: acquire (wait 0xFFFFFFFF) / release the registry
 * mutex when a handle is bound; no-op without one. */
void generic_device_registry_lock(generic_device_registry *registry);
void generic_device_registry_unlock(generic_device_registry *registry);

/* --- Subscriber registry -------------------------------------------------- */

/* 0x0005DB14: requires the initialized flag, a non-NULL name, and a nonzero
 * parameter.  Under the registry mutex: reject a duplicate name (return
 * NULL), allocate+append a node, zero its 0x1C data bytes, store the root
 * back-pointer, copy the name capped at 7 characters (strlen truncated to
 * uint8 first, recovered quirk) with NUL termination, store the parameter,
 * clear flag bits 0/1, and bind the current task. */
generic_device_registry_subscriber *generic_device_registry_subscribe(
    generic_device_registry *registry, const char *name, uintptr_t parameter);

/* 0x0005DBBC: under the mutex, clear flag bit1, zero the tick word, and
 * refresh it through the port operation (1, &tick).  NULL node: no-op. */
void generic_device_registry_subscriber_keepalive(
    generic_device_registry *registry,
    generic_device_registry_subscriber *subscriber);

/* 0x0005DBEA: under the mutex, set flag bit1.  NULL node: no-op. */
void generic_device_registry_subscriber_disable(
    generic_device_registry *registry,
    generic_device_registry_subscriber *subscriber);

/* 0x0005DA00: under the mutex, invoke the port operation (1, &tick) then
 * (0, NULL).  NULL node: no-op. */
void generic_device_registry_subscriber_notify(
    generic_device_registry *registry,
    generic_device_registry_subscriber *subscriber);

/* 0x0005DA30: return the current subscriber's task handle when the current
 * subscriber exists and its flag bit0 is set, else NULL. */
void *generic_device_registry_subscriber_current_task(
    generic_device_registry *registry);

/* --- Static request-block client wrappers --------------------------------- */

/* 0x000509BC: fill ctrl_block {command, code, buffer (only when nonzero),
 * length} and dispatch slot 0x14 on ctrl_device with (device, 0, block). */
void generic_device_registry_ctrl_request(generic_device_registry *registry,
                                          uint8_t command, uint16_t code,
                                          uintptr_t buffer, uint16_t length);

/* 0x0006F90E: ops-table-shaped veneer; reorders to
 * ctrl_request(command, 0, buffer, length) and returns 1. */
uint32_t generic_device_registry_ctrl_adapter(generic_device_registry *registry,
                                              uintptr_t command,
                                              uintptr_t buffer,
                                              uintptr_t length);

/* 0x00050ABC: dispatch slot 0x08 on ctrl_record_b, then slot 0x20 with
 * arg1 = 1 when ctrl_flag is nonzero. */
void generic_device_registry_ctrl_cycle(generic_device_registry *registry);

/* 0x00050DF0: zero a 0x40 time request, store epoch at +0x2C and the uint16
 * offset at +0x30, dispatch slot 0x14 on time_device with (device, 0, block). */
void generic_device_registry_time_request(generic_device_registry *registry,
                                          uint32_t epoch_seconds,
                                          uint16_t utc_offset_minutes);

/* 0x00050F34: fill request_block_a {command, code, data, length2} and
 * dispatch slot 0x10 on request_device_a; returns 1 when the operation
 * returned 0, else 0 (recovered inversion). */
uint32_t generic_device_registry_request_a_control(
    generic_device_registry *registry, uint8_t command, uint16_t code,
    uintptr_t data, uint16_t length2);

/* 0x00050F5C: fill request_block_a {command, code, buffer (only when
 * nonzero), length} and dispatch slot 0x14 on request_device_a; returns 1
 * when the operation returned 0, else 0 (recovered inversion). */
uint32_t generic_device_registry_request_a_transfer(
    generic_device_registry *registry, uint8_t command, uint16_t code,
    uintptr_t buffer, uint16_t length);

/* 0x00050510: fill the shared bus block and dispatch slot 0x10. */
uint32_t generic_device_registry_bus_control_dispatch(
    generic_device_registry *registry, uint8_t command, uint16_t code,
    uintptr_t data, uint16_t length2);

/* 0x00044BE0: select command 0xAE and forward the reordered arguments to
 * the 0x00050510 control helper. */
uint32_t generic_device_registry_bus_read_command_ae(
    generic_device_registry *registry, uint16_t code, uintptr_t data,
    uint16_t length2);

/* 0x0005D1EA: when length is nonzero, fill
 * the shared bus_block {command 0xAE, code, data = buffer, length2} and
 * dispatch slot 0x10 on bus_device, returning its status; zero length
 * returns 0. */
uint32_t generic_device_registry_bus_read(generic_device_registry *registry,
                                          uint16_t code, uintptr_t buffer,
                                          uint16_t length);

/* 0x0005D1F4: seed a local word, bus-read register 0x0D into it; on success
 * (status 0) set its low bit to `bit & 1` and bus-write register 0x0D back. */
void generic_device_registry_bus_update_bit(generic_device_registry *registry,
                                            uint8_t bit, uint32_t seed);

/* 0x00050534: fill the shared bus block and dispatch slot 0x14. */
uint32_t generic_device_registry_bus_transfer_dispatch(
    generic_device_registry *registry, uint8_t command, uint16_t code,
    uintptr_t buffer, uint16_t length);

/* 0x0005D21E: when length is nonzero, run the Nordic
 * delay (5), fill the shared bus_block {command 0xAE, code, buffer (only
 * when nonzero), length} and dispatch slot 0x14 on bus_device, returning
 * its status; zero length returns 0. */
uint32_t generic_device_registry_bus_write(generic_device_registry *registry,
                                           uint16_t code, uintptr_t buffer,
                                           uint16_t length);

/* 0x00077214: dispatch slot 0x0C on slot_0c_device and return its status. */
uint32_t generic_device_registry_slot_0c_entry(generic_device_registry *registry);

/* 0x00087AF8: pack message_b {arg2, arg1, arg3}, dispatch slot 0x10 on
 * message_device with (device, 0, message), return arg3. */
uintptr_t generic_device_registry_message_control(
    generic_device_registry *registry, uintptr_t arg1, uintptr_t arg2,
    uintptr_t arg3);

/* 0x0009338C: fill request_block_b {code, data, length2} (the command byte
 * is NOT written, recovered quirk) and dispatch slot 0x10 on
 * request_device_b; returns 1 when the operation returned 0, else 0. */
uint32_t generic_device_registry_request_b_control(
    generic_device_registry *registry, uint16_t code, uintptr_t data,
    uint16_t length2);

/* 0x00096FB0: pack message_a {arg2, arg1, arg3}; when arg3 is zero replace
 * it with strlen(arg2); dispatch slot 0x14 on message_device. */
void generic_device_registry_message_transfer(generic_device_registry *registry,
                                              uintptr_t arg1, uintptr_t arg2,
                                              uintptr_t arg3);

/* --- Flash-sector clients -------------------------------------------------- */

/* 0x0005B2F8: erase the whole flash region: for i in 0 .. sector_count()-1
 * (recovered 8-bit counter wrap) call erase(record base + i*0x1000, 0x1000). */
void generic_device_registry_flash_erase_all(generic_device_registry *registry);

/* 0x0005E1FC: when the ready flag is set and sector < 2, erase
 * (record base + sector*0x1000, 0x1000) and return 1; else return 0. */
uint32_t generic_device_registry_flash_erase_sector(
    generic_device_registry *registry, uint32_t sector);

/* --- Module sync scan ------------------------------------------------------ */

/* 0x000734E8: when at least one module record has its +0x12 bit0 set, call
 * sync_one_class(record, index) for every table entry (index is a 16-bit
 * wrap counter), log nonzero statuses through the gated R1/Nordic loggers,
 * then invoke the sync flush operation with (1, 0).  Returns 1 always. */
uint32_t generic_device_registry_sync_modules(generic_device_registry *registry);

#endif
