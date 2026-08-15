/*
 * Provenance banner
 * -----------------
 * Family:         unknown_generic_device_registry_candidate (Bravechip B210
 *                 "ChipletRing" platform name-based device registry, its
 *                 operation-table dispatchers, the companion offset-based
 *                 intrusive subscriber list, and the static request-block
 *                 client wrappers).
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       r1/research/decompilation/application/decompiler-output.c
 *                 (Ghidra bodies) cross-checked against fresh Capstone/GNU
 *                 objdump Thumb disassembly of the byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin.
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities or
 *                 Bravechip source.  Reduction is owner-authorized per
 *                 docs/SOURCE-ADMISSION.md ("Owner-authorized full reduction
 *                 (2026-08-14)").
 *
 * Per-function mapping (stock extent, end-exclusive / size -> symbol here):
 *
 *   0x000509BC..<0x000509DB  32  -> generic_device_registry_ctrl_request
 *   0x00050ABC..<0x00050AD9  30  -> generic_device_registry_ctrl_cycle
 *   0x00050DF0..<0x00050E17  40  -> generic_device_registry_time_request
 *   0x00050F34..<0x00050F57  36  -> generic_device_registry_request_a_control
 *   0x00050F5C..<0x00050F81  38  -> generic_device_registry_request_a_transfer
 *   0x0005B2F8..<0x0005B327  48  -> generic_device_registry_flash_erase_all
 *   0x0005D1EA..<0x0005D1F3  52  -> generic_device_registry_bus_read
 *                                  (folds shared helpers 0x00044BE0/0x00050510)
 *   0x0005D1F4..<0x0005D21D  42  -> generic_device_registry_bus_update_bit
 *   0x0005D21E..<0x0005D241  68  -> generic_device_registry_bus_write
 *                                  (folds shared helper 0x00050534)
 *   0x0005D8CC..<0x0005D8E5  26  -> generic_device_registry_hash
 *   0x0005D8E6..<0x0005D8ED  8   -> generic_device_registry_list_head
 *   0x0005D8EE..<0x0005D8F5  8   -> generic_device_registry_list_next
 *   0x0005D8F6..<0x0005D8FD  8   -> generic_device_registry_list_tail
 *   0x0005D94A..<0x0005D985  60  -> generic_device_registry_list_append_alloc
 *   0x0005D998..<0x0005D9FF  104 -> generic_device_registry_list_remove
 *   0x0005DA00..<0x0005DA2B  44  -> generic_device_registry_subscriber_notify
 *   0x0005DA30..<0x0005DA45  22  -> generic_device_registry_subscriber_current_task
 *   0x0005DB14..<0x0005DBB1  158 -> generic_device_registry_subscribe
 *   0x0005DBBC..<0x0005DBE9  46  -> generic_device_registry_subscriber_keepalive
 *   0x0005DBEA..<0x0005DC05  28  -> generic_device_registry_subscriber_disable
 *   0x0005E1FC..<0x0005E221  38  -> generic_device_registry_flash_erase_sector
 *   0x0006F90E..<0x0006F91F  18  -> generic_device_registry_ctrl_adapter
 *   0x000734E8..<0x00073577  144 -> generic_device_registry_sync_modules
 *   0x00077214..<0x0007721B  8   -> generic_device_registry_slot_0c_entry
 *   0x00077E30..<0x00077E3B  12  -> generic_device_registry_list_set_next
 *   0x00077E3C..<0x00077E45  10  -> generic_device_registry_list_set_prev
 *   0x00085CBA..<0x00085CCB  18  -> generic_device_registry_dispatch_slot_0c
 *   0x00085CCC..<0x00085CDD  18  -> generic_device_registry_dispatch_slot_18
 *   0x00085CE0..<0x00085D01  34  -> generic_device_registry_find
 *   0x00085D08..<0x00085D19  18  -> generic_device_registry_dispatch_slot_00
 *   0x00085D1A..<0x00085D2B  18  -> generic_device_registry_dispatch_slot_08
 *   0x00085D2C..<0x00085D45  26  -> generic_device_registry_dispatch_slot_10
 *   0x00085D46..<0x00085D57  18  -> generic_device_registry_dispatch_slot_20
 *   0x00085D58..<0x00085DA1  74  -> generic_device_registry_register
 *   0x00085DA8..<0x00085DC1  26  -> generic_device_registry_dispatch_slot_14
 *   0x00087AF8..<0x00087B15  30  -> generic_device_registry_message_control
 *   0x0009338C..<0x000933AF  36  -> generic_device_registry_request_b_control
 *   0x00096FB0..<0x00096FD5  38  -> generic_device_registry_message_transfer
 *   0x00097730..<0x00097741  18  -> generic_device_registry_lock
 *   0x00097748..<0x00097755  14  -> generic_device_registry_unlock
 *
 * Observable behavior is preserved; restructuring is limited to explicit
 * provider bindings (FreeRTOS pvPortMalloc / xTaskGetCurrentTaskHandle,
 * CMSIS osMutex*, the subscriber port operation, the Nordic delay, the R1
 * flash-geometry/sync/log helpers), pointer/argument validation where stock
 * would fault, and per-context state instead of fixed .bss addresses.  Every
 * divergence is listed in
 * docs/correlation/GENERIC-DEVICE-REGISTRY-REDUCTION-CORRELATION.md.
 */

