/*
 * Host tests for the reconstructed generic device registry (family
 * unknown_generic_device_registry_candidate).  Expected values are derived
 * from the recovered stock semantics documented in
 * docs/correlation/GENERIC-DEVICE-REGISTRY-REDUCTION-CORRELATION.md.
 * Exposes test_reconstructed_generic_device_registry(); the integrator wave
 * wires it into the test runner.
 */

#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "generic_device_registry/generic_device_registry.h"

/* --- Test doubles ---------------------------------------------------------- */

static uintptr_t test_pool[512];
static size_t test_pool_used;
static bool test_pool_fail;
static unsigned int test_alloc_calls;
static size_t test_alloc_last_size;

static void *test_allocate(size_t size) {
    ++test_alloc_calls;
    test_alloc_last_size = size;
    /* heap_4-style alignment rounding so link words stay uintptr_t-aligned */
    size_t aligned = (size + sizeof(uintptr_t) - 1u) & ~(sizeof(uintptr_t) - 1u);
    if (test_pool_fail || test_pool_used + aligned > sizeof(test_pool)) {
        return NULL;
    }
    void *block = (void *)((uint8_t *)test_pool + test_pool_used);
    test_pool_used += aligned;
    return block;
}

static int test_task_token;
static unsigned int test_current_task_calls;

static void *test_current_task(void) {
    ++test_current_task_calls;
    return &test_task_token;
}

static unsigned int test_acquire_calls;
static unsigned int test_release_calls;
static void *test_acquire_mutex_seen;
static uint32_t test_acquire_wait_seen;

static uint32_t test_mutex_acquire(void *mutex, uint32_t wait) {
    ++test_acquire_calls;
    test_acquire_mutex_seen = mutex;
    test_acquire_wait_seen = wait;
    return 0u;
}

static void test_mutex_release(void *mutex) {
    ++test_release_calls;
    assert(mutex == test_acquire_mutex_seen || test_acquire_calls == 0u);
}

static unsigned int test_port_op_calls;
static uintptr_t test_port_op_last_operation;
static uint32_t *test_port_op_last_word;
static uint32_t test_port_op_write_value;
static bool test_port_op_writes;

static uint32_t test_port_op(uintptr_t operation, uint32_t *word) {
    ++test_port_op_calls;
    test_port_op_last_operation = operation;
    test_port_op_last_word = word;
    if (test_port_op_writes && word != NULL) {
        *word = test_port_op_write_value;
    }
    return 0u;
}

static unsigned int test_delay_calls;
static uint32_t test_delay_last;

static void test_delay(uint32_t milliseconds) {
    ++test_delay_calls;
    test_delay_last = milliseconds;
}

static uint32_t test_sector_count_value;
static unsigned int test_sector_count_calls;

static uint32_t test_sector_count(void) {
    ++test_sector_count_calls;
    return test_sector_count_value;
}

static unsigned int test_sync_calls;
static uint16_t test_sync_index_seen[8];
static const uint8_t *test_sync_record_seen[8];
static uint32_t test_sync_status[8];

static uint32_t test_sync_one_class(const uint8_t *module_record,
                                    uint16_t index) {
    assert(test_sync_calls < 8u);
    test_sync_record_seen[test_sync_calls] = module_record;
    test_sync_index_seen[test_sync_calls] = index;
    uint32_t status = test_sync_status[test_sync_calls];
    ++test_sync_calls;
    return status;
}

static uint32_t test_log_level_value;
static unsigned int test_log_level_calls;

static uint32_t test_log_level(void) {
    ++test_log_level_calls;
    return test_log_level_value;
}

static unsigned int test_log_r1_calls;
static unsigned int test_log_nordic_calls;
static uint32_t test_log_r1_marker_seen;
static uint32_t test_log_nordic_id_seen;
static const char *test_log_name_seen;
static uint32_t test_log_status_seen;

static void test_log_r1(uint32_t marker, const char *prefix,
                        const char *format, const char *name,
                        uint32_t status) {
    ++test_log_r1_calls;
    test_log_r1_marker_seen = marker;
    assert(prefix != NULL && format != NULL);
    test_log_name_seen = name;
    test_log_status_seen = status;
}

static void test_log_nordic(uint32_t packed_id, const char *format,
                            const char *name, uint32_t status) {
    ++test_log_nordic_calls;
    test_log_nordic_id_seen = packed_id;
    assert(format != NULL);
    test_log_name_seen = name;
    test_log_status_seen = status;
}

static generic_device_registry_device *test_op_device_seen;
static uintptr_t test_op_args_seen[3];
static uint32_t test_op_return;
static unsigned int test_op_calls;
/* When set, the operation treats arg2 as a request block and writes the low
 * byte of the word pointed to by its data field (bus-read behavior). */
static bool test_op_fills_data;
static uint8_t test_op_fill_value;

static uint32_t test_operation(generic_device_registry_device *device,
                               uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    ++test_op_calls;
    test_op_device_seen = device;
    test_op_args_seen[0] = arg1;
    test_op_args_seen[1] = arg2;
    test_op_args_seen[2] = arg3;
    if (test_op_fills_data && arg2 != 0u) {
        const generic_device_registry_request_block *block =
            (const generic_device_registry_request_block *)arg2;
        if (block->data != 0u) {
            *(uint8_t *)(uintptr_t)block->data = test_op_fill_value;
        }
    }
    return test_op_return;
}

/* Bus operation doubles for the read-modify-write path: the slot 0x10 read
 * delivers a byte through the block's data pointer; the slot 0x14 write
 * captures the word behind the block's buffer pointer. */
static uint8_t test_bus_read_byte;
static uint32_t test_bus_read_status;
static uint32_t test_bus_written_word;
static bool test_bus_write_seen;

