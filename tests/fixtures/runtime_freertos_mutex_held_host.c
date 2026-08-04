/*
 * MIT-licensed host harness for the shared G2 FreeRTOS mutex-held adapter.
 */

#include <stdint.h>

enum {
    OPEN_CFW_TEST_MUTEX_HELD_SEQUENCE_LENGTH = 3,
    OPEN_CFW_TEST_MUTEX_HELD_SLOT_COUNT = 4
};

struct open_cfw_test_mutex_held_slot {
    uintptr_t identity;
    uint32_t value;
};

static uintptr_t open_cfw_test_mutex_held_current_sequence[
    OPEN_CFW_TEST_MUTEX_HELD_SEQUENCE_LENGTH
];
static struct open_cfw_test_mutex_held_slot
    open_cfw_test_mutex_held_slots[OPEN_CFW_TEST_MUTEX_HELD_SLOT_COUNT];
static uint32_t open_cfw_test_mutex_held_current_read_count;
static uint32_t open_cfw_test_mutex_held_count_read_count;
static uint32_t open_cfw_test_mutex_held_count_write_count;
static uint32_t open_cfw_test_mutex_held_increment_count;
static uint32_t open_cfw_test_mutex_held_invalid_identity_count;
static uintptr_t open_cfw_test_mutex_held_increment_owner;
static uint32_t open_cfw_test_mutex_held_fallback_value;

static uintptr_t open_cfw_test_mutex_held_current_tcb_read(void)
{
    uint32_t index = open_cfw_test_mutex_held_current_read_count;

    ++open_cfw_test_mutex_held_current_read_count;
    if (index >= OPEN_CFW_TEST_MUTEX_HELD_SEQUENCE_LENGTH) {
        index = OPEN_CFW_TEST_MUTEX_HELD_SEQUENCE_LENGTH - 1U;
    }
    return open_cfw_test_mutex_held_current_sequence[index];
}

static uint32_t *open_cfw_test_mutex_held_find(uintptr_t identity)
{
    uint32_t index;

    for (index = 0U;
         index < OPEN_CFW_TEST_MUTEX_HELD_SLOT_COUNT;
         ++index) {
        if (open_cfw_test_mutex_held_slots[index].identity == identity) {
            return &open_cfw_test_mutex_held_slots[index].value;
        }
    }

    ++open_cfw_test_mutex_held_invalid_identity_count;
    return &open_cfw_test_mutex_held_fallback_value;
}

static void open_cfw_test_mutex_held_increment(uintptr_t identity)
{
    uint32_t *value = open_cfw_test_mutex_held_find(identity);
    uint32_t next;

    open_cfw_test_mutex_held_increment_owner = identity;
    ++open_cfw_test_mutex_held_increment_count;
    ++open_cfw_test_mutex_held_count_read_count;
    next = *value + 1U;
    ++open_cfw_test_mutex_held_count_write_count;
    *value = next;
}

#define OPEN_CFW_FREERTOS_MUTEX_HELD_CURRENT_TCB_READ() \
    open_cfw_test_mutex_held_current_tcb_read()
#define OPEN_CFW_FREERTOS_MUTEX_HELD_INCREMENT(tcb) \
    open_cfw_test_mutex_held_increment((uintptr_t)(tcb))

#include \
    "../../components/shared/freertos/runtime_freertos_mutex_held.c"

void open_cfw_test_mutex_held_reset(
    uintptr_t first,
    uintptr_t second,
    uintptr_t third
)
{
    uint32_t index;

    open_cfw_test_mutex_held_current_sequence[0] = first;
    open_cfw_test_mutex_held_current_sequence[1] = second;
    open_cfw_test_mutex_held_current_sequence[2] = third;
    for (index = 0U;
         index < OPEN_CFW_TEST_MUTEX_HELD_SLOT_COUNT;
         ++index) {
        open_cfw_test_mutex_held_slots[index].identity = 0U;
        open_cfw_test_mutex_held_slots[index].value = 0U;
    }
    open_cfw_test_mutex_held_current_read_count = 0U;
    open_cfw_test_mutex_held_count_read_count = 0U;
    open_cfw_test_mutex_held_count_write_count = 0U;
    open_cfw_test_mutex_held_increment_count = 0U;
    open_cfw_test_mutex_held_invalid_identity_count = 0U;
    open_cfw_test_mutex_held_increment_owner = 0U;
    open_cfw_test_mutex_held_fallback_value = 0U;
}

void open_cfw_test_mutex_held_set(uintptr_t identity, uint32_t value)
{
    uint32_t index;

    for (index = 0U;
         index < OPEN_CFW_TEST_MUTEX_HELD_SLOT_COUNT;
         ++index) {
        if (
            open_cfw_test_mutex_held_slots[index].identity == identity
            || open_cfw_test_mutex_held_slots[index].identity == 0U
        ) {
            open_cfw_test_mutex_held_slots[index].identity = identity;
            open_cfw_test_mutex_held_slots[index].value = value;
            return;
        }
    }

    ++open_cfw_test_mutex_held_invalid_identity_count;
}

uintptr_t open_cfw_test_mutex_held_invoke(void)
{
    return (uintptr_t)
        open_cfw_freertos_task_increment_mutex_held_count();
}

uint32_t open_cfw_test_mutex_held_get(uintptr_t identity)
{
    return *open_cfw_test_mutex_held_find(identity);
}

uint32_t open_cfw_test_mutex_held_current_reads(void)
{
    return open_cfw_test_mutex_held_current_read_count;
}

uint32_t open_cfw_test_mutex_held_count_reads(void)
{
    return open_cfw_test_mutex_held_count_read_count;
}

uint32_t open_cfw_test_mutex_held_count_writes(void)
{
    return open_cfw_test_mutex_held_count_write_count;
}

uint32_t open_cfw_test_mutex_held_increments(void)
{
    return open_cfw_test_mutex_held_increment_count;
}

uint32_t open_cfw_test_mutex_held_invalid_identities(void)
{
    return open_cfw_test_mutex_held_invalid_identity_count;
}

uintptr_t open_cfw_test_mutex_held_owner(void)
{
    return open_cfw_test_mutex_held_increment_owner;
}