#include "generic_device_registry/generic_device_registry.h"

/* The recovered field offsets are a property of the 32-bit target ABI; on
 * wider host pointer ABIs the C layout legitimately differs, so the exact
 * layout asserts apply to the target ABI only. */
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(generic_device_registry_device, ops) == 0x04u,
               "record +0x04");
_Static_assert(offsetof(generic_device_registry_device, next) == 0x14u,
               "record +0x14");
_Static_assert(sizeof(generic_device_registry_device) == 24u,
               "recovered record is 24 bytes");
_Static_assert(sizeof(generic_device_registry_ops) == 36u,
               "recovered operation table is nine words");
_Static_assert(offsetof(generic_device_registry_link_list, head) == 0x04u,
               "descriptor +0x04");
_Static_assert(offsetof(generic_device_registry_link_list, tail) == 0x08u,
               "descriptor +0x08");
_Static_assert(offsetof(generic_device_registry_subscriber_root, list) == 0x04u,
               "subscriber root +0x04");
_Static_assert(offsetof(generic_device_registry_subscriber, task) == 0x04u,
               "subscriber +0x04");
_Static_assert(offsetof(generic_device_registry_subscriber, name) == 0x08u,
               "subscriber +0x08");
_Static_assert(offsetof(generic_device_registry_subscriber, flags) == 0x10u,
               "subscriber +0x10");
_Static_assert(offsetof(generic_device_registry_subscriber, tick) == 0x14u,
               "subscriber +0x14");
_Static_assert(offsetof(generic_device_registry_subscriber, parameter) == 0x18u,
               "subscriber +0x18");
_Static_assert(offsetof(generic_device_registry_subscriber, prev) == 0x1Cu,
               "subscriber +0x1C");
_Static_assert(offsetof(generic_device_registry_subscriber, next) == 0x20u,
               "subscriber +0x20");
_Static_assert(sizeof(generic_device_registry_subscriber) == 36u,
               "recovered subscriber node is 36 bytes");
_Static_assert(offsetof(generic_device_registry_flash_ops, erase) == 0x30u,
               "flash ops +0x30");
_Static_assert(offsetof(generic_device_registry_sync_ops, flush) == 0x18u,
               "sync ops +0x18");
/* The request block carries uintptr_t words at +0x04/+0x0C, so its exact
 * layout is a 32-bit-target-ABI property like the records above. */
_Static_assert(offsetof(generic_device_registry_request_block, code) == 0x02u,
               "request block +0x02");
_Static_assert(offsetof(generic_device_registry_request_block, buffer) == 0x04u,
               "request block +0x04");
_Static_assert(offsetof(generic_device_registry_request_block, length) == 0x08u,
               "request block +0x08");
_Static_assert(offsetof(generic_device_registry_request_block, data) == 0x0Cu,
               "request block +0x0C");
_Static_assert(offsetof(generic_device_registry_request_block, length2) == 0x10u,
               "request block +0x10");
_Static_assert(sizeof(generic_device_registry_request_block) == 0x14u,
               "recovered request block is 20 bytes");
#endif
_Static_assert(offsetof(generic_device_registry_time_block, epoch_seconds) == 0x2Cu,
               "time request +0x2C");
_Static_assert(offsetof(generic_device_registry_time_block, utc_offset_minutes) == 0x30u,
               "time request +0x30");
_Static_assert(sizeof(generic_device_registry_time_block) == 0x40u,
               "recovered time request is 64 bytes");

/* Recovered log format strings (0x000734E8): R1 logger prefix/format at
 * flash 0x00073580, Nordic/SEGGER format at flash 0x000735B4. */