static uint32_t test_bus_read_op(generic_device_registry_device *device,
                                 uintptr_t arg1, uintptr_t arg2,
                                 uintptr_t arg3) {
    ++test_op_calls;
    test_op_device_seen = device;
    test_op_args_seen[0] = arg1;
    test_op_args_seen[1] = arg2;
    test_op_args_seen[2] = arg3;
    const generic_device_registry_request_block *block =
        (const generic_device_registry_request_block *)arg2;
    assert(block->data != 0u);
    *(uint8_t *)(uintptr_t)block->data = test_bus_read_byte;
    return test_bus_read_status;
}

static uint32_t test_bus_write_op(generic_device_registry_device *device,
                                  uintptr_t arg1, uintptr_t arg2,
                                  uintptr_t arg3) {
    ++test_op_calls;
    test_op_device_seen = device;
    test_op_args_seen[0] = arg1;
    test_op_args_seen[1] = arg2;
    test_op_args_seen[2] = arg3;
    const generic_device_registry_request_block *block =
        (const generic_device_registry_request_block *)arg2;
    assert(block->buffer != 0u);
    test_bus_written_word = *(const uint32_t *)(uintptr_t)block->buffer;
    test_bus_write_seen = true;
    return 0u;
}

static unsigned int test_erase_calls;
static uint32_t test_erase_address_seen[8];
static uint32_t test_erase_length_seen[8];

static void test_erase(uint32_t address, uint32_t length) {
    assert(test_erase_calls < 8u);
    test_erase_address_seen[test_erase_calls] = address;
    test_erase_length_seen[test_erase_calls] = length;
    ++test_erase_calls;
}

static unsigned int test_flush_calls;
static uintptr_t test_flush_arg1_seen;
static uintptr_t test_flush_arg2_seen;

static uint32_t test_flush(uintptr_t arg1, uintptr_t arg2) {
    ++test_flush_calls;
    test_flush_arg1_seen = arg1;
    test_flush_arg2_seen = arg2;
    return 0u;
}

static int test_mutex_token;

static void test_reset(generic_device_registry *registry,
                       generic_device_registry_providers *providers,
                       generic_device_registry_wiring *wiring) {
    test_pool_used = 0u;
    test_pool_fail = false;
    test_alloc_calls = 0u;
    test_alloc_last_size = 0u;
    test_current_task_calls = 0u;
    test_acquire_calls = 0u;
    test_release_calls = 0u;
    test_acquire_mutex_seen = NULL;
    test_acquire_wait_seen = 0u;
    test_port_op_calls = 0u;
    test_port_op_last_operation = 0u;
    test_port_op_last_word = NULL;
    test_port_op_writes = false;
    test_delay_calls = 0u;
    test_delay_last = 0u;
    test_sector_count_value = 0u;
    test_sector_count_calls = 0u;
    test_sync_calls = 0u;
    test_log_level_value = 0u;
    test_log_level_calls = 0u;
    test_log_r1_calls = 0u;
    test_log_nordic_calls = 0u;
    test_op_device_seen = NULL;
    test_op_args_seen[0] = 0u;
    test_op_args_seen[1] = 0u;
    test_op_args_seen[2] = 0u;
    test_op_return = 0u;
    test_op_calls = 0u;
    test_op_fills_data = false;
    test_op_fill_value = 0u;
    test_bus_read_byte = 0u;
    test_bus_read_status = 0u;
    test_bus_written_word = 0u;
    test_bus_write_seen = false;
    test_erase_calls = 0u;
    test_flush_calls = 0u;

    *providers = (generic_device_registry_providers){
        .allocate = test_allocate,
        .current_task = test_current_task,
        .mutex_acquire = test_mutex_acquire,
        .mutex_release = test_mutex_release,
        .port_op = test_port_op,
        .delay_ms = test_delay,
        .sector_count = test_sector_count,
        .sync_one_class = test_sync_one_class,
        .log_level = test_log_level,
        .log_r1 = test_log_r1,
        .log_nordic = test_log_nordic,
    };
    *wiring = (generic_device_registry_wiring){
        .subscriber_mutex = &test_mutex_token,
        .subscriber_initialized = 1u,
    };
    generic_device_registry_initialize(registry, providers);
    generic_device_registry_bind_wiring(registry, wiring);
}

/* --- Core registry ---------------------------------------------------------- */

static void test_registry_register_and_find(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    static const generic_device_registry_ops ops = {0};
    generic_device_registry_device first = {.name = "i2c_0", .ops = &ops};
    generic_device_registry_device second = {.name = "sys rtc", .ops = &ops};
    generic_device_registry_device duplicate = {.name = "i2c_0", .ops = &ops};
    generic_device_registry_device no_name = {.name = NULL, .ops = &ops};
    generic_device_registry_device no_ops = {.name = "nfc_gpo_irq", .ops = NULL};

    /* Bad arguments return the recovered failure value 0. */
    assert(generic_device_registry_register(NULL, &first) == 0u);
    assert(generic_device_registry_register(&registry, NULL) == 0u);
    assert(generic_device_registry_register(&registry, &no_name) == 0u);
    assert(generic_device_registry_register(&registry, &no_ops) == 0u);
    assert(registry.head == NULL);

    /* Success: returns 1, appends in order, clears the next pointer. */
    first.next = &second; /* cleared by registration */
    assert(generic_device_registry_register(&registry, &first) == 1u);
    assert(registry.head == &first);
    assert(first.next == NULL);
    assert(generic_device_registry_register(&registry, &second) == 1u);
    assert(first.next == &second);
    assert(second.next == NULL);

    /* Duplicate names are rejected. */
    assert(generic_device_registry_register(&registry, &duplicate) == 0u);
    assert(second.next == NULL);

    /* Find: strcmp walk over offset zero; miss and bad arguments -> NULL. */
    assert(generic_device_registry_find(&registry, "sys rtc") == &second);
    assert(generic_device_registry_find(&registry, "i2c_0") == &first);
    assert(generic_device_registry_find(&registry, "watchdog") == NULL);
    assert(generic_device_registry_find(&registry, "i2c_") == NULL);
    assert(generic_device_registry_find(&registry, NULL) == NULL);
    assert(generic_device_registry_find(NULL, "i2c_0") == NULL);
}

