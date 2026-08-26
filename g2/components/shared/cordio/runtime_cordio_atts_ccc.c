/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-routed G2 Cordio ATT client-characteristic-configuration
 * implementation.  Business behavior follows Packetcraft r20.05--r20.05c
 * and preserves the recovered G2 validation and fixed-SRAM ABI.
 */

#include "runtime_cordio_atts_ccc.h"

#if !defined(OPEN_CFW_ATTS_CCC_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_ALLOCATE_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_GET_TABLE_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_FREE_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_READ_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_WRITE_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_MAIN_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_REGISTER_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_INITIALIZE_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_CLEAR_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_GET_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_SET_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_ENABLED_ONLY) && \
    !defined(OPEN_CFW_ATTS_CCC_LENGTH_ONLY)
#define OPEN_CFW_ATTS_CCC_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_ATTS_CCC_PRODUCTION
#define OPEN_CFW_ATTS_CCC_CB \
    (*(struct open_cfw_cordio_atts_ccc_control_block *)0x20073B00U)
#define OPEN_CFW_ATTS_CCC_ATTS_CALLBACK \
    (*(open_cfw_cordio_atts_ccc_main_callback_t *)0x2006E85CU)
#else
#define OPEN_CFW_ATTS_CCC_CB open_cfw_cordio_atts_ccc_control_block
#define OPEN_CFW_ATTS_CCC_ATTS_CALLBACK \
    open_cfw_cordio_atts_ccc_atts_main_callback
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_CALLBACK_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ccc_callback(
    uint8_t connection_id,
    uint8_t index,
    uint16_t handle,
    uint16_t value
)
{
    struct open_cfw_cordio_atts_ccc_event event;

    event.header.parameter = connection_id;
    event.header.event = OPEN_CFW_ATTS_CCC_STATE_EVENT;
    /* Stock deliberately leaves event.header.status unspecified. */
    event.handle = handle;
    event.value = value;
    event.index = index;
    OPEN_CFW_ATTS_CCC_CB.callback(&event);
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_ALLOCATE_ONLY)
__attribute__((used, noinline))
uint16_t *open_cfw_cordio_atts_ccc_allocate_table(uint8_t connection_id)
{
    uint16_t **slot;

    if (connection_id == 0U) {
        return NULL;
    }
    slot = &OPEN_CFW_ATTS_CCC_CB.tables[connection_id - 1U];
    if (*slot == NULL) {
        *slot = (uint16_t *)open_cfw_cordio_wsf_buffer_allocate_candidate(
            (uint16_t)OPEN_CFW_ATTS_CCC_CB.settings_length * 2U
        );
    }
    return *slot;
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_GET_TABLE_ONLY)
__attribute__((used, noinline))
uint16_t *open_cfw_cordio_atts_ccc_get_table(uint8_t connection_id)
{
    if (connection_id == 0U) {
        return NULL;
    }
    return OPEN_CFW_ATTS_CCC_CB.tables[connection_id - 1U];
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_FREE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ccc_free_table(uint8_t connection_id)
{
    uint16_t **slot;

    if (connection_id == 0U) {
        return;
    }
    slot = &OPEN_CFW_ATTS_CCC_CB.tables[connection_id - 1U];
    if (*slot != NULL) {
        open_cfw_cordio_wsf_buffer_free_candidate(*slot);
        *slot = NULL;
    }
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_READ_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_ccc_read_value(
    uint8_t connection_id,
    uint16_t handle,
    uint8_t *value
)
{
    uint16_t *table;
    uint8_t index;

    for (index = 0U; index < OPEN_CFW_ATTS_CCC_CB.settings_length; index++) {
        if (OPEN_CFW_ATTS_CCC_CB.settings[index].handle == handle) {
            break;
        }
    }
    if (index == OPEN_CFW_ATTS_CCC_CB.settings_length) {
        return OPEN_CFW_ATTS_CCC_ATT_ERR_NOT_FOUND;
    }
    table = open_cfw_cordio_atts_ccc_get_table(connection_id);
    if (table == NULL) {
        return OPEN_CFW_ATTS_CCC_ATT_ERR_RESOURCES;
    }
    value[0] = (uint8_t)table[index];
    value[1] = (uint8_t)(table[index] >> 8);
    return OPEN_CFW_ATTS_CCC_ATT_SUCCESS;
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_WRITE_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_ccc_write_value(
    uint8_t connection_id,
    uint16_t handle,
    uint8_t *value
)
{
    struct open_cfw_cordio_atts_ccc_setting *setting;
    uint16_t *table;
    uint16_t next;
    uint16_t previous;
    uint8_t index;

    for (index = 0U; index < OPEN_CFW_ATTS_CCC_CB.settings_length; index++) {
        if (OPEN_CFW_ATTS_CCC_CB.settings[index].handle == handle) {
            break;
        }
    }
    if (index == OPEN_CFW_ATTS_CCC_CB.settings_length) {
        return OPEN_CFW_ATTS_CCC_ATT_ERR_NOT_FOUND;
    }
    setting = &OPEN_CFW_ATTS_CCC_CB.settings[index];
    next = (uint16_t)value[0] | ((uint16_t)value[1] << 8);
    if (((next != 0U) && (next != OPEN_CFW_ATTS_CCC_NOTIFY)
            && (next != OPEN_CFW_ATTS_CCC_INDICATE))
        || ((next != 0U) && ((next & setting->value_range) == 0U))) {
        return OPEN_CFW_ATTS_CCC_ATT_ERR_VALUE_RANGE;
    }
    table = open_cfw_cordio_atts_ccc_get_table(connection_id);
    if (table == NULL) {
        return OPEN_CFW_ATTS_CCC_ATT_ERR_RESOURCES;
    }
    previous = table[index];
    table[index] = next;
    if (previous != next) {
        open_cfw_cordio_atts_ccc_callback(
            connection_id, index, handle, next
        );
    }
    return OPEN_CFW_ATTS_CCC_ATT_SUCCESS;
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_MAIN_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_ccc_main_callback(
    uint8_t connection_id,
    uint8_t method,
    uint16_t handle,
    uint8_t *value
)
{
    if (method == OPEN_CFW_ATTS_CCC_METHOD_READ) {
        return open_cfw_cordio_atts_ccc_read_value(
            connection_id, handle, value
        );
    }
    return open_cfw_cordio_atts_ccc_write_value(
        connection_id, handle, value
    );
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_REGISTER_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ccc_register(
    uint8_t settings_length,
    struct open_cfw_cordio_atts_ccc_setting *settings,
    open_cfw_cordio_atts_ccc_callback_t callback
)
{
    OPEN_CFW_ATTS_CCC_CB.settings_length = settings_length;
    OPEN_CFW_ATTS_CCC_CB.settings = settings;
    OPEN_CFW_ATTS_CCC_CB.callback = callback;
#ifdef OPEN_CFW_ATTS_CCC_PRODUCTION
    /* Preserve the authenticated registered Thumb entry.  The entry itself
     * is guarded-routed to the maintained MAIN leaf. */
    OPEN_CFW_ATTS_CCC_ATTS_CALLBACK =
        (open_cfw_cordio_atts_ccc_main_callback_t)(uintptr_t)0x0052C0ADU;
#else
    OPEN_CFW_ATTS_CCC_ATTS_CALLBACK = open_cfw_cordio_atts_ccc_main_callback;
#endif
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_INITIALIZE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ccc_initialize_table(
    uint8_t connection_id,
    uint16_t *initial_values
)
{
    uint16_t *table = open_cfw_cordio_atts_ccc_allocate_table(connection_id);
    uint8_t index;

    if (table == NULL) {
        return;
    }
    for (index = 0U; index < OPEN_CFW_ATTS_CCC_CB.settings_length; index++) {
        table[index] = initial_values == NULL ? 0U : initial_values[index];
        if ((initial_values != NULL) && (initial_values[index] != 0U)) {
            open_cfw_cordio_atts_ccc_callback(
                connection_id, index, OPEN_CFW_ATTS_CCC_HANDLE_NONE,
                initial_values[index]
            );
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_CLEAR_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ccc_clear_table(uint8_t connection_id)
{
    if ((connection_id == 0U)
        || (connection_id > OPEN_CFW_ATTS_CCC_CONNECTIONS)) {
        return;
    }
    open_cfw_cordio_atts_ccc_free_table(connection_id);
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_GET_ONLY)
__attribute__((used, noinline))
uint16_t open_cfw_cordio_atts_ccc_get(uint8_t connection_id, uint8_t index)
{
    uint16_t *table = open_cfw_cordio_atts_ccc_get_table(connection_id);
    return table == NULL ? 0U : table[index];
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_SET_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_ccc_set(
    uint8_t connection_id,
    uint8_t index,
    uint16_t value
)
{
    uint16_t *table = open_cfw_cordio_atts_ccc_get_table(connection_id);
    if (table != NULL) {
        table[index] = value;
    }
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_ENABLED_ONLY)
__attribute__((used, noinline))
uint16_t open_cfw_cordio_atts_ccc_enabled(
    uint8_t connection_id,
    uint8_t index
)
{
    if (open_cfw_cordio_dm_connection_security_level(connection_id)
        < OPEN_CFW_ATTS_CCC_CB.settings[index].security_level) {
        return 0U;
    }
    return open_cfw_cordio_atts_ccc_get(connection_id, index);
}
#endif

#if defined(OPEN_CFW_ATTS_CCC_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CCC_LENGTH_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_ccc_table_length(void)
{
    return OPEN_CFW_ATTS_CCC_CB.settings_length;
}
#endif