#define GDR_SYNC_LOG_FORMAT_R1 "[RING]sync store one class, name:%s,ret:%d"
#define GDR_SYNC_LOG_FORMAT_NORDIC "sync store one class, name:%s,ret:%d"
/* Recovered R1 log marker and Nordic packed id
 * (((0x000C44FC - 0x000C441C) >> 3) << 16) + 3. */
#define GDR_SYNC_LOG_MARKER UINT32_C(0x0C800000)
#define GDR_SYNC_LOG_NORDIC_ID UINT32_C(0x001C0003)

/* Local libc replacements; the freestanding build does not use string.h. */
static bool text_equal(const char *left, const char *right) {
    while (*left != '\0' && *left == *right) {
        ++left;
        ++right;
    }
    return *left == *right;
}

static uint32_t text_length(const char *text) {
    uint32_t length = 0u;
    while (text[length] != '\0') {
        ++length;
    }
    return length;
}

static void bytes_zero(void *destination, size_t count) {
    uint8_t *bytes = (uint8_t *)destination;
    for (size_t index = 0u; index < count; ++index) {
        bytes[index] = 0u;
    }
}

static void bytes_copy(void *destination, const void *source, size_t count) {
    uint8_t *target = (uint8_t *)destination;
    const uint8_t *origin = (const uint8_t *)source;
    for (size_t index = 0u; index < count; ++index) {
        target[index] = origin[index];
    }
}

void generic_device_registry_initialize(
    generic_device_registry *registry,
    const generic_device_registry_providers *providers) {
    if (registry == NULL) {
        return;
    }
    bytes_zero(registry, sizeof(*registry));
    if (providers != NULL) {
        registry->providers = *providers;
    }
    /* Recovered fixed descriptor configuration (stock: the non-family R1
     * initcall at 0x0005DAB4 stored link_offset 28 via the 0x0005D8FE
     * helper). */
    registry->subscribers.list.link_offset =
        GENERIC_DEVICE_REGISTRY_SUBSCRIBER_LINK_OFFSET;
}

void generic_device_registry_bind_wiring(
    generic_device_registry *registry,
    const generic_device_registry_wiring *wiring) {
    if (registry == NULL || wiring == NULL) {
        return;
    }
    registry->wiring = *wiring;
}

/* --- Core registry ------------------------------------------------------- */

generic_device_registry_device *generic_device_registry_find(
    generic_device_registry *registry, const char *name) {
    if (registry == NULL || name == NULL) {
        return NULL;
    }
    generic_device_registry_device *record = registry->head;
    while (record != NULL) {
        /* Record names are non-NULL on every registered record; the guard
         * only covers hand-corrupted state (stock would fault). */
        if (record->name != NULL && text_equal(record->name, name)) {
            return record;
        }
        record = record->next;
    }
    return NULL;
}

uint32_t generic_device_registry_register(
    generic_device_registry *registry,
    generic_device_registry_device *device) {
    if (registry == NULL || device == NULL || device->name == NULL ||
            device->ops == NULL) {
        return 0u;
    }
    /* Stock walks the list dereferencing device->name before its NULL check;
     * the reconstruction validates first (identical on every stock-reachable
     * state) and keeps the recovered duplicate rejection. */
    for (const generic_device_registry_device *record = registry->head;
            record != NULL; record = record->next) {
        if (record->name != NULL && text_equal(record->name, device->name)) {
            return 0u;
        }
    }
    if (registry->head == NULL) {
        registry->head = device;
    } else {
        generic_device_registry_device *tail = registry->head;
        while (tail->next != NULL) {
            tail = tail->next;
        }
        tail->next = device;
    }
    device->next = NULL;
    return 1u;
}

/* Shared dispatcher core: NULL record -> 1; NULL table or slot -> the
 * recovered per-slot status (stock faults on a NULL table; the guard
 * returns the same missing-operation status as a NULL slot); otherwise the
 * slot is invoked with (device, arg1, arg2, arg3) and its value returned. */
static uint32_t dispatch_slot(generic_device_registry_device *device,
                              uint32_t slot_index, uint32_t missing_status,
                              uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    if (device == NULL) {
        return GENERIC_DEVICE_REGISTRY_STATUS_DEVICE_NULL;
    }
    generic_device_registry_operation operation = NULL;
    if (device->ops != NULL) {
        operation = device->ops->slot[slot_index];
    }
    if (operation == NULL) {
        return missing_status;
    }
    return operation(device, arg1, arg2, arg3);
}

uint32_t generic_device_registry_dispatch_slot_00(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    return dispatch_slot(device, GENERIC_DEVICE_REGISTRY_SLOT_00,
                         GENERIC_DEVICE_REGISTRY_STATUS_SLOT_00_MISSING,
                         arg1, arg2, arg3);
}