static void test_registry_dispatchers(void) {
    static const struct {
        uint32_t (*dispatch)(generic_device_registry_device *, uintptr_t,
                             uintptr_t, uintptr_t);
        uint32_t slot_index;
        uint32_t missing_status;
    } cases[] = {
        {generic_device_registry_dispatch_slot_00, 0u, 5u},
        {generic_device_registry_dispatch_slot_08, 2u, 5u},
        {generic_device_registry_dispatch_slot_0c, 3u, 6u},
        {generic_device_registry_dispatch_slot_10, 4u, 2u},
        {generic_device_registry_dispatch_slot_14, 5u, 3u},
        {generic_device_registry_dispatch_slot_18, 6u, 7u},
        {generic_device_registry_dispatch_slot_20, 8u, 9u},
    };
    for (size_t index = 0u; index < sizeof(cases) / sizeof(cases[0]); ++index) {
        generic_device_registry_ops ops = {0};
        generic_device_registry_device device = {.name = "d", .ops = &ops};
        generic_device_registry_device no_ops = {.name = "d", .ops = NULL};

        /* NULL record returns 1; NULL slot returns the per-slot status. */
        assert(cases[index].dispatch(NULL, 1u, 2u, 3u) == 1u);
        test_op_calls = 0u;
        assert(cases[index].dispatch(&device, 1u, 2u, 3u) ==
               cases[index].missing_status);
        assert(test_op_calls == 0u);
        /* NULL table (stock would fault) returns the missing status. */
        assert(cases[index].dispatch(&no_ops, 1u, 2u, 3u) ==
               cases[index].missing_status);

        /* Bound slot: tail-call argument pass-through and return forward. */
        ops.slot[cases[index].slot_index] = test_operation;
        test_op_calls = 0u;
        test_op_return = 0xABCDu;
        assert(cases[index].dispatch(&device, 0x11u, 0x22u, 0x33u) ==
               0xABCDu);
        assert(test_op_calls == 1u);
        assert(test_op_device_seen == &device);
        assert(test_op_args_seen[0] == 0x11u);
        assert(test_op_args_seen[1] == 0x22u);
        assert(test_op_args_seen[2] == 0x33u);
    }
}

/* --- Intrusive offset list ---------------------------------------------------- */

static void test_list_helpers(void) {
    generic_device_registry_link_list list = {
        .link_offset = GENERIC_DEVICE_REGISTRY_SUBSCRIBER_LINK_OFFSET,
    };
    generic_device_registry_subscriber nodes[3] = {0};

    /* Guarded getters on an empty list; NULL list -> NULL. */
    assert(generic_device_registry_list_head(&list) == NULL);
    assert(generic_device_registry_list_tail(&list) == NULL);
    assert(generic_device_registry_list_head(NULL) == NULL);
    assert(generic_device_registry_list_tail(NULL) == NULL);
    assert(generic_device_registry_list_next(NULL, &nodes[0]) == NULL);
    assert(generic_device_registry_list_next(&list, NULL) == NULL);

    /* Store helpers: NULL node is a no-op. */
    generic_device_registry_list_set_next(&list, NULL, 0xDEADu);
    generic_device_registry_list_set_prev(&list, NULL, 0xDEADu);
    generic_device_registry_list_set_next(NULL, &nodes[0], 0xDEADu);
    assert(nodes[0].next == 0u);

    /* Append allocates link_offset + two pointer words and links at the
     * tail (recovered 36 bytes on the 32-bit target ABI). */
    void *first = generic_device_registry_list_append_alloc(&list, test_allocate);
    assert(first == (void *)test_pool);
    assert(test_alloc_last_size ==
           GENERIC_DEVICE_REGISTRY_SUBSCRIBER_LINK_OFFSET +
               2u * sizeof(uintptr_t));
    assert(list.head == first && list.tail == first);
    assert(generic_device_registry_list_next(&list, first) == NULL);

    void *second = generic_device_registry_list_append_alloc(&list, test_allocate);
    assert(second != NULL && second != first);
    assert(list.head == first && list.tail == second);
    assert(generic_device_registry_list_next(&list, first) == second);
    assert(generic_device_registry_list_next(&list, second) == NULL);

    void *third = generic_device_registry_list_append_alloc(&list, test_allocate);
    assert(third != NULL);
    assert(list.tail == third);
    assert(generic_device_registry_list_next(&list, second) == third);

    /* Allocation failure returns NULL and leaves the list untouched. */
    test_pool_fail = true;
    assert(generic_device_registry_list_append_alloc(&list, test_allocate) ==
           NULL);
    test_pool_fail = false;
    assert(list.tail == third);
    /* Unbound allocator fails explicitly. */
    assert(generic_device_registry_list_append_alloc(&list, NULL) == NULL);

    /* Remove the middle node. */
    generic_device_registry_list_remove(&list, second);
    assert(list.head == first && list.tail == third);
    assert(generic_device_registry_list_next(&list, first) == third);
    assert(generic_device_registry_list_next(&list, third) == NULL);

    /* Remove the head. */
    generic_device_registry_list_remove(&list, first);
    assert(list.head == third && list.tail == third);
    assert(generic_device_registry_list_next(&list, third) == NULL);

    /* Remove the last node: head and tail both clear. */
    generic_device_registry_list_remove(&list, third);
    assert(list.head == NULL && list.tail == NULL);

    /* NULL arguments are no-ops. */
    generic_device_registry_list_remove(NULL, first);
    generic_device_registry_list_remove(&list, NULL);
}

