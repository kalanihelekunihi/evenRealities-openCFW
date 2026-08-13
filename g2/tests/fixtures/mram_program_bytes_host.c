/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the protected-MRAM byte-program wrapper.
 */

#include <string.h>

unsigned int open_cfw_test_mram_program_bytes_irq_disable(void);
unsigned int open_cfw_test_mram_program_bytes_program(
    unsigned int,
    const void *,
    void *,
    unsigned int
);
void open_cfw_test_mram_program_bytes_restore(unsigned int);

#define OPEN_CFW_MRAM_PROGRAM_BYTES_IRQ_DISABLE() \
    open_cfw_test_mram_program_bytes_irq_disable()
#define OPEN_CFW_MRAM_PROGRAM_BYTES_PROGRAM(key, source, destination, words) \
    open_cfw_test_mram_program_bytes_program( \
        (key), \
        (source), \
        (destination), \
        (words) \
    )
#define OPEN_CFW_MRAM_PROGRAM_BYTES_PRIMASK_RESTORE(value) \
    open_cfw_test_mram_program_bytes_restore(value)

#include "../../components/apollo_main/core_overlay/mram_program_bytes.c"

unsigned int open_cfw_test_mram_program_bytes_order[8];
unsigned int open_cfw_test_mram_program_bytes_order_count;
unsigned int open_cfw_test_mram_program_bytes_disable_result;
unsigned int open_cfw_test_mram_program_bytes_program_result;
unsigned int open_cfw_test_mram_program_bytes_program_count;
unsigned int open_cfw_test_mram_program_bytes_key;
open_cfw_mram_program_bytes_uintptr
open_cfw_test_mram_program_bytes_source;
open_cfw_mram_program_bytes_uintptr
open_cfw_test_mram_program_bytes_destination;
unsigned int open_cfw_test_mram_program_bytes_words;
unsigned int open_cfw_test_mram_program_bytes_restore_count;
unsigned int open_cfw_test_mram_program_bytes_restored_primask;

static void open_cfw_test_mram_program_bytes_order_append(
    unsigned int event
)
{
    if (open_cfw_test_mram_program_bytes_order_count < 8U) {
        open_cfw_test_mram_program_bytes_order[
            open_cfw_test_mram_program_bytes_order_count
        ] = event;
    }
    ++open_cfw_test_mram_program_bytes_order_count;
}

void open_cfw_test_mram_program_bytes_reset(void)
{
    memset(
        open_cfw_test_mram_program_bytes_order,
        0,
        sizeof(open_cfw_test_mram_program_bytes_order)
    );
    open_cfw_test_mram_program_bytes_order_count = 0U;
    open_cfw_test_mram_program_bytes_disable_result = 0U;
    open_cfw_test_mram_program_bytes_program_result = 0U;
    open_cfw_test_mram_program_bytes_program_count = 0U;
    open_cfw_test_mram_program_bytes_key = 0U;
    open_cfw_test_mram_program_bytes_source = 0U;
    open_cfw_test_mram_program_bytes_destination = 0U;
    open_cfw_test_mram_program_bytes_words = 0U;
    open_cfw_test_mram_program_bytes_restore_count = 0U;
    open_cfw_test_mram_program_bytes_restored_primask = 0U;
}

unsigned int open_cfw_test_mram_program_bytes_irq_disable(void)
{
    open_cfw_test_mram_program_bytes_order_append(1U);
    return open_cfw_test_mram_program_bytes_disable_result;
}

unsigned int open_cfw_test_mram_program_bytes_program(
    unsigned int key,
    const void *source,
    void *destination,
    unsigned int words
)
{
    open_cfw_test_mram_program_bytes_order_append(2U);
    ++open_cfw_test_mram_program_bytes_program_count;
    open_cfw_test_mram_program_bytes_key = key;
    open_cfw_test_mram_program_bytes_source =
        (open_cfw_mram_program_bytes_uintptr)source;
    open_cfw_test_mram_program_bytes_destination =
        (open_cfw_mram_program_bytes_uintptr)destination;
    open_cfw_test_mram_program_bytes_words = words;
    return open_cfw_test_mram_program_bytes_program_result;
}

void open_cfw_test_mram_program_bytes_restore(unsigned int value)
{
    open_cfw_test_mram_program_bytes_order_append(3U);
    ++open_cfw_test_mram_program_bytes_restore_count;
    open_cfw_test_mram_program_bytes_restored_primask = value;
}