uint32_t generic_device_registry_dispatch_slot_08(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    return dispatch_slot(device, GENERIC_DEVICE_REGISTRY_SLOT_08,
                         GENERIC_DEVICE_REGISTRY_STATUS_SLOT_08_MISSING,
                         arg1, arg2, arg3);
}

uint32_t generic_device_registry_dispatch_slot_0c(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    return dispatch_slot(device, GENERIC_DEVICE_REGISTRY_SLOT_0C,
                         GENERIC_DEVICE_REGISTRY_STATUS_SLOT_0C_MISSING,
                         arg1, arg2, arg3);
}

uint32_t generic_device_registry_dispatch_slot_10(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    return dispatch_slot(device, GENERIC_DEVICE_REGISTRY_SLOT_10,
                         GENERIC_DEVICE_REGISTRY_STATUS_SLOT_10_MISSING,
                         arg1, arg2, arg3);
}

uint32_t generic_device_registry_dispatch_slot_14(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    return dispatch_slot(device, GENERIC_DEVICE_REGISTRY_SLOT_14,
                         GENERIC_DEVICE_REGISTRY_STATUS_SLOT_14_MISSING,
                         arg1, arg2, arg3);
}

uint32_t generic_device_registry_dispatch_slot_18(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    return dispatch_slot(device, GENERIC_DEVICE_REGISTRY_SLOT_18,
                         GENERIC_DEVICE_REGISTRY_STATUS_SLOT_18_MISSING,
                         arg1, arg2, arg3);
}

uint32_t generic_device_registry_dispatch_slot_20(
    generic_device_registry_device *device,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    return dispatch_slot(device, GENERIC_DEVICE_REGISTRY_SLOT_20,
                         GENERIC_DEVICE_REGISTRY_STATUS_SLOT_20_MISSING,
                         arg1, arg2, arg3);
}

/* --- Offset-based intrusive list ------------------------------------------ */

/* Link words live at a byte offset inside each node (recovered 32-bit
 * layout); byte-wise access keeps the freestanding unit alignment-safe on
 * any host ABI while compiling to plain ldr/str on the target. */
static uintptr_t link_word_read(const generic_device_registry_link_list *list,
                                const void *node, uintptr_t link) {
    uintptr_t value = 0u;
    bytes_copy(&value, (const uint8_t *)node + list->link_offset + link,
               sizeof(value));
    return value;
}

static void link_word_write(const generic_device_registry_link_list *list,
                            void *node, uintptr_t link, uintptr_t value) {
    bytes_copy((uint8_t *)node + list->link_offset + link, &value,
               sizeof(value));
}

void generic_device_registry_list_set_next(
    generic_device_registry_link_list *list, void *node, uintptr_t value) {
    if (list == NULL) {
        return;
    }
    if (node != NULL) {
        link_word_write(list, node, sizeof(uintptr_t), value);
    }
}

void generic_device_registry_list_set_prev(
    generic_device_registry_link_list *list, void *node, uintptr_t value) {
    if (list == NULL) {
        return;
    }
    if (node != NULL) {
        link_word_write(list, node, 0u, value);
    }
}

void *generic_device_registry_list_head(
    const generic_device_registry_link_list *list) {
    if (list == NULL) {
        return NULL;
    }
    return list->head;
}

void *generic_device_registry_list_next(
    const generic_device_registry_link_list *list, const void *node) {
    if (list == NULL || node == NULL) {
        return NULL;
    }
    return (void *)link_word_read(list, node, sizeof(uintptr_t));
}

void *generic_device_registry_list_tail(
    const generic_device_registry_link_list *list) {
    if (list == NULL) {
        return NULL;
    }
    return list->tail;
}

uint32_t generic_device_registry_hash(const void *bytes, uint32_t length) {
    if (bytes == NULL) {
        return 0u;
    }
    const uint8_t *data = (const uint8_t *)bytes;
    uint32_t hash = 0u;
    for (uint32_t index = 0u; index < length; ++index) {
        hash = hash * UINT32_C(0x83) + (uint32_t)data[index];
    }
    return hash;
}

void *generic_device_registry_list_append_alloc(
    generic_device_registry_link_list *list,
    generic_device_registry_alloc_fn allocate) {
    if (list == NULL || allocate == NULL) {
        return NULL;
    }
    void *node = allocate(list->link_offset + sizeof(uintptr_t) * 2u);
    if (node == NULL) {
        return NULL;
    }
    generic_device_registry_list_set_next(list, node, 0u);
    generic_device_registry_list_set_prev(list, node, (uintptr_t)list->tail);
    if (list->tail != NULL) {
        generic_device_registry_list_set_next(list, list->tail,
                                              (uintptr_t)node);
    }
    list->tail = node;
    if (list->head == NULL) {
        list->head = node;
    }
    return node;
}