static void test_hash(void) {
    /* Recovered BKDR-style recurrence h = h * 0x83 + byte. */
    assert(generic_device_registry_hash("", 0u) == 0u);
    assert(generic_device_registry_hash("a", 1u) == 0x61u);
    assert(generic_device_registry_hash("ab", 2u) == 12805u);
    /* 32-bit wrap: "i2c_0" -> ((((0x69*0x83+0x32)*0x83+0x63)*0x83+0x5f)*0x83+0x30). */
    uint32_t expected = 0u;
    const char *text = "i2c_0";
    for (uint32_t index = 0u; index < 5u; ++index) {
        expected = expected * 0x83u + (uint8_t)text[index];
    }
    assert(generic_device_registry_hash(text, 5u) == expected);
    assert(generic_device_registry_hash(NULL, 4u) == 0u);
}

/* --- Subscriber registry ------------------------------------------------------- */

static void test_subscribe(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    /* Bad arguments and the uninitialized flag fail explicitly. */
    assert(generic_device_registry_subscribe(NULL, "pmic_irq", 7u) == NULL);
    assert(generic_device_registry_subscribe(&registry, NULL, 7u) == NULL);
    assert(generic_device_registry_subscribe(&registry, "pmic_irq", 0u) == NULL);
    registry.wiring.subscriber_initialized = 0u;
    assert(generic_device_registry_subscribe(&registry, "pmic_irq", 7u) == NULL);
    registry.wiring.subscriber_initialized = 1u;
    assert(test_alloc_calls == 0u);

    /* Successful insert: recovered node contents.  "pmic_irq" is eight
     * characters; the recovered 7-byte cap stores "pmic_ir". */
    generic_device_registry_subscriber *node =
        generic_device_registry_subscribe(&registry, "pmic_irq", 0x1234u);
    assert(node != NULL);
    assert(node->root == &registry.subscribers);
    assert(node->task == &test_task_token);
    assert(node->parameter == 0x1234u);
    assert(node->flags == 0u);
    static const char expected_name[8] = {'p', 'm', 'i', 'c',
                                          '_', 'i', 'r', '\0'};
    for (size_t index = 0u; index < 8u; ++index) {
        assert(node->name[index] == expected_name[index]);
    }
    assert(registry.subscribers.list.head == node);
    assert(registry.subscribers.list.tail == node);
    /* Mutex taken with wait-forever and released around the insert. */
    assert(test_acquire_calls == 1u);
    assert(test_release_calls == 1u);
    assert(test_acquire_mutex_seen == &test_mutex_token);
    assert(test_acquire_wait_seen == 0xFFFFFFFFu);

    /* Duplicate names are rejected under the mutex.  Recovered quirk: the
     * comparison runs against the truncated 7-character stored name, so an
     * exact 7-character request is a duplicate while repeating the original
     * 8-character name is NOT detected and links a second node. */
    assert(generic_device_registry_subscribe(&registry, "pmic_ir", 5u) == NULL);
    assert(registry.subscribers.list.tail == node);
    generic_device_registry_subscriber *second =
        generic_device_registry_subscribe(&registry, "pmic_irq", 6u);
    assert(second != NULL && second != node);
    assert(registry.subscribers.list.head == node);
    assert(registry.subscribers.list.tail == second);
    assert(generic_device_registry_list_next(&registry.subscribers.list,
                                             node) == (void *)second);

    /* A distinct name links a third node at the tail. */
    generic_device_registry_subscriber *third =
        generic_device_registry_subscribe(&registry, "ppg_int", 9u);
    assert(third != NULL);
    assert(registry.subscribers.list.tail == third);

    /* Allocation failure fails explicitly. */
    test_pool_fail = true;
    assert(generic_device_registry_subscribe(&registry, "ppg_int", 1u) == NULL);
    test_pool_fail = false;

    /* Unbound mandatory providers fail explicitly. */
    generic_device_registry unbound;
    generic_device_registry_providers no_providers = {0};
    generic_device_registry_initialize(&unbound, &no_providers);
    generic_device_registry_bind_wiring(&unbound, &wiring);
    assert(generic_device_registry_subscribe(&unbound, "ppg_int", 1u) == NULL);
}

static void test_subscriber_operations(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    /* NULL nodes are no-ops. */
    generic_device_registry_subscriber_keepalive(&registry, NULL);
    generic_device_registry_subscriber_disable(&registry, NULL);
    generic_device_registry_subscriber_notify(&registry, NULL);
    assert(test_port_op_calls == 0u);
    assert(generic_device_registry_subscriber_current_task(NULL) == NULL);
    assert(generic_device_registry_subscriber_current_task(&registry) == NULL);

    generic_device_registry_subscriber *node =
        generic_device_registry_subscribe(&registry, "ppg_int", 0x55u);
    assert(node != NULL);
    test_acquire_calls = 0u;
    test_release_calls = 0u;

    /* Disable sets flag bit1 under the mutex. */
    generic_device_registry_subscriber_disable(&registry, node);
    assert(node->flags == 2u);
    assert(test_acquire_calls == 1u && test_release_calls == 1u);

    /* Keepalive clears bit1, zeroes the tick word, and refreshes it through
     * port operation (1, &tick). */
    node->tick = 0x77u;
    test_port_op_writes = true;
    test_port_op_write_value = 0x4242u;
    generic_device_registry_subscriber_keepalive(&registry, node);
    assert(node->flags == 0u);
    assert(node->tick == 0x4242u);
    assert(test_port_op_calls == 1u);
    assert(test_port_op_last_operation == 1u);
    assert(test_port_op_last_word == &node->tick);

    /* Notify issues (1, &tick) then (0, NULL). */
    test_port_op_calls = 0u;
    test_port_op_writes = false;
    generic_device_registry_subscriber_notify(&registry, node);
    assert(test_port_op_calls == 2u);
    assert(test_port_op_last_operation == 0u);
    assert(test_port_op_last_word == NULL);

    /* Current-task getter requires the current subscriber and flag bit0. */
    registry.subscriber_current = node;
    assert(generic_device_registry_subscriber_current_task(&registry) == NULL);
    node->flags |= 1u;
    assert(generic_device_registry_subscriber_current_task(&registry) ==
           &test_task_token);
    node->task = NULL;
    assert(generic_device_registry_subscriber_current_task(&registry) == NULL);
}