void generic_device_registry_list_remove(
    generic_device_registry_link_list *list, void *node) {
    if (list == NULL || node == NULL) {
        return;
    }
    if (list->head == node) {
        void *next = generic_device_registry_list_next(list, node);
        list->head = next;
        if (next == NULL) {
            list->tail = NULL;
            return;
        }
        generic_device_registry_list_set_prev(list, next, 0u);
        return;
    }
    if (list->tail == node) {
        void *prev = (void *)link_word_read(list, node, 0u);
        list->tail = prev;
        if (prev == NULL) {
            list->head = NULL;
            return;
        }
        generic_device_registry_list_set_next(list, prev, 0u);
        return;
    }
    uintptr_t prev = link_word_read(list, node, 0u);
    uintptr_t next = link_word_read(list, node, sizeof(uintptr_t));
    generic_device_registry_list_set_next(list, (void *)prev, next);
    generic_device_registry_list_set_prev(list, (void *)next, prev);
}

/* --- Registry mutex guards ------------------------------------------------- */

void generic_device_registry_lock(generic_device_registry *registry) {
    if (registry == NULL) {
        return;
    }
    if (registry->wiring.subscriber_mutex != NULL &&
            registry->providers.mutex_acquire != NULL) {
        (void)registry->providers.mutex_acquire(
            registry->wiring.subscriber_mutex,
            GENERIC_DEVICE_REGISTRY_MUTEX_WAIT_FOREVER);
    }
}

void generic_device_registry_unlock(generic_device_registry *registry) {
    if (registry == NULL) {
        return;
    }
    if (registry->wiring.subscriber_mutex != NULL &&
            registry->providers.mutex_release != NULL) {
        registry->providers.mutex_release(registry->wiring.subscriber_mutex);
    }
}

/* --- Subscriber registry --------------------------------------------------- */

generic_device_registry_subscriber *generic_device_registry_subscribe(
    generic_device_registry *registry, const char *name, uintptr_t parameter) {
    if (registry == NULL || name == NULL || parameter == 0u) {
        return NULL;
    }
    if (registry->wiring.subscriber_initialized == 0u) {
        return NULL;
    }
    if (registry->providers.allocate == NULL ||
            registry->providers.current_task == NULL) {
        return NULL;
    }
    generic_device_registry_subscriber_root *root = &registry->subscribers;
    generic_device_registry_lock(registry);
    for (generic_device_registry_subscriber *node =
             (generic_device_registry_subscriber *)
                 generic_device_registry_list_head(&root->list);
            node != NULL;
            node = (generic_device_registry_subscriber *)
                generic_device_registry_list_next(&root->list, node)) {
        if (text_equal(node->name, name)) {
            generic_device_registry_unlock(registry);
            return NULL;
        }
    }
    generic_device_registry_subscriber *node =
        (generic_device_registry_subscriber *)
            generic_device_registry_list_append_alloc(
                &root->list, registry->providers.allocate);
    if (node == NULL) {
        generic_device_registry_unlock(registry);
        return NULL;
    }
    /* Recovered order: the 0x1C-byte data area is zeroed after the links at
     * +0x1C/+0x20 were established by the append. */
    bytes_zero(node, 0x1Cu);
    node->root = root;
    /* Recovered quirk: strlen truncated to uint8 before the 7-byte cap. */
    uint8_t length = (uint8_t)text_length(name);
    if (length > GENERIC_DEVICE_REGISTRY_SUBSCRIBER_NAME_MAX) {
        length = GENERIC_DEVICE_REGISTRY_SUBSCRIBER_NAME_MAX;
    }
    bytes_copy(node->name, name, length);
    node->name[length] = '\0';
    node->parameter = parameter;
    node->flags &= ~UINT32_C(3);
    node->task = registry->providers.current_task();
    generic_device_registry_unlock(registry);
    return node;
}

void generic_device_registry_subscriber_keepalive(
    generic_device_registry *registry,
    generic_device_registry_subscriber *subscriber) {
    if (registry == NULL || subscriber == NULL) {
        return;
    }
    generic_device_registry_lock(registry);
    subscriber->flags &= ~UINT32_C(2);
    subscriber->tick = 0u;
    if (registry->providers.port_op != NULL) {
        (void)registry->providers.port_op(1u, &subscriber->tick);
    }
    generic_device_registry_unlock(registry);
}

void generic_device_registry_subscriber_disable(
    generic_device_registry *registry,
    generic_device_registry_subscriber *subscriber) {
    if (registry == NULL || subscriber == NULL) {
        return;
    }
    generic_device_registry_lock(registry);
    subscriber->flags |= UINT32_C(2);
    generic_device_registry_unlock(registry);
}

void generic_device_registry_subscriber_notify(
    generic_device_registry *registry,
    generic_device_registry_subscriber *subscriber) {
    if (registry == NULL || subscriber == NULL) {
        return;
    }
    generic_device_registry_lock(registry);
    if (registry->providers.port_op != NULL) {
        (void)registry->providers.port_op(1u, &subscriber->tick);
        (void)registry->providers.port_op(0u, NULL);
    }
    generic_device_registry_unlock(registry);
}

void *generic_device_registry_subscriber_current_task(
    generic_device_registry *registry) {
    if (registry == NULL) {
        return NULL;
    }
    generic_device_registry_subscriber *node = registry->subscriber_current;
    if (node == NULL || (node->flags & 1u) == 0u) {
        return NULL;
    }
    return node->task;
}

/* --- Static request-block client wrappers ----------------------------------- */

void generic_device_registry_ctrl_request(generic_device_registry *registry,
                                          uint8_t command, uint16_t code,
                                          uintptr_t buffer, uint16_t length) {
    if (registry == NULL) {
        return;
    }
    generic_device_registry_request_block *block = &registry->ctrl_block;
    block->code = code;
    block->command = command;
    if (buffer != 0u) {
        block->buffer = buffer;
    }
    block->length = length;
    (void)generic_device_registry_dispatch_slot_14(
        registry->wiring.ctrl_device, 0u, (uintptr_t)block, 0u);
}

uint32_t generic_device_registry_ctrl_adapter(generic_device_registry *registry,
                                              uintptr_t command,
                                              uintptr_t buffer,
                                              uintptr_t length) {
    if (registry == NULL) {
        return GENERIC_DEVICE_REGISTRY_STATUS_DEVICE_NULL;
    }
    generic_device_registry_ctrl_request(registry, (uint8_t)command, 0u,
                                         buffer, (uint16_t)length);
    return 1u;
}

void generic_device_registry_ctrl_cycle(generic_device_registry *registry) {
    if (registry == NULL) {
        return;
    }
    (void)generic_device_registry_dispatch_slot_08(
        registry->wiring.ctrl_record_b, 0u, 0u, 0u);
    if (registry->wiring.ctrl_flag != 0u) {
        (void)generic_device_registry_dispatch_slot_20(
            registry->wiring.ctrl_record_b, 1u, 0u, 0u);
    }
}

void generic_device_registry_time_request(generic_device_registry *registry,
                                          uint32_t epoch_seconds,
                                          uint16_t utc_offset_minutes) {
    if (registry == NULL) {
        return;
    }
    generic_device_registry_time_block block;
    bytes_zero(&block, sizeof(block));
    block.epoch_seconds = epoch_seconds;
    block.utc_offset_minutes = utc_offset_minutes;
    (void)generic_device_registry_dispatch_slot_14(
        registry->wiring.time_device, 0u, (uintptr_t)&block, 0u);
}

uint32_t generic_device_registry_request_a_control(
    generic_device_registry *registry, uint8_t command, uint16_t code,
    uintptr_t data, uint16_t length2) {
    if (registry == NULL) {
        return 0u;
    }
    generic_device_registry_request_block *block = &registry->request_block_a;
    block->code = code;
    block->command = command;
    block->length2 = length2;
    block->data = data;
    uint32_t status = generic_device_registry_dispatch_slot_10(
        registry->wiring.request_device_a, 0u, (uintptr_t)block, 0u);
    if (status != GENERIC_DEVICE_REGISTRY_STATUS_OK) {
        return 0u;
    }
    return 1u;
}

uint32_t generic_device_registry_request_a_transfer(
    generic_device_registry *registry, uint8_t command, uint16_t code,
    uintptr_t buffer, uint16_t length) {
    if (registry == NULL) {
        return 0u;
    }
    generic_device_registry_request_block *block = &registry->request_block_a;
    block->code = code;
    block->command = command;
    if (buffer != 0u) {
        block->buffer = buffer;
    }
    block->length = length;
    uint32_t status = generic_device_registry_dispatch_slot_14(
        registry->wiring.request_device_a, 0u, (uintptr_t)block, 0u);
    if (status != GENERIC_DEVICE_REGISTRY_STATUS_OK) {
        return 0u;
    }
    return 1u;
}