static void test_mutex_guards(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    generic_device_registry_lock(NULL);
    generic_device_registry_unlock(NULL);
    generic_device_registry_lock(&registry);
    generic_device_registry_unlock(&registry);
    assert(test_acquire_calls == 1u && test_release_calls == 1u);
    assert(test_acquire_wait_seen == 0xFFFFFFFFu);

    /* No bound mutex handle: no-op (stock checks the handle word). */
    registry.wiring.subscriber_mutex = NULL;
    generic_device_registry_lock(&registry);
    generic_device_registry_unlock(&registry);
    assert(test_acquire_calls == 1u && test_release_calls == 1u);
}

/* --- Request-block client wrappers --------------------------------------------- */

static void test_ctrl_request_and_adapter(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    generic_device_registry_ops ops = {0};
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_14] = test_operation;
    generic_device_registry_device device = {.name = "ctrl", .ops = &ops};
    registry.wiring.ctrl_device = &device;

    generic_device_registry_ctrl_request(NULL, 1u, 2u, 3u, 4u);
    assert(test_op_calls == 0u);

    generic_device_registry_ctrl_request(&registry, 0xA5u, 0x1234u,
                                         (uintptr_t)&test_pool, 0x30u);
    assert(test_op_calls == 1u);
    assert(test_op_device_seen == &device);
    assert(test_op_args_seen[0] == 0u);
    assert(test_op_args_seen[1] ==
           (uintptr_t)&registry.ctrl_block);
    assert(test_op_args_seen[2] == 0u);
    assert(registry.ctrl_block.command == 0xA5u);
    assert(registry.ctrl_block.code == 0x1234u);
    assert(registry.ctrl_block.buffer == (uintptr_t)&test_pool);
    assert(registry.ctrl_block.length == 0x30u);

    /* Recovered quirk: a zero buffer argument leaves the stale word. */
    generic_device_registry_ctrl_request(&registry, 0x11u, 0x22u, 0u, 0x5u);
    assert(registry.ctrl_block.buffer == (uintptr_t)&test_pool);
    assert(registry.ctrl_block.command == 0x11u);
    assert(registry.ctrl_block.length == 0x5u);

    /* Ops veneer: reorders to (command, 0, buffer, length), returns 1. */
    test_op_calls = 0u;
    assert(generic_device_registry_ctrl_adapter(&registry, 0x7u,
                                                (uintptr_t)&test_task_token,
                                                0x9u) == 1u);
    assert(test_op_calls == 1u);
    assert(registry.ctrl_block.command == 0x7u);
    assert(registry.ctrl_block.code == 0u);
    assert(registry.ctrl_block.buffer == (uintptr_t)&test_task_token);
    assert(registry.ctrl_block.length == 0x9u);
    assert(generic_device_registry_ctrl_adapter(NULL, 0u, 0u, 0u) == 1u);

    /* An unbound device fails through the dispatcher (status 1) silently. */
    registry.wiring.ctrl_device = NULL;
    test_op_calls = 0u;
    generic_device_registry_ctrl_request(&registry, 1u, 2u, 3u, 4u);
    assert(test_op_calls == 0u);
}

static void test_ctrl_cycle(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    generic_device_registry_ops ops = {0};
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_08] = test_operation;
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_20] = test_operation;
    generic_device_registry_device device = {.name = "b", .ops = &ops};
    registry.wiring.ctrl_record_b = &device;

    /* Flag clear: only slot 0x08 runs. */
    registry.wiring.ctrl_flag = 0u;
    test_op_calls = 0u;
    generic_device_registry_ctrl_cycle(&registry);
    assert(test_op_calls == 1u);
    assert(test_op_device_seen == &device);

    /* Flag set: slot 0x08 then slot 0x20 with arg1 = 1. */
    registry.wiring.ctrl_flag = 1u;
    test_op_calls = 0u;
    generic_device_registry_ctrl_cycle(&registry);
    assert(test_op_calls == 2u);
    assert(test_op_args_seen[0] == 1u);

    generic_device_registry_ctrl_cycle(NULL);
}

static void test_time_request(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    generic_device_registry_ops ops = {0};
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_14] = test_operation;
    generic_device_registry_device device = {.name = "sys rtc", .ops = &ops};
    registry.wiring.time_device = &device;

    generic_device_registry_time_request(NULL, 1u, 2u);
    assert(test_op_calls == 0u);

    generic_device_registry_time_request(&registry, 1786708800u, 90u);
    assert(test_op_calls == 1u);
    assert(test_op_device_seen == &device);
    assert(test_op_args_seen[0] == 0u);
    const generic_device_registry_time_block *block =
        (const generic_device_registry_time_block *)test_op_args_seen[1];
    assert(block->epoch_seconds == 1786708800u);
    assert(block->utc_offset_minutes == 90u);
    /* The rest of the 0x40 block is zeroed (stock memset). */
    const uint8_t *bytes = (const uint8_t *)block;
    for (size_t index = 0u; index < sizeof(*block); ++index) {
        if (index >= 0x32u) {
            assert(bytes[index] == 0u);
        }
    }
    assert(test_op_args_seen[2] == 0u);
}