uint32_t generic_device_registry_bus_read(generic_device_registry *registry,
                                          uint16_t code, uintptr_t buffer,
                                          uint16_t length) {
    if (registry == NULL || length == 0u) {
        return 0u;
    }
    /* Folded helpers 0x00044BE0 (argument reorder, command 0xAE) and
     * 0x00050510 (block fill + slot 0x10 dispatch on the shared bus block). */
    generic_device_registry_request_block *block = &registry->bus_block;
    block->code = code;
    block->command = GENERIC_DEVICE_REGISTRY_BUS_COMMAND;
    block->length2 = length;
    block->data = buffer;
    return generic_device_registry_dispatch_slot_10(
        registry->wiring.bus_device, 0u, (uintptr_t)block, 0u);
}

void generic_device_registry_bus_update_bit(generic_device_registry *registry,
                                            uint8_t bit, uint32_t seed) {
    if (registry == NULL) {
        return;
    }
    uint32_t local = seed;
    if (generic_device_registry_bus_read(
            registry, GENERIC_DEVICE_REGISTRY_BUS_RMW_REGISTER,
            (uintptr_t)&local, 1u) == GENERIC_DEVICE_REGISTRY_STATUS_OK) {
        local = (local & ~UINT32_C(0xFF)) |
                ((local & UINT32_C(0xFE)) | (uint32_t)(bit & 1u));
        (void)generic_device_registry_bus_write(
            registry, GENERIC_DEVICE_REGISTRY_BUS_RMW_REGISTER,
            (uintptr_t)&local, 1u);
    }
}

uint32_t generic_device_registry_bus_write(generic_device_registry *registry,
                                           uint16_t code, uintptr_t buffer,
                                           uint16_t length) {
    if (registry == NULL || length == 0u) {
        return 0u;
    }
    if (registry->providers.delay_ms == NULL) {
        return 0u;
    }
    registry->providers.delay_ms(GENERIC_DEVICE_REGISTRY_BUS_DELAY_MS);
    /* Folded helper 0x00050534 (block fill + slot 0x14 dispatch on the
     * shared bus block). */
    generic_device_registry_request_block *block = &registry->bus_block;
    block->code = code;
    block->command = GENERIC_DEVICE_REGISTRY_BUS_COMMAND;
    if (buffer != 0u) {
        block->buffer = buffer;
    }
    block->length = length;
    return generic_device_registry_dispatch_slot_14(
        registry->wiring.bus_device, 0u, (uintptr_t)block, 0u);
}

uint32_t generic_device_registry_slot_0c_entry(generic_device_registry *registry) {
    if (registry == NULL) {
        return GENERIC_DEVICE_REGISTRY_STATUS_DEVICE_NULL;
    }
    return generic_device_registry_dispatch_slot_0c(
        registry->wiring.slot_0c_device, 0u, 0u, 0u);
}

uintptr_t generic_device_registry_message_control(
    generic_device_registry *registry, uintptr_t arg1, uintptr_t arg2,
    uintptr_t arg3) {
    if (registry == NULL) {
        return arg3;
    }
    uintptr_t *message = registry->message_b;
    message[0] = arg2;
    message[1] = arg1;
    message[2] = arg3;
    (void)generic_device_registry_dispatch_slot_10(
        registry->wiring.message_device, 0u, (uintptr_t)message, 0u);
    return arg3;
}

uint32_t generic_device_registry_request_b_control(
    generic_device_registry *registry, uint16_t code, uintptr_t data,
    uint16_t length2) {
    if (registry == NULL) {
        return 0u;
    }
    generic_device_registry_request_block *block = &registry->request_block_b;
    block->code = code;
    /* Recovered quirk: the command byte is not written by this wrapper. */
    block->length2 = length2;
    block->data = data;
    uint32_t status = generic_device_registry_dispatch_slot_10(
        registry->wiring.request_device_b, 0u, (uintptr_t)block, 0u);
    if (status != GENERIC_DEVICE_REGISTRY_STATUS_OK) {
        return 0u;
    }
    return 1u;
}

void generic_device_registry_message_transfer(generic_device_registry *registry,
                                              uintptr_t arg1, uintptr_t arg2,
                                              uintptr_t arg3) {
    if (registry == NULL) {
        return;
    }
    uintptr_t *message = registry->message_a;
    message[0] = arg2;
    message[1] = arg1;
    message[2] = arg3;
    if (arg3 == 0u) {
        message[2] = (uintptr_t)text_length((const char *)arg2);
    }
    (void)generic_device_registry_dispatch_slot_14(
        registry->wiring.message_device, 0u, (uintptr_t)message, 0u);
}