static void test_request_block_a(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    generic_device_registry_ops ops = {0};
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_10] = test_operation;
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_14] = test_operation;
    generic_device_registry_device device = {.name = "a", .ops = &ops};
    registry.wiring.request_device_a = &device;

    /* Control form: data/length2 fields, slot 0x10, inverted return. */
    test_op_return = 0u;
    assert(generic_device_registry_request_a_control(
               &registry, 0x5Au, 0x20u, 0xCAFEu, 2u) == 1u);
    assert(registry.request_block_a.command == 0x5Au);
    assert(registry.request_block_a.code == 0x20u);
    assert(registry.request_block_a.data == 0xCAFEu);
    assert(registry.request_block_a.length2 == 2u);
    assert(test_op_args_seen[1] == (uintptr_t)&registry.request_block_a);

    test_op_return = 2u; /* recovered slot-0x10 missing status */
    assert(generic_device_registry_request_a_control(
               &registry, 0x5Au, 0x20u, 0xCAFEu, 2u) == 0u);

    /* Transfer form: buffer/length fields, slot 0x14, inverted return. */
    test_op_return = 0u;
    assert(generic_device_registry_request_a_transfer(
               &registry, 0x01u, 0x40u, 0xBEEFu, 4u) == 1u);
    assert(registry.request_block_a.buffer == 0xBEEFu);
    assert(registry.request_block_a.length == 4u);

    /* Zero buffer leaves the stale word (recovered). */
    registry.request_block_a.buffer = 0x1234u;
    assert(generic_device_registry_request_a_transfer(
               &registry, 0x01u, 0x40u, 0u, 4u) == 1u);
    assert(registry.request_block_a.buffer == 0x1234u);

    /* NULL registry and unbound device fail explicitly. */
    assert(generic_device_registry_request_a_control(NULL, 0u, 0u, 0u, 1u) ==
           0u);
    registry.wiring.request_device_a = NULL;
    assert(generic_device_registry_request_a_control(
               &registry, 0u, 0u, 0u, 1u) == 0u); /* dispatcher returned 1 */
    assert(generic_device_registry_request_a_transfer(
               &registry, 0u, 0u, 0u, 1u) == 0u); /* dispatcher returned 1 */
}

static void test_bus_read_write(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    generic_device_registry_ops ops = {0};
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_10] = test_operation;
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_14] = test_operation;
    generic_device_registry_device device = {.name = "i2c_1", .ops = &ops};
    registry.wiring.bus_device = &device;

    /* Zero length returns 0 without dispatching. */
    assert(generic_device_registry_bus_read(&registry, 0x0Du, 0x1111u, 0u) ==
           0u);
    assert(generic_device_registry_bus_write(&registry, 0x0Du, 0x1111u, 0u) ==
           0u);
    assert(test_op_calls == 0u && test_delay_calls == 0u);
    assert(generic_device_registry_bus_read(NULL, 0x0Du, 0x1111u, 1u) == 0u);

    /* Read: command 0xAE, code, data = buffer, length2; slot 0x10 status
     * passes through. */
    test_op_return = 0u;
    assert(generic_device_registry_bus_read(&registry, 0x0Du, 0x1111u, 3u) ==
           0u);
    assert(registry.bus_block.command == 0xAEu);
    assert(registry.bus_block.code == 0x0Du);
    assert(registry.bus_block.data == 0x1111u);
    assert(registry.bus_block.length2 == 3u);
    assert(test_op_args_seen[1] == (uintptr_t)&registry.bus_block);
    test_op_return = 7u;
    assert(generic_device_registry_bus_read(&registry, 0x0Du, 0x1111u, 3u) ==
           7u);

    /* Write: Nordic delay(5) runs first, then command 0xAE, code, buffer,
     * length; slot 0x14 status passes through. */
    test_op_return = 0u;
    test_op_calls = 0u;
    assert(generic_device_registry_bus_write(&registry, 0x21u, 0x2222u, 2u) ==
           0u);
    assert(test_delay_calls == 1u && test_delay_last == 5u);
    assert(registry.bus_block.command == 0xAEu);
    assert(registry.bus_block.code == 0x21u);
    assert(registry.bus_block.buffer == 0x2222u);
    assert(registry.bus_block.length == 2u);
    assert(test_op_calls == 1u);

    /* Zero buffer leaves the stale word (recovered). */
    assert(generic_device_registry_bus_write(&registry, 0x21u, 0u, 2u) == 0u);
    assert(registry.bus_block.buffer == 0x2222u);

    /* Unbound delay provider fails explicitly (0) without dispatching. */
    registry.providers.delay_ms = NULL;
    test_op_calls = 0u;
    assert(generic_device_registry_bus_write(&registry, 0x21u, 0x2222u, 2u) ==
           0u);
    assert(test_op_calls == 0u);
}