/* --- Flash-sector clients ---------------------------------------------------- */

void generic_device_registry_flash_erase_all(generic_device_registry *registry) {
    if (registry == NULL || registry->providers.sector_count == NULL) {
        return;
    }
    const uint32_t *record = registry->wiring.flash_all_record;
    const generic_device_registry_flash_ops *ops = registry->wiring.flash_all_ops;
    if (record == NULL || ops == NULL || ops->erase == NULL) {
        return;
    }
    uint8_t count = (uint8_t)registry->providers.sector_count();
    /* Recovered 8-bit loop counter (i = (i + 1) & 0xFF in stock). */
    for (uint8_t index = 0u; index < count; index = (uint8_t)(index + 1u)) {
        ops->erase(record[GENERIC_DEVICE_REGISTRY_FLASH_BASE_WORD] +
                       (uint32_t)index * GENERIC_DEVICE_REGISTRY_SECTOR_SIZE,
                   GENERIC_DEVICE_REGISTRY_SECTOR_SIZE);
    }
}

uint32_t generic_device_registry_flash_erase_sector(
    generic_device_registry *registry, uint32_t sector) {
    if (registry == NULL) {
        return 0u;
    }
    const uint32_t *record = registry->wiring.flash_sector_record;
    const generic_device_registry_flash_ops *ops = registry->wiring.flash_sector_ops;
    if (registry->wiring.flash_sector_ready != 0u && sector < 2u &&
            record != NULL && ops != NULL && ops->erase != NULL) {
        ops->erase(record[GENERIC_DEVICE_REGISTRY_FLASH_BASE_WORD] +
                       sector * GENERIC_DEVICE_REGISTRY_SECTOR_SIZE,
                   GENERIC_DEVICE_REGISTRY_SECTOR_SIZE);
        return 1u;
    }
    return 0u;
}

/* --- Module sync scan -------------------------------------------------------- */

uint32_t generic_device_registry_sync_modules(generic_device_registry *registry) {
    if (registry == NULL || registry->providers.sync_one_class == NULL) {
        return 1u;
    }
    const uint8_t *const *begin = registry->wiring.module_begin;
    const uint8_t *const *end = registry->wiring.module_end;
    if (begin == NULL || end == NULL) {
        return 1u;
    }
    /* Enabled gate: at least one module record with its +0x12 bit0 set. */
    bool any_enabled = false;
    for (const uint8_t *const *entry = begin; entry < end; ++entry) {
        if (*entry != NULL && ((*entry)[0x12] & 1u) != 0u) {
            any_enabled = true;
            break;
        }
    }
    if (!any_enabled) {
        return 1u;
    }
    uint16_t index = 0u;
    for (const uint8_t *const *entry = begin; entry < end; ++entry) {
        const uint8_t *module = *entry;
        if (module != NULL) {
            uint32_t status =
                registry->providers.sync_one_class(module, index);
            if (status != 0u) {
                /* Module record +0x04: name pointer (byte-wise read; the
                 * recovered 32-bit layout is not pointer-aligned on wide
                 * host ABIs). */
                uintptr_t name_word = 0u;
                bytes_copy(&name_word, module + 4u, sizeof(name_word));
                const char *name = (const char *)name_word;
                if (registry->providers.log_level != NULL &&
                        registry->providers.log_r1 != NULL) {
                    uint32_t level = registry->providers.log_level();
                    if ((level & 1u) != 0u || (level & 4u) != 0u) {
                        registry->providers.log_r1(GDR_SYNC_LOG_MARKER,
                                                   GDR_SYNC_LOG_FORMAT_R1,
                                                   GDR_SYNC_LOG_FORMAT_R1,
                                                   name, status);
                    }
                }
                if (registry->providers.log_level != NULL &&
                        registry->providers.log_nordic != NULL) {
                    if ((registry->providers.log_level() & 2u) != 0u) {
                        registry->providers.log_nordic(GDR_SYNC_LOG_NORDIC_ID,
                                                       GDR_SYNC_LOG_FORMAT_NORDIC,
                                                       name, status);
                    }
                }
            }
        }
        index = (uint16_t)(index + 1u);
    }
    const generic_device_registry_sync_ops *ops = registry->wiring.sync_ops;
    if (ops != NULL && ops->flush != NULL) {
        (void)ops->flush(1u, 0u);
    }
    return 1u;
}