static void test_bus_update_bit(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    generic_device_registry_ops ops = {0};
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_10] = test_bus_read_op;
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_14] = test_bus_write_op;
    generic_device_registry_device device = {.name = "i2c_2", .ops = &ops};
    registry.wiring.bus_device = &device;

    /* Read delivers 0x04; bit = 1 rewrites the low byte to
     * (0x04 & 0xFE) | 1 = 0x05 while the seed's upper bytes survive. */
    test_bus_read_byte = 0x04u;
    test_bus_read_status = 0u;
    generic_device_registry_bus_update_bit(&registry, 1u, 0x1000u);
    assert(test_bus_write_seen);
    assert(test_bus_written_word == 0x1005u);
    assert(registry.bus_block.code == 0x0Du);
    assert(registry.bus_block.command == 0xAEu);
    assert(registry.bus_block.length == 1u);

    /* bit = 0 rewrites the low byte to 0x04 & 0xFE = 0x04. */
    test_bus_write_seen = false;
    generic_device_registry_bus_update_bit(&registry, 0u, 0x2000u);
    assert(test_bus_write_seen);
    assert(test_bus_written_word == 0x2004u);

    /* A failed read (nonzero status) skips the write entirely. */
    test_bus_read_status = 6u;
    test_bus_write_seen = false;
    generic_device_registry_bus_update_bit(&registry, 1u, 0u);
    assert(!test_bus_write_seen);

    generic_device_registry_bus_update_bit(NULL, 1u, 0u);
}

static void test_slot_0c_entry(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    /* Unbound device: dispatcher status 1. */
    assert(generic_device_registry_slot_0c_entry(&registry) == 1u);
    assert(generic_device_registry_slot_0c_entry(NULL) == 1u);

    generic_device_registry_ops ops = {0};
    generic_device_registry_device device = {.name = "touch", .ops = &ops};
    registry.wiring.slot_0c_device = &device;
    assert(generic_device_registry_slot_0c_entry(&registry) == 6u);

    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_0C] = test_operation;
    test_op_return = 0x55u;
    assert(generic_device_registry_slot_0c_entry(&registry) == 0x55u);
    assert(test_op_device_seen == &device);
}

static void test_message_wrappers(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    generic_device_registry_ops ops = {0};
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_10] = test_operation;
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_14] = test_operation;
    generic_device_registry_device device = {.name = "msg", .ops = &ops};
    registry.wiring.message_device = &device;

    /* 0x00087AF8: packs {arg2, arg1, arg3}, slot 0x10, returns arg3. */
    assert(generic_device_registry_message_control(&registry, 0xA1u, 0xB2u,
                                                   0xC3u) == 0xC3u);
    assert(registry.message_b[0] == 0xB2u);
    assert(registry.message_b[1] == 0xA1u);
    assert(registry.message_b[2] == 0xC3u);
    assert(test_op_args_seen[1] == (uintptr_t)&registry.message_b[0]);
    assert(generic_device_registry_message_control(NULL, 0u, 0u, 0x77u) ==
           0x77u);

    /* 0x00096FB0: packs {arg2, arg1, arg3}; zero arg3 -> strlen(arg2). */
    static const char payload[] = "ship_mode_en";
    generic_device_registry_message_transfer(&registry, 0x44u,
                                             (uintptr_t)payload, 0u);
    assert(registry.message_a[0] == (uintptr_t)payload);
    assert(registry.message_a[1] == 0x44u);
    assert(registry.message_a[2] == 12u);
    generic_device_registry_message_transfer(&registry, 0x45u,
                                             (uintptr_t)payload, 3u);
    assert(registry.message_a[2] == 3u);
    generic_device_registry_message_transfer(NULL, 0u, 0u, 0u);
}

static void test_request_block_b(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    generic_device_registry_ops ops = {0};
    ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_10] = test_operation;
    generic_device_registry_device device = {.name = "b2", .ops = &ops};
    registry.wiring.request_device_b = &device;

    /* Recovered quirk: the command byte is not written. */
    registry.request_block_b.command = 0xEEu;
    test_op_return = 0u;
    assert(generic_device_registry_request_b_control(&registry, 0x33u,
                                                     0x4444u, 1u) == 1u);
    assert(registry.request_block_b.command == 0xEEu);
    assert(registry.request_block_b.code == 0x33u);
    assert(registry.request_block_b.data == 0x4444u);
    assert(registry.request_block_b.length2 == 1u);
    assert(test_op_args_seen[1] == (uintptr_t)&registry.request_block_b);

    test_op_return = 3u;
    assert(generic_device_registry_request_b_control(&registry, 0x33u,
                                                     0x4444u, 1u) == 0u);
    assert(generic_device_registry_request_b_control(NULL, 0u, 0u, 1u) == 0u);
}

/* --- Flash-sector clients ------------------------------------------------------- */

static void test_flash_erase_all(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    static uint32_t record[14];
    record[GENERIC_DEVICE_REGISTRY_FLASH_BASE_WORD] = 0x40000u;
    static const generic_device_registry_flash_ops ops = {.erase = test_erase};
    registry.wiring.flash_all_record = record;
    registry.wiring.flash_all_ops = &ops;

    /* Unbound count provider: explicit no-op. */
    registry.providers.sector_count = NULL;
    generic_device_registry_flash_erase_all(&registry);
    assert(test_erase_calls == 0u);
    registry.providers.sector_count = test_sector_count;

    /* Three sectors from the record base, 0x1000 each, in order. */
    test_sector_count_value = 3u;
    generic_device_registry_flash_erase_all(&registry);
    assert(test_erase_calls == 3u);
    assert(test_erase_address_seen[0] == 0x40000u);
    assert(test_erase_address_seen[1] == 0x41000u);
    assert(test_erase_address_seen[2] == 0x42000u);
    assert(test_erase_length_seen[0] == 0x1000u);

    /* Zero sectors: no calls. */
    test_sector_count_value = 0u;
    test_erase_calls = 0u;
    generic_device_registry_flash_erase_all(&registry);
    assert(test_erase_calls == 0u);

    /* Missing record/ops/erase: explicit no-op. */
    registry.wiring.flash_all_record = NULL;
    generic_device_registry_flash_erase_all(&registry);
    assert(test_erase_calls == 0u);
    generic_device_registry_flash_erase_all(NULL);
}

static void test_flash_erase_sector(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    static uint32_t record[14];
    record[GENERIC_DEVICE_REGISTRY_FLASH_BASE_WORD] = 0x80000u;
    static const generic_device_registry_flash_ops ops = {.erase = test_erase};
    registry.wiring.flash_sector_record = record;
    registry.wiring.flash_sector_ops = &ops;

    /* Not ready, or sector >= 2: return 0 without erasing. */
    registry.wiring.flash_sector_ready = 0u;
    assert(generic_device_registry_flash_erase_sector(&registry, 0u) == 0u);
    registry.wiring.flash_sector_ready = 1u;
    assert(generic_device_registry_flash_erase_sector(&registry, 2u) == 0u);
    assert(generic_device_registry_flash_erase_sector(&registry, 100u) == 0u);
    assert(test_erase_calls == 0u);

    assert(generic_device_registry_flash_erase_sector(&registry, 0u) == 1u);
    assert(test_erase_address_seen[0] == 0x80000u);
    assert(generic_device_registry_flash_erase_sector(&registry, 1u) == 1u);
    assert(test_erase_address_seen[1] == 0x81000u);
    assert(test_erase_length_seen[1] == 0x1000u);
    assert(generic_device_registry_flash_erase_sector(NULL, 0u) == 0u);
}

/* --- Module sync scan ------------------------------------------------------------ */

static uint8_t test_module_storage[3][0x14];
static const uint8_t *test_module_table[3];

/* Byte-wise pointer store matching the recovered 32-bit module-record
 * layout (name pointer at +0x04, not pointer-aligned on wide host ABIs). */
static void test_store_module_name(uint8_t *record, const char *name) {
    uintptr_t word = (uintptr_t)name;
    for (size_t index = 0u; index < sizeof(word); ++index) {
        record[4u + index] = (uint8_t)(word >> (index * 8u));
    }
}

static void test_sync_modules(void) {
    generic_device_registry registry;
    generic_device_registry_providers providers;
    generic_device_registry_wiring wiring;
    test_reset(&registry, &providers, &wiring);

    static const generic_device_registry_sync_ops sync_ops = {
        .flush = test_flush,
    };
    for (size_t index = 0u; index < 3u; ++index) {
        for (size_t byte = 0u; byte < 0x14u; ++byte) {
            test_module_storage[index][byte] = 0u;
        }
        static const char *const names[3] = {"kv.bin", "health.db", "sleep.db"};
        test_store_module_name(&test_module_storage[index][0], names[index]);
        test_module_table[index] = &test_module_storage[index][0];
    }
    registry.wiring.module_begin = &test_module_table[0];
    registry.wiring.module_end = &test_module_table[3];
    registry.wiring.sync_ops = &sync_ops;

    /* No enabled module: return 1 without sync calls or the flush. */
    assert(generic_device_registry_sync_modules(&registry) == 1u);
    assert(test_sync_calls == 0u);
    assert(test_flush_calls == 0u);

    /* Enabled gate set on one record: every entry is synced in index order
     * and the flush runs once with (1, 0). */
    test_module_storage[1][0x12] = 1u;
    test_sync_status[0] = 0u;
    test_sync_status[1] = 0x2Au; /* failing module triggers the log gates */
    test_sync_status[2] = 0u;
    test_log_level_value = 7u; /* all log gates open */
    assert(generic_device_registry_sync_modules(&registry) == 1u);
    assert(test_sync_calls == 3u);
    assert(test_sync_index_seen[0] == 0u);
    assert(test_sync_index_seen[1] == 1u);
    assert(test_sync_index_seen[2] == 2u);
    assert(test_sync_record_seen[2] == &test_module_storage[2][0]);
    assert(test_flush_calls == 1u);
    assert(test_flush_arg1_seen == 1u);
    assert(test_flush_arg2_seen == 0u);
    assert(test_log_r1_calls == 1u);
    assert(test_log_r1_marker_seen == 0x0C800000u);
    assert(test_log_nordic_calls == 1u);
    assert(test_log_nordic_id_seen == 0x001C0003u);
    assert(test_log_status_seen == 0x2Au);

    /* Log level 0: no logger calls for the same failure. */
    test_log_r1_calls = 0u;
    test_log_nordic_calls = 0u;
    test_log_level_value = 0u;
    assert(generic_device_registry_sync_modules(&registry) == 1u);
    assert(test_log_r1_calls == 0u);
    assert(test_log_nordic_calls == 0u);

    /* Unbound sync provider or table: explicit no-op success. */
    registry.providers.sync_one_class = NULL;
    test_sync_calls = 0u;
    test_flush_calls = 0u;
    assert(generic_device_registry_sync_modules(&registry) == 1u);
    assert(test_sync_calls == 0u && test_flush_calls == 0u);
    assert(generic_device_registry_sync_modules(NULL) == 1u);
}

void test_reconstructed_generic_device_registry(void) {
    test_registry_register_and_find();
    test_registry_dispatchers();
    test_list_helpers();
    test_hash();
    test_subscribe();
    test_subscriber_operations();
    test_mutex_guards();
    test_ctrl_request_and_adapter();
    test_ctrl_cycle();
    test_time_request();
    test_request_block_a();
    test_bus_read_write();
    test_bus_update_bit();
    test_slot_0c_entry();
    test_message_wrappers();
    test_request_block_b();
    test_flash_erase_all();
    test_flash_erase_sector();
    test_sync_modules();
}
