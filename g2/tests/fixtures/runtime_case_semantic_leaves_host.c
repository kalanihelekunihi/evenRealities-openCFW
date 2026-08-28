/* SPDX-License-Identifier: MIT */
#include "runtime_case_semantic_leaves.h"

#include <stdint.h>
#include <string.h>

static uint32_t action_count;
static uint32_t command_first;
static uint32_t command_second;
static uintptr_t dispatch_resource;
static uint32_t dispatch_values[3];
static uint32_t emitted_bits;
static uint32_t emitted_count;
static uint32_t notify_count;
static uint32_t profile_values[8];
static uintptr_t mask_resource;
static uint32_t mask_value;
static void *resource_seen;
static uint32_t cursor_argument;
static uint32_t cursor_value;
static char event_log[256];
static uint32_t event_count;
static uint32_t sample_bits;
static uint32_t sample_count;
static uint32_t mask_action_value[2];
static uint32_t fake_tick;
static uint32_t bit_pattern;
static uint32_t bit_index;
static uint32_t selector_attempts;
static volatile uint32_t *wait_status_register;
static uint32_t status_action_count;
static uint32_t configured_record[5];
static volatile uint32_t *controller_wait_registers;
static uint32_t register_sequence[14];
static uint32_t register_sequence_count;
static uint32_t probe_values[8];
static uint32_t probe_value_count;
static uint32_t probe_value_index;
static volatile uint32_t *serial_wait_registers;
static uint32_t serial_words[3];
static uint32_t serial_word_count;
static uint32_t stable_read_count;
static uint32_t descriptor_seen;
static uint32_t serial_read_values[4];
static uint32_t serial_read_index;
static uint32_t sample_values8[8];
static uint32_t sample_index8;
static volatile uint32_t *start_controller_registers;
static uint32_t wait_call_count;
static int restored_irq_state;
static uint32_t selector_write_count;
static uint32_t waiter_unblock_count;
static uint32_t finalized_short;
static uint32_t wire_last_value;
static uint32_t wire_collect_index;
static uint32_t frame_notify_value;
static uint32_t pulse_write_count;

static void action(void) { ++action_count; }
static void command(uint32_t first, uint32_t second)
{ command_first = first; command_second = second; }
static int mode_action(uint32_t first, uint32_t second, uint32_t mode)
{ return first == 4U && second == 5U && mode == 1U ? 0 : -1; }
static int byte_action(uint32_t selector, uint8_t value)
{ return selector == 7U && value == 9U ? 0 : -1; }
static void transform(uint32_t *value) { *value ^= 0x55AA55AAU; }
static void dispatch(uintptr_t resource, uint32_t first, uint32_t second,
                     uint32_t third)
{
    dispatch_resource = resource;
    dispatch_values[0] = first;
    dispatch_values[1] = second;
    dispatch_values[2] = third;
}
static void emit(int enabled)
{ emitted_bits = (emitted_bits << 1U) | (enabled != 0); ++emitted_count; }
static void notify(void *record) { (void)record; ++notify_count; }
static void write_index(uint32_t index, uint32_t value)
{ if (index < 8U) profile_values[index] = value; }
static uint32_t read_mask(uintptr_t resource, uint32_t mask)
{ mask_resource = resource; mask_value = mask; return mask; }
static void write_mask(uintptr_t resource, uint32_t mask, uint32_t value)
{ mask_resource = resource; mask_value = mask ^ value; }
static void resource_action(void *resource) { resource_seen = resource; }
static int fill_status(uint8_t status[28])
{ status[26] = 0x10U; return 0; }
static int query_word(uint32_t *value) { *value = 0x1234ABCDU; return 0; }
static void publish_cursor(uint32_t argument, uint32_t cursor)
{ cursor_argument = argument; cursor_value = cursor; }
static void log_event(char event)
{ if (event_count < sizeof(event_log)) event_log[event_count++] = event; }
static void mask4_set(void) { log_event('a'); }
static void mask4_clear(void) { log_event('b'); }
static void mask8_set(void) { log_event('c'); }
static void mask8_clear(void) { log_event('d'); }
static void word4_primary(void) { log_event('p'); }
static void word4_alternate(void) { log_event('q'); }
static void counted_delay(int32_t iterations)
{ log_event(iterations == 23 ? 's' : iterations == 90 ? 'l' : 'x'); }
static void clock_write(int enabled) { log_event(enabled != 0 ? 'C' : 'c'); }
static void data_write(int enabled) { log_event(enabled != 0 ? 'D' : 'd'); }
static int sample(void)
{
    int value = (sample_bits & 0x80U) != 0U;
    sample_bits = (sample_bits & 0x7FU) << 1U;
    ++sample_count;
    return value;
}
static void line_delay(void) { log_event('-'); }
static int query_command(uint32_t command_value, uint32_t *value,
                         uint32_t mode)
{
    if (command_value != 0xA2U || value == NULL || mode != 1U) return -1;
    *value |= 1U;
    return 0;
}
static void first_mask_action(uint32_t mask)
{ mask_action_value[0] = mask; }
static void second_mask_action(uint32_t mask)
{ mask_action_value[1] = mask; }
static uint32_t read_tick(void) { return fake_tick++; }
static int read_bit(int *value)
{
    if (value == NULL || bit_index >= 8U) return 0;
    *value = (int)((bit_pattern >> (7U - bit_index++)) & 1U);
    return 1;
}
static int update_byte(uint32_t index, uint32_t mode, uint32_t *value,
                       uint32_t argument, uint32_t repeated_index)
{
    if (value == NULL || mode != 1U || index != repeated_index) return 0;
    *value = (*value + argument) & 0xFFU;
    return 1;
}
static int stage_first(void *resource)
{ return resource == NULL ? -1 : 0; }
static int stage_second(void *resource)
{ return resource == NULL ? -1 : 0; }
static int attempt_selector(uint32_t selector)
{ ++selector_attempts; return selector == 8U ? 0 : -1; }
static uint32_t read_wait_tick(void)
{
    if (wait_status_register != NULL && fake_tick == 3U)
        *wait_status_register |= 1U << 5U;
    return fake_tick++;
}
static int status_start(void) { ++status_action_count; return 1; }
static int status_finalize(void) { ++status_action_count; return 0; }
static int query_a0(uint32_t *value)
{ if (value == NULL) return -1; *value = 0xA0U; return 0; }
static void configure_record(uintptr_t resource, const uint32_t record_value[5])
{
    uint32_t index;
    dispatch_resource = resource;
    for (index = 0U; index < 5U; ++index)
        configured_record[index] = record_value[index];
}
static void context_dispatch(void *context_value, uint32_t first,
                             uint32_t second)
{
    resource_seen = context_value;
    dispatch_values[0] = first;
    dispatch_values[1] = second;
}
static void register_write(uint32_t index, uint32_t value)
{
    if (register_sequence_count + 1U < 14U) {
        register_sequence[register_sequence_count++] = index;
        register_sequence[register_sequence_count++] = value;
    }
}
static void configure_context(void *resource, uint8_t *configuration)
{
    resource_seen = resource;
    if (configuration != NULL) configuration[0] = 0x5AU;
}
static uint32_t read_probe_value(void)
{
    if (probe_value_index >= probe_value_count) return 0U;
    return probe_values[probe_value_index++];
}
static uint32_t read_serial_tick(void)
{
    if (serial_wait_registers != NULL && fake_tick == 2U)
        serial_wait_registers[4] &= ~UINT32_C(0x00030000);
    return fake_tick++;
}
static void write_serial_word(uint32_t value)
{
    if (serial_word_count < 3U) serial_words[serial_word_count++] = value;
}
static int acknowledge_success(void) { return 0; }
static uint32_t read_serial_value(void)
{
    if (serial_read_index >= 4U) return 0U;
    return serial_read_values[serial_read_index++];
}
static uint32_t read_resource_value(void *resource)
{
    resource_seen = resource;
    return sample_values8[sample_index8++];
}
static uint32_t read_start_controller_tick(void)
{
    if (start_controller_registers != NULL && fake_tick == 3U)
        start_controller_registers[3] |= 1U << 2U;
    return fake_tick++;
}
static int status_true(void) { return 1; }
static void restore_irq(int enabled) { restored_irq_state = enabled; }
static int wait_success(uint32_t timeout)
{ ++wait_call_count; return timeout == 1000U ? 0 : 1; }
static void pair_action(uint32_t first, uint32_t second)
{ command_first = first; command_second = second; }
static void copy_one(uint32_t *destination, const uint32_t *source)
{ destination[0] = source[0]; }
static int write_selector_byte(uint32_t selector, uint8_t value)
{
    if (selector_write_count < 80U &&
        (selector != selector_write_count + 0x10U ||
         value != (uint8_t)selector_write_count)) return -1;
    ++selector_write_count;
    return 0;
}
static int read_selector_byte(uint32_t selector, uint8_t *value)
{
    if (selector != 0xA7U || value == NULL) return -1;
    *value = 0x0CU;
    return 0;
}
static void unblock_waiter(void *waiter, uint32_t value)
{
    (void)waiter;
    dispatch_values[0] = value;
    ++waiter_unblock_count;
}
static void finalize_short(void *context, int16_t value)
{ resource_seen = context; finalized_short = (uint16_t)value; }
static int wait_condition_success(
    uint8_t *context, volatile uint32_t *controller, uint32_t mask,
    int expected, uint32_t started, uint32_t timeout)
{
    (void)context; (void)controller; (void)mask; (void)expected;
    (void)started; (void)timeout;
    ++wait_call_count;
    return 0;
}
static void init_entry(uint32_t first, uint32_t second, uint32_t third)
{ dispatch_values[0] = first; dispatch_values[1] = second; dispatch_values[2] = third; }
static void wire_emit(uint32_t value, int seven_bits)
{ wire_last_value = value; dispatch_values[0] = (uint32_t)seven_bits; }
static void wire_route(int enabled) { dispatch_values[1] = (uint32_t)enabled; }
static int wire_check(uint32_t *value)
{
    uint32_t checked = dispatch_values[1] != 0U
        ? wire_last_value * 2U + 1U : wire_last_value * 2U;
    if (value == NULL) return 0;
    *value = open_cfw_case_parity8(checked);
    return 1;
}
static uint32_t wire_parity_marker(void) { return 1U; }
static int wire_collect(uint8_t *value)
{ if (value == NULL) return 0; *value = (uint8_t)(0xA0U + wire_collect_index++); return 1; }
static int frame_validate(const uint8_t *data, uint32_t length)
{ return data != NULL && length != 0U; }
static int frame_read(uint8_t *output, uint32_t length, uint32_t timeout)
{ memset(output, 0x5A, length); return timeout == 20U ? 0 : 3; }
static void frame_notify(uint32_t mask) { frame_notify_value = mask; }
static void pulse_write(uintptr_t resource, uint32_t mask, uint32_t value)
{ (void)resource; (void)mask; (void)value; ++pulse_write_count; }
static int initialize_three(uint32_t selector) { return selector == 3U ? 0 : 1; }
static int transfer_success(void *resource) { return resource == NULL ? 1 : 0; }
static int selector_read(uint32_t selector, uint32_t *value)
{
    if (value == NULL) return -1;
    if (selector == 8U) *value = 0U;
    else if (selector == 0x0BU) *value = 0x80U;
    else if (selector >= 0x10U && selector < 0x60U)
        *value = selector - 0x10U;
    else return -1;
    return 0;
}
static int stable_read(uintptr_t resource, uint32_t *value, uint32_t length)
{
    if (resource != 0x99U || value == NULL || length != 2U) return -1;
    ++stable_read_count;
    *value = UINT32_C(0x00003412);
    return 0;
}
static uint32_t read_first_value(void) { return 0xAAU; }
static uint32_t read_second_value(void) { return 0xBBU; }
static int context_pair_success(void *context, uint32_t first,
                                uint32_t second)
{
    resource_seen = context;
    dispatch_values[0] = first;
    dispatch_values[1] = second;
    return 0;
}
static int context_value_success(void *context, uint32_t value)
{ resource_seen = context; dispatch_values[0] = value; return 0; }
static int context_transfer_success(void *context, uint32_t option,
                                    int enabled)
{
    resource_seen = context;
    dispatch_values[0] = option;
    dispatch_values[1] = (uint32_t)enabled;
    return 0;
}
static int context_descriptor_success(
    void *context, const uint32_t descriptor[3])
{
    resource_seen = context;
    descriptor_seen = descriptor == NULL ? 0U : descriptor[0];
    return descriptor == NULL ? 1 : 0;
}
static int query_nonzero(uint32_t selector) { (void)selector; return 1; }
static int record_success(const uint32_t *record, uint32_t words)
{
    if (record == NULL || words == 0U) return 1;
    descriptor_seen = record[0];
    dispatch_values[2] = words;
    return 0;
}
static int wait_channel_success(void *context, uint32_t mask,
                                uint32_t started, uint32_t budget)
{
    resource_seen = context;
    dispatch_values[0] = mask;
    dispatch_values[1] = started;
    dispatch_values[2] = budget;
    return 0;
}
static uint32_t read_controller_tick(void)
{
    if (controller_wait_registers != NULL && fake_tick == 3U)
        controller_wait_registers[3] |= 1U << 6U;
    return fake_tick++;
}
static int wait_ready_success(void *resource)
{ return resource == NULL ? -1 : 0; }
static uint32_t divide_value(uint32_t numerator, uint32_t denominator)
{ return denominator == 0U ? 0U : numerator / denominator; }

int main(void)
{
    uint8_t record[16] = {5U, 1U, 2U, 0xA5U, 0U, 0U, 0U, 0U,
                          0xFEU, 0xFFU, 0xFFU, 0xFFU, 0U, 0U, 0U, 0U};
    uint8_t context[0x90] = {0};
    uint32_t index;

    if (open_cfw_case_read_byte3(NULL) != 0U) return 1;
    if (open_cfw_case_read_byte3(record) != 0xA5U) return 1;
    open_cfw_case_add_byte0_to_word8(record);
    if (record[8] != 3U || record[9] != 0U ||
        record[10] != 0U || record[11] != 0U) return 2;
    open_cfw_case_add_byte0_to_word8(NULL);
    for (index = 0U; index < 8U; ++index) record[index] = (uint8_t)(index + 1U);
    open_cfw_case_copy_head8_to_tail8(record);
    if (memcmp(record, record + 8, 8U) != 0) return 3;
    open_cfw_case_copy_head8_to_tail8(NULL);
    context[0x88] = 0x78U;
    context[0x89] = 0x56U;
    context[0x8A] = 0x34U;
    context[0x8B] = 0x12U;
    context[0x8C] = 0x0FU;
    context[0x8D] = 0xF0U;
    context[0x8E] = 0x00U;
    context[0x8F] = 0x80U;
    if (open_cfw_case_or_words_88_8c(context) != UINT32_C(0x9234F67F)) return 4;
    if (open_cfw_case_or_words_88_8c(NULL) != 0U) return 5;
    for (index = 0U; index < 256U; ++index) {
        uint32_t expected = 0U;
        uint32_t bit;
        for (bit = 0U; bit < 8U; ++bit) expected ^= (index >> bit) & 1U;
        if (open_cfw_case_parity8(index) != expected) return 6;
        if (open_cfw_case_parity8_alt(index) != expected) return 7;
    }
    open_cfw_case_delay_10();
    open_cfw_case_busy_delay(-1);
    open_cfw_case_busy_delay_alt(-1);
    open_cfw_case_busy_delay(INT32_MIN);
    open_cfw_case_busy_delay_alt(INT32_MIN);
    open_cfw_case_busy_delay(2U);
    open_cfw_case_busy_delay_alt(2U);
#define OPEN_CFW_CASE_CALL_NOOP(address) open_cfw_case_hook_##address();
    OPEN_CFW_CASE_NOOP_HOOKS(OPEN_CFW_CASE_CALL_NOOP)
#undef OPEN_CFW_CASE_CALL_NOOP
    open_cfw_case_forward_action(action);
    open_cfw_case_run_pair(action, action);
    if (action_count != 3U) return 8;
    open_cfw_case_command_a2_clear(command);
    if (command_first != 0xA2U || command_second != 0U) return 9;
    open_cfw_case_command_a2_set(command);
    if (command_first != 0xA2U || command_second != 1U) return 10;
    if (open_cfw_case_invoke_mode_one(mode_action, 4U, 5U) != 0) return 11;
    record[0] = 9U;
    if (open_cfw_case_invoke_byte(byte_action, 7U, record) != 0) return 12;
    open_cfw_case_transform_word(&index, 0x12345678U, transform);
    if (index != (0x12345678U ^ 0x55AA55AAU)) return 13;
    open_cfw_case_transform_word_alt(&index, 0x87654321U, transform);
    if (index != (0x87654321U ^ 0x55AA55AAU)) return 14;
    {
        int32_t token = -37;
        open_cfw_case_run_if_token(&token, -37, action);
        open_cfw_case_run_if_token(&token, 0, action);
    }
    if (action_count != 4U) return 15;
    open_cfw_case_dispatch_resource(dispatch, 0x1234U, 1U, 2U);
    if (dispatch_resource != 0x1234U || dispatch_values[0] != 1U ||
        dispatch_values[1] != 2U || dispatch_values[2] != 0U) return 16;
    open_cfw_case_dispatch_resource4(dispatch, 0x5678U, 3U, 4U, 5U);
    if (dispatch_resource != 0x5678U || dispatch_values[0] != 3U ||
        dispatch_values[1] != 4U || dispatch_values[2] != 5U) return 17;
    open_cfw_case_route_boolean(1, action, NULL);
    open_cfw_case_route_boolean_alt(0, NULL, action);
    if (action_count != 6U) return 18;
    emitted_bits = 0U;
    emitted_count = 0U;
    open_cfw_case_emit_bits(0xA5U, 0, emit);
    if (emitted_count != 8U || emitted_bits != 0xA5U) return 19;
    emitted_bits = 0U;
    emitted_count = 0U;
    open_cfw_case_emit_bits_alt(0x55U, 1, emit);
    if (emitted_count != 7U || emitted_bits != 0x55U) return 20;
    open_cfw_case_nested_delay(2, 3);
    memset(context, 0, sizeof(context));
    if (!open_cfw_case_context_word38_is_zero(context)) return 21;
    context[0x38U] = 1U;
    if (open_cfw_case_context_word38_is_zero(context)) return 22;
    index = 0x12345678U;
    if (open_cfw_case_read_word_protected(&index, action, action) != index ||
        action_count != 8U) return 23;
    record[1] = 0U;
    open_cfw_case_run_guarded(record, action);
    if (record[1] != 0U || action_count != 9U) return 24;
    memset(record, 0, sizeof(record));
    notify_count = 0U;
    open_cfw_case_transition_word4(record, 1U, notify);
    open_cfw_case_transition_word4(record, 1U, notify);
    open_cfw_case_transition_word4_alt(record, 0U, notify);
    open_cfw_case_transition_word8(record, 1U, notify);
    open_cfw_case_transition_word8_alt(record, 0U, notify);
    if (notify_count != 4U) return 25;
    memset(profile_values, 0, sizeof(profile_values));
    open_cfw_case_write_profile_three(write_index);
    if (profile_values[7] != 0x20U || profile_values[6] != 0x81U ||
        profile_values[5] != 3U || profile_values[3] != 0xFFU) return 26;
    open_cfw_case_write_profile_four(write_index);
    if (profile_values[4] != 0xFFU) return 27;
    record[0] = 0U;
    if (open_cfw_case_select_mask(record, 0x1111U, read_mask) != 0x10U ||
        mask_resource != 0x1111U || mask_value != 0x10U) return 28;
    open_cfw_case_write_selected_mask(record, 0x2222U, 3U, write_mask);
    if (mask_resource != 0x2222U || mask_value != (8U ^ 3U)) return 29;
    record[0] = 1U;
    open_cfw_case_write_selected_mask_alt(record, 0x3333U, 5U, write_mask);
    if (mask_resource != 0x3333U || mask_value != (8U ^ 5U)) return 30;
    open_cfw_case_forward_resource(record, resource_action);
    if (resource_seen != record) return 31;
    record[1] = 0U;
    if (open_cfw_case_run_guarded_status(record, action) != 0 ||
        record[1] != 0U || action_count != 10U) return 32;
    open_cfw_case_read_mask4(0x4444U, read_mask);
    if (mask_resource != 0x4444U || mask_value != 4U) return 33;
    open_cfw_case_read_mask8(0x5555U, read_mask);
    if (mask_resource != 0x5555U || mask_value != 8U) return 34;
    open_cfw_case_write_mask4_set(0x6666U, write_mask);
    if (mask_resource != 0x6666U || mask_value != (4U ^ 1U)) return 35;
    open_cfw_case_write_mask4_clear(0x7777U, write_mask);
    if (mask_value != 4U) return 36;
    open_cfw_case_write_mask8_set(0x8888U, write_mask);
    if (mask_value != (8U ^ 1U)) return 37;
    open_cfw_case_write_mask8_clear(0x9999U, write_mask);
    if (mask_value != 8U) return 38;
    open_cfw_case_dispatch_tagged(dispatch, 0xABCDU, 6U, 7U, 8U);
    if (dispatch_resource != 0xABCDU || dispatch_values[0] != 6U ||
        dispatch_values[1] != 7U || dispatch_values[2] != 8U) return 39;
    open_cfw_case_route_parity(1U, action, NULL);
    open_cfw_case_route_parity_alt(3U, NULL, action);
    if (action_count != 12U) return 40;
    memset(context, 0xFF, sizeof(context));
    open_cfw_case_reset_timer_fields(context, action);
    if (context[0x56U] != 0U || context[0x57U] != 0U ||
        context[0x5EU] != 0U || context[0x5FU] != 0U ||
        action_count != 13U) return 41;
    {
        const uint8_t encoded[3] = {0x23U, 0xAAU, 0xBBU};
        uint8_t decoded[3] = {0U};
        if (open_cfw_case_expand_runs(
                encoded, sizeof(encoded), decoded, sizeof(decoded)) != 0 ||
            decoded[0] != 0xAAU || decoded[1] != 0xBBU ||
            decoded[2] != 0U) return 42;
    }
    if (open_cfw_case_classify_status(fill_status) != 1U ||
        open_cfw_case_classify_status(NULL) != 2U) return 43;
    {
        uint8_t shifts[32] = {0U};
        shifts[12] = 4U;
        if (open_cfw_case_shift_selected(
                0x12345678U, 0x3000U, shifts, 8U) != 0x01234567U)
            return 44;
    }
    index = 0U;
    if (open_cfw_case_query_low_byte(&index, 0U, query_word) != 0 ||
        index != 0xCDU) return 45;
    {
        uint32_t cursor_record[17] = {0U};
        cursor_record[0] = 100U;
        cursor_record[2] = 120U;
        cursor_record[3] = 110U;
        cursor_record[16] = 5U;
        open_cfw_case_advance_cursor(cursor_record, 7U, publish_cursor);
        if (cursor_record[3] != 115U || cursor_argument != 7U ||
            cursor_value != 115U) return 46;
        open_cfw_case_advance_cursor(cursor_record, 8U, publish_cursor);
        if (cursor_record[3] != 100U || cursor_argument != 8U ||
            cursor_value != 100U) return 47;
    }
    {
        const open_cfw_case_pulse_ops pulse_ops = {
            mask4_set, mask4_clear, mask8_set, mask8_clear,
            word4_primary, word4_alternate, counted_delay
        };
        event_count = 0U;
        open_cfw_case_pulse4_short(&pulse_ops);
        open_cfw_case_pulse8_short(&pulse_ops);
        open_cfw_case_pulse4_long(&pulse_ops);
        open_cfw_case_pulse8_long(&pulse_ops);
        open_cfw_case_pulse4_extended(&pulse_ops);
        open_cfw_case_pulse8_extended(&pulse_ops);
        if (event_count != 38U || event_log[0] != 'a' ||
            event_log[1] != 'p' || event_log[4] != 's' ||
            event_log[6] != 'c' || event_log[7] != 'q' ||
            event_log[29] != 'x' || event_log[37] != 'c') return 48;
        event_count = 0U;
        open_cfw_case_pulse4_train_pre_delay(&pulse_ops);
        if (event_count != 46U || event_log[0] != 'a' ||
            event_log[3] != 'x' || event_log[45] != 'a') return 52;
        event_count = 0U;
        open_cfw_case_pulse4_train(&pulse_ops);
        if (event_count != 45U || event_log[3] != 'b' ||
            event_log[44] != 'a') return 53;
        event_count = 0U;
        open_cfw_case_pulse8_double_train(&pulse_ops);
        if (event_count != 28U || event_log[0] != 'c' ||
            event_log[14] != 'c' || event_log[15] != 's' ||
            event_log[27] != 'c') return 54;
    }
    {
        const open_cfw_case_serial_line_ops line_ops = {
            clock_write, data_write, sample, line_delay
        };
        event_count = 0U;
        open_cfw_case_serial_preamble(&line_ops);
        open_cfw_case_serial_ack(&line_ops);
        open_cfw_case_serial_start(&line_ops);
        open_cfw_case_serial_stop(&line_ops);
        if (event_count != 28U || event_log[0] != 'c' ||
            event_log[2] != 'd' || event_log[26] != 'D') return 49;
        event_count = 0U;
        sample_bits = 0xA5U;
        sample_count = 0U;
        if (open_cfw_case_serial_read_byte(&line_ops) != 0xA5U ||
            sample_count != 8U) return 50;
        event_count = 0U;
        open_cfw_case_serial_write_byte(&line_ops, 0xA5U);
        if (event_count != 50U || event_log[0] != 'D' ||
            event_log[6] != 'd' || event_log[48] != 'D') return 51;
    }
    if (!open_cfw_case_query_command_a2_is_one(
            UINT32_C(0x123456AA), query_command)) return 55;
    {
        volatile uint32_t clear_register = 0U;
        action_count = 0U;
        open_cfw_case_clear_irq(5, &clear_register, action, action);
        if (clear_register != 0x20U || action_count != 2U) return 56;
        open_cfw_case_clear_irq(-1, &clear_register, action, action);
        if (action_count != 2U) return 57;
    }
    {
        volatile uint32_t first_status = 0x12U;
        volatile uint32_t second_status = 0x30U;
        mask_action_value[0] = 0U;
        mask_action_value[1] = 0U;
        open_cfw_case_dispatch_pending(
            &first_status, &second_status, 0x10U,
            first_mask_action, second_mask_action);
        if (first_status != 0x10U || second_status != 0x10U ||
            mask_action_value[0] != 0x10U ||
            mask_action_value[1] != 0x10U) return 58;
    }
    {
        uint8_t ready_context[0x2AU] = {0U};
        volatile uint32_t controller[0x60U / 4U] = {0U};
        resource_seen = NULL;
        controller[0x50U / 4U] = 4U;
        open_cfw_case_mark_controller_ready(
            ready_context, controller, resource_action);
        if (ready_context[0x29U] != 1U ||
            controller[0x5CU / 4U] != 4U ||
            resource_seen != ready_context) return 59;
    }
    fake_tick = 10U;
    open_cfw_case_wait_elapsed(3U, 2U, read_tick);
    if (fake_tick != 16U) return 60;
    {
        uint8_t controller_context[0x8CU] = {0U};
        volatile uint32_t control_register = UINT32_C(0xFFFFFFFF);
        if (open_cfw_case_guarded_controller_disable(
                controller_context, &control_register) != 0U ||
            controller_context[0x84U] != 0U ||
            controller_context[0x88U] != 0x20U ||
            control_register != UINT32_C(0xDFFFFFFF)) return 61;
        controller_context[0x84U] = 1U;
        if (open_cfw_case_guarded_controller_disable(
                controller_context, &control_register) != 2U) return 62;
    }
    action_count = 0U;
    if (open_cfw_case_start_scheduler(1, 3U, action) != -6 ||
        open_cfw_case_start_scheduler(0, 0U, action) != -4 ||
        open_cfw_case_start_scheduler(1, 0U, action) != 0 ||
        action_count != 1U) return 63;
    {
        const open_cfw_case_serial_line_ops line_ops = {
            clock_write, data_write, sample, line_delay
        };
        event_count = 0U;
        sample_bits = 0x80U;
        if (!open_cfw_case_serial_ack_sample(&line_ops) ||
            event_count != 5U || event_log[0] != 'D' ||
            event_log[1] != 'C' || event_log[3] != 'c') return 64;
    }
    {
        uint8_t collected = 0U;
        bit_pattern = 0xA5U;
        bit_index = 0U;
        if (!open_cfw_case_collect_bits(&collected, 0, read_bit) ||
            collected != 0xA5U || bit_index != 8U) return 65;
    }
    {
        uint8_t cache[4] = {0U};
        open_cfw_case_update_cached_byte(cache, 2U, 5U, 3U, update_byte);
        if (cache[2] != 8U) return 66;
        open_cfw_case_update_cached_byte(cache, 2U, 8U, 4U, update_byte);
        if (cache[2] != 8U) return 67;
    }
    {
        uint8_t stage_context[0x5CU] = {0U};
        stage_context[0x59U] = 1U;
        if (open_cfw_case_guarded_two_stage(
                stage_context, stage_first, stage_second) != 0 ||
            stage_context[0x54U] != 0U || stage_context[0x58U] != 1U ||
            stage_context[0x59U] != 0U) return 68;
    }
    {
        uint32_t positive_registers[4] = {UINT32_C(0xFFFFFFFF), 0U, 0U, 0U};
        uint8_t negative_registers[36] = {0U};
        open_cfw_case_configure_two_bit_field(
            1U, 2U, positive_registers, negative_registers);
        if (positive_registers[0] != UINT32_C(0xFFFF80FF)) return 69;
        open_cfw_case_configure_two_bit_field(
            UINT32_C(0xFFFFFFFF), 3U, positive_registers,
            negative_registers);
        if (negative_registers[32] != 0U ||
            negative_registers[35] != 0xC0U) return 70;
    }
    selector_attempts = 0U;
    event_count = 0U;
    if (open_cfw_case_retry_selector8(
            attempt_selector, counted_delay) != 0 ||
        selector_attempts != 2U || event_count != 2U ||
        event_log[0] != 'x' || event_log[1] != 'x') return 71;
    {
        volatile uint32_t status_register = UINT32_C(0xFFFFFFFF);
        fake_tick = 0U;
        wait_status_register = &status_register;
        if (open_cfw_case_wait_status_bit5(
                &status_register, read_wait_tick) != 0 ||
            (status_register & (1U << 5U)) == 0U) return 72;
        wait_status_register = NULL;
    }
    {
        uint8_t critical_record[0x29U] = {0U};
        uint32_t atomic_value = UINT32_C(0x12345678);
        critical_record[0x1CU] = 0x78U;
        critical_record[0x1DU] = 0x56U;
        critical_record[0x1EU] = 0x34U;
        critical_record[0x1FU] = 0x12U;
        critical_record[0x28U] = 1U;
        action_count = 0U;
        if (open_cfw_case_critical_read_word28(
                critical_record, action, action, action) !=
                UINT32_C(0x12345678) ||
            !open_cfw_case_critical_read_flag40(
                critical_record, action, action, action) ||
            action_count != 4U) return 73;
        if (open_cfw_case_atomic_clear_word(
                &atomic_value, 0x5600U, action, action, action) !=
                UINT32_C(0x12345678) ||
            atomic_value != UINT32_C(0x12340078) ||
            action_count != 6U) return 74;
        (void)open_cfw_case_atomic_clear_word(
            NULL, 1U, action, action, action);
        if (action_count != 7U) return 75;
    }
    {
        uint8_t field_context[0x8CU] = {0U};
        volatile uint32_t controller[3] = {
            UINT32_C(0xFFFFFFFF), 0U, UINT32_C(0xFFFFFFFF)};
        resource_seen = NULL;
        if (open_cfw_case_guarded_controller_field_high(
                field_context, controller, UINT32_C(0xA0000000),
                resource_action) != 0 ||
            controller[0] != UINT32_C(0xFFFFFFFF) ||
            controller[2] != UINT32_C(0xBFFFFFFF) ||
            resource_seen != field_context) return 76;
        if (open_cfw_case_guarded_controller_field_mid(
                field_context, controller, UINT32_C(0x0C000000),
                resource_action) != 0 ||
            controller[2] != UINT32_C(0xBDFFFFFF)) return 77;
    }
    status_action_count = 0U;
    if (open_cfw_case_start_validated(
            0U, query_a0, status_start, status_finalize) != 0 ||
        status_action_count != 2U) return 78;
    event_count = 0U;
    open_cfw_case_toggle_lines_three(clock_write, data_write, counted_delay);
    if (event_count != 20U || event_log[0] != 'C' ||
        event_log[18] != 'c' || event_log[19] != 'd') return 79;
    memset(configured_record, 0xFF, sizeof(configured_record));
    action_count = 0U;
    open_cfw_case_configure_record_and_stop(
        0x1234U, configure_record, action);
    if (dispatch_resource != 0x1234U || configured_record[0] != 0x18U ||
        configured_record[1] != 0x11U || configured_record[2] != 0U ||
        action_count != 1U) return 80;
    {
        uint8_t normalized[0x46U] = {0U};
        normalized[0x44U] = 0xFFU;
        normalized[0x45U] = 0xFFU;
        resource_seen = NULL;
        action_count = 0U;
        open_cfw_case_normalize_context(
            normalized, 7U, 8U, action, action,
            context_dispatch, resource_action);
        if (normalized[0x44U] != 0U || normalized[0x45U] != 0U ||
            resource_seen != normalized || dispatch_values[0] != 7U ||
            dispatch_values[1] != 8U || action_count != 2U) return 81;
    }
    {
        uint8_t reset_context[0x94U];
        volatile uint32_t controller[7] = {
            1U, 2U, 3U, 0U, 0U, 0U, 1U << 5U};
        memset(reset_context, 0xFF, sizeof(reset_context));
        resource_seen = NULL;
        if (open_cfw_case_reset_controller_context(
                reset_context, controller, resource_action) != 0 ||
            controller[0] != 0U || controller[1] != 0U ||
            controller[2] != 0U || reset_context[0x84U] != 0U ||
            reset_context[0x90U] != 0U ||
            resource_seen != reset_context) return 82;
        fake_tick = 0U;
        controller_wait_registers = controller;
        if (open_cfw_case_wait_controller_ready(
                reset_context, controller, read_controller_tick) != 0 ||
            (controller[3] & (1U << 6U)) == 0U) return 83;
        controller_wait_registers = NULL;
        controller[3] = UINT32_C(0xFFFFFFFF);
        controller[6] = 1U << 5U;
        if (open_cfw_case_prepare_controller_wait(
                reset_context, controller, wait_ready_success) != 0 ||
            (controller[3] & (1U << 7U)) != 0U ||
            (controller[6] & (1U << 5U)) == 0U) return 84;
    }
    {
        volatile uint32_t mode_registers[6] = {0U};
        if (open_cfw_case_configure_mode_wait(
                mode_registers, 0x100U, 1U, 1U, divide_value) != 0 ||
            mode_registers[0] != 0x100U) return 85;
        mode_registers[5] = 1U << 10U;
        if (open_cfw_case_configure_mode_wait(
                mode_registers, 0x200U, 0U, 1U, divide_value) != 3)
            return 86;
    }
    {
        register_sequence_count = 0U;
        event_count = 0U;
        open_cfw_case_configure_register_sequence(
            register_write, counted_delay);
        if (register_sequence_count != 14U ||
            register_sequence[0] != 0x13U ||
            register_sequence[1] != 0x90U ||
            register_sequence[12] != 0x1BU ||
            register_sequence[13] != 1U || event_count != 7U)
            return 87;
    }
    {
        uint8_t peripheral[0x49U] = {0U};
        volatile uint32_t controller[5] = {0U};
        peripheral[0] = 0x34U;
        peripheral[1] = 0x12U;
        resource_seen = NULL;
        if (open_cfw_case_initialize_peripheral_context(
                peripheral, resource_action, configure_context) != 0 ||
            resource_seen != (void *)(uintptr_t)0x1234U ||
            peripheral[4] != 0x5AU || peripheral[0x3DU] != 1U ||
            peripheral[0x48U] != 1U) return 88;
        controller[2] = 6U;
        if (open_cfw_case_enable_peripheral_context(
                peripheral, controller, 0xFU, 1) != 0 ||
            controller[0] != 0U || peripheral[0x3DU] != 2U) return 89;
        peripheral[0x3DU] = 1U;
        if (open_cfw_case_enable_peripheral_context(
                peripheral, controller, 0xFU, 0) != 0 ||
            controller[0] != 1U) return 90;
    }
    {
        volatile uint32_t serial_registers[5] = {0U};
        volatile uint32_t error_registers[2] = {0U};
        fake_tick = 0U;
        serial_registers[4] = UINT32_C(0x00030000);
        serial_wait_registers = serial_registers;
        if (open_cfw_case_wait_serial_idle(
                serial_registers, error_registers, 10U, 4U, 0U,
                read_serial_tick) != 0) return 91;
        serial_wait_registers = NULL;
        serial_registers[4] = 4U;
        if (open_cfw_case_wait_serial_idle(
                serial_registers, error_registers, 10U, 4U, 0U,
                read_tick) != 1 || error_registers[1] != 4U) return 92;
    }
    {
        uint32_t state[5] = {0U};
        uint32_t observed = 9U;
        open_cfw_case_probe_ops ops = {
            action, action, action, action, action,
            counted_delay, read_probe_value};
        probe_values[0] = 1U;
        probe_values[1] = 0U;
        probe_values[2] = 0U;
        probe_value_count = 3U;
        probe_value_index = 0U;
        if (open_cfw_case_probe_low_signal(
                state, &observed, 2U, &ops) != 0 ||
            observed != 0U || state[3] != 1U) return 93;
        probe_values[0] = 1U;
        probe_values[1] = 1U;
        probe_values[2] = 0U;
        probe_values[3] = 0U;
        probe_values[4] = 0U;
        probe_value_count = 5U;
        probe_value_index = 0U;
        if (open_cfw_case_probe_high_signal(
                state, &observed, 2U, action, action, counted_delay,
                read_probe_value) != (UINT64_C(1) << 32U) ||
            observed != 1U || state[3] != 1U || state[4] != 1U)
            return 94;
    }
    {
        const uint8_t switch_table[5] = {3U, 1U, 4U, 7U, 9U};
        volatile uint32_t control = 0U;
        action_count = 0U;
        if (open_cfw_case_switch8_offset(2U, switch_table) != 14U ||
            open_cfw_case_switch8_offset(8U, switch_table) != 18U ||
            open_cfw_case_initialize_serial_block(
                &control, 0x20U, initialize_three, action) != 0 ||
            control != 0x20U || action_count != 1U) return 95;
    }
    {
        volatile uint8_t serial_state = 9U;
        serial_word_count = 0U;
        action_count = 0U;
        if (open_cfw_case_serial_write_pair_200(
                0x12U, 0x34U, &serial_state, action, write_serial_word,
                acknowledge_success, action) != 1 ||
            serial_state != 0U || serial_word_count != 3U ||
            serial_words[0] != 200U || serial_words[1] != 0x12U ||
            serial_words[2] != 0x34U || action_count != 2U) return 96;
        serial_word_count = 0U;
        if (open_cfw_case_serial_write_pair_70(
                1U, 2U, &serial_state, action, write_serial_word,
                acknowledge_success, action) != 1 ||
            serial_words[0] != 0x70U) return 97;
    }
    {
        uint8_t transfer_context[0x90U] = {0U};
        volatile uint32_t controller[3] = {0U, 1U << 23U, 0xFFFFFFFFU};
        transfer_context[8] = 0x00U;
        transfer_context[9] = 0x20U;
        transfer_context[0x8CU] = 0x20U;
        action_count = 0U;
        if (open_cfw_case_start_context_transfer(
                transfer_context, controller, 1U, 1, action, action,
                transfer_success) != 0 ||
            (controller[0] & (1U << 26U)) == 0U || action_count != 2U)
            return 98;
        transfer_context[0x6CU] = 1U;
        open_cfw_case_reset_context_transfer(
            transfer_context, controller, UINT32_C(0xFFFFFF00),
            action, action);
        if (controller[2] != UINT32_C(0xFFFFFF00) ||
            transfer_context[0x6CU] != 0U ||
            transfer_context[0x8CU] != 0x20U) return 99;
    }
    {
        uint8_t expected[80];
        int32_t stable = 0;
        uint32_t index;
        for (index = 0U; index < 80U; ++index) expected[index] = (uint8_t)index;
        if (open_cfw_case_verify_selector_bank(expected, selector_read) != 0)
            return 100;
        stable_read_count = 0U;
        if (open_cfw_case_read_stable_u16(
                0x99U, &stable, stable_read, counted_delay) != 0 ||
            stable != 0x1234 || stable_read_count != 2U) return 101;
    }
    {
        volatile uint32_t registers[21] = {0U};
        uint32_t descriptor[7] = {0U, 4U, 0U, 0U, 0U, 0U, 0U};
        volatile uint32_t first_control = UINT32_C(0xFFFFFFFF);
        volatile uint32_t second_control = UINT32_C(0xFFFFFFFF);
        registers[19] = UINT32_C(0x00123456);
        open_cfw_case_build_register_descriptor(
            descriptor, registers, 0xCCU, read_first_value,
            read_second_value);
        if (descriptor[0] != 7U || descriptor[2] != 0x56U ||
            descriptor[3] != 0x12U || descriptor[4] != 0xAAU ||
            descriptor[5] != 0xCCU || descriptor[6] != 0xBBU)
            return 102;
        serial_word_count = 0U;
        open_cfw_case_release_peripheral(
            1U, 1U, 2U, &first_control, &second_control, 0x400U,
            command, write_serial_word);
        if ((first_control & 0x4000U) != 0U ||
            command_first != UINT32_C(0x50000000) ||
            command_second != 0x600U || serial_words[0] != 0x1BU)
            return 103;
    }
    {
        uint32_t channel[10] = {0U};
        resource_seen = NULL;
        if (open_cfw_case_initialize_channel_profile(
                channel, 0x55U, stage_first, context_pair_success,
                resource_action, action) != 0 ||
            channel[0] != 0x55U || channel[3] != 0x7FU ||
            channel[4] != 0x1FU || channel[8] != UINT32_C(0x40000000) ||
            resource_seen != channel) return 104;
    }
    {
        uint8_t controller_context[64] = {0U};
        open_cfw_case_controller_init_ops ops = {
            resource_action, status_finalize, context_value_success,
            context_value_success, stage_first, context_transfer_success,
            action};
        resource_seen = NULL;
        status_action_count = 0U;
        if (open_cfw_case_initialize_controller_profile(
                controller_context, 0x1111U, 0x2222U, 8U, 1, 1,
                0x77U, &ops) != 0 ||
            controller_context[0] != 0x11U ||
            controller_context[4] != 0x22U ||
            controller_context[20] != 8U ||
            controller_context[40] != 0x10U ||
            controller_context[61] != 0x10U ||
            dispatch_values[0] != 0x77U || dispatch_values[1] != 1U)
            return 105;
    }
    {
        uint8_t transport[80];
        descriptor_seen = 0U;
        resource_seen = NULL;
        if (open_cfw_case_initialize_transport_record(
                transport, 3U, 0x99U, status_finalize,
                context_descriptor_success, resource_action, action) != 0 ||
            transport[0] != 3U || transport[20] != 4U ||
            transport[0x1AU] != 1U || transport[28] != 1U ||
            transport[52] != 5U || descriptor_seen != 0x99U ||
            resource_seen != transport) return 106;
    }
    {
        uint8_t flag_context[0x60U] = {0U};
        volatile uint32_t controller[3] = {1U, 0U, 1U << 2U};
        fake_tick = 0U;
        if (open_cfw_case_wait_controller_flag2(
                flag_context, controller, UINT32_C(0xFFFFFFFF),
                query_nonzero, read_tick) != 1 ||
            flag_context[0x58U] != 0x10U ||
            flag_context[0x5CU] != 1U) return 107;
        memset(flag_context, 0, sizeof(flag_context));
        controller[2] = 1U;
        fake_tick = 0U;
        if (open_cfw_case_start_controller_flag0(
                flag_context, controller, UINT32_C(0xFFFFFFFF),
                status_start, read_tick) != 1 ||
            controller[0] != 3U || flag_context[0x58U] != 0x10U)
            return 108;
    }
    {
        volatile uint32_t clock_control = 0U;
        volatile uint32_t enable_control = 0U;
        serial_word_count = 0U;
        memset(configured_record, 0, sizeof(configured_record));
        open_cfw_case_configure_irq_resource(
            4U, 4U, &clock_control, &enable_control, configure_record,
            dispatch, write_serial_word);
        if (clock_control != (1U << 20U) || enable_control != 1U ||
            configured_record[0] != 0x10U || configured_record[1] != 3U ||
            serial_words[0] != 0xCU) return 109;
        descriptor_seen = 0U;
        if (open_cfw_case_configure_controller_irq(
                5U, 5U, &clock_control, &enable_control, record_success,
                dispatch, write_serial_word, action) != 0 ||
            descriptor_seen != 0x20000U || dispatch_values[2] != 0U)
            return 110;
    }
    {
        descriptor_seen = 0U;
        resource_seen = (void *)(uintptr_t)1U;
        if (open_cfw_case_initialize_application_profile(
                context_value_success, record_success,
                context_pair_success, action) != 0 ||
            descriptor_seen != 10U || dispatch_values[0] != 2U)
            return 111;
    }
    {
        uint8_t channel_context[0x94U] = {0U};
        volatile uint32_t controller[1] = {(1U << 3U) | (1U << 2U)};
        fake_tick = 9U;
        if (open_cfw_case_wait_controller_channels(
                channel_context, controller, 0x33U, 0x44U, read_tick,
                wait_channel_success) != (UINT64_C(0x44) << 32U) ||
            channel_context[0x88U] != 0x20U ||
            channel_context[0x8CU] != 0x20U ||
            dispatch_values[0] != 0x400000U ||
            dispatch_values[2] != 0x44U) return 112;
    }
    {
        volatile uint8_t serial_state = 9U;
        uint8_t output[4] = {0U};
        open_cfw_case_serial_bus_ops ops = {
            action, write_serial_word, acknowledge_success,
            read_serial_value, action, action, action};
        serial_read_values[0] = 0x11U;
        serial_read_values[1] = 0x22U;
        serial_read_values[2] = 0x33U;
        serial_read_index = 0U;
        serial_word_count = 0U;
        action_count = 0U;
        if (open_cfw_case_serial_read_200(
                7U, output, 3U, &serial_state, &ops) != 1 ||
            serial_state != 0U || serial_word_count != 3U ||
            serial_words[0] != 200U || serial_words[1] != 7U ||
            serial_words[2] != 0xC9U || output[0] != 0x11U ||
            output[2] != 0x33U || action_count != 6U) return 113;
        serial_read_index = 0U;
        serial_word_count = 0U;
        if (open_cfw_case_serial_read_70(
                8U, output, 1U, &serial_state, &ops) != 1 ||
            serial_words[0] != 0x70U || serial_words[2] != 0x71U)
            return 114;
    }
    {
        uint32_t sample_resource = 0xAAU;
        uint32_t registers[4] = {0U, 0U, 0U, 0U};
        uint32_t index;
        for (index = 0U; index < 8U; ++index)
            sample_values8[index] = index + 1U;
        sample_index8 = 0U;
        resource_seen = NULL;
        if (open_cfw_case_trimmed_average8(
                &sample_resource, resource_action, context_value_success,
                read_resource_value, resource_action) != 4U ||
            sample_index8 != 8U || resource_seen != &sample_resource)
            return 115;
        registers[0] = 2U << 11U;
        if (open_cfw_case_derive_clock(registers, 48000000U) != 12000000U)
            return 116;
        registers[2] = 2U << 3U;
        registers[3] = (3U << 8U) | (1U << 4U);
        if (open_cfw_case_derive_clock(registers, 48000000U) != 72000000U)
            return 117;
    }
    {
        uint8_t start_context[42] = {0U};
        volatile uint32_t controller[13] = {0U};
        uint32_t profile[6] = {0xA0U, 0x30U, 0xB0U,
                               0x200U, 0xC0U, 0x80U};
        controller[6] = (1U << 10U) | (1U << 14U);
        fake_tick = 0U;
        start_controller_registers = controller;
        if (open_cfw_case_start_controller(
                start_context, controller, read_start_controller_tick) != 0 ||
            start_context[40] != 0U || start_context[41] != 1U ||
            controller[9] != 0xFFU || controller[6] != 0U)
            return 118;
        controller[0] = UINT32_C(0xFFFFFFFF);
        open_cfw_case_apply_controller_profile(
            controller, profile, 1, 1, 1);
        if (controller[0] != UINT32_C(0xFFFFFEBF) ||
            controller[10] != 0xA0U || controller[11] != 0xB0U ||
            controller[12] != 0xC0U || controller[5] != 1U)
            return 119;
    }
    {
        uint32_t source[64];
        uint32_t destination[64] = {0U};
        volatile uint32_t controller[6] = {0U};
        uint32_t index;
        for (index = 0U; index < 64U; ++index) source[index] = index + 7U;
        action_count = 0U;
        restored_irq_state = -1;
        open_cfw_case_copy64_protected(
            destination, source, controller, status_true, status_true,
            action, restore_irq);
        if (destination[63] != 70U ||
            (controller[5] & 0x40000U) == 0U || action_count != 1U ||
            restored_irq_state != 1) return 120;
    }
    {
        uint8_t state[8] = {0U};
        volatile uint32_t controller[6] = {0U, 0U, 0U, 0U, 0U, 2U};
        uint32_t operation[4] = {0U, 0x55U, 3U, 2U};
        uint32_t failed = 0U;
        uint32_t source[64] = {9U};
        uint32_t destination[64] = {0U};
        wait_call_count = 0U;
        if (open_cfw_case_run_controller_range(
                state, controller, operation, &failed, wait_success,
                write_serial_word, pair_action) != 0 ||
            failed != UINT32_MAX || command_first != 0x55U ||
            command_second != 4U || controller[5] != 0U ||
            wait_call_count != 3U || state[0] != 0U) return 121;
        wait_call_count = 0U;
        controller[5] = 1U;
        if (open_cfw_case_copy_controller_words(
                state, controller, 1U, destination, source,
                wait_success, copy_one) != 0 || destination[0] != 9U ||
            controller[5] != 0U || wait_call_count != 2U) return 122;
    }
    {
        uint8_t context[0x8CU] = {0U};
        volatile uint32_t controller[3] = {
            UINT32_MAX, UINT32_MAX, UINT32_MAX};
        context[40] = 1U;
        resource_seen = NULL;
        if (open_cfw_case_prepare_controller_context(
                context, controller, resource_action, stage_first,
                resource_action, stage_first) != 0 ||
            context[0x88U] != 0x24U || resource_seen != context ||
            (controller[0] & 1U) == 0U ||
            controller[1] != UINT32_C(0xFFFFB7FF) ||
            controller[2] != UINT32_C(0xFFFFFFD5)) return 123;
    }
    {
        volatile uint32_t enable = 0U;
        volatile uint32_t route = 0U;
        uint32_t profile[7] = {0U};
        uint32_t selected = UINT32_MAX;
        serial_word_count = 0U;
        open_cfw_case_enable_interrupt_source(
            &enable, &route, 0x20000U, dispatch, initialize_three);
        if (enable != 1U || route != 0x20000U ||
            dispatch_resource != UINT32_C(0xFFFFFFFE)) return 124;
        if (open_cfw_case_initialize_interrupt_path(
                2U, 0x55U, 0x66U, 100U, 4U, 1, profile, &route,
                &selected, stage_first, stage_first, write_serial_word,
                dispatch) != 0 || profile[0] != 0x55U ||
            profile[1] != 49U || profile[3] != 0x66U || selected != 2U ||
            serial_words[0] != 0x16U) return 125;
    }
    {
        uint8_t context[42] = {0U};
        volatile uint32_t controller[10] = {0U};
        context[8] = 1U;
        context[20] = 2U;
        context[28] = 4U;
        context[16] = 5U;
        context[12] = 6U;
        context[24] = 8U;
        context[32] = 0x10U;
        context[36] = 0x20U;
        if (open_cfw_case_activate_controller(
                context, controller, UINT32_MAX, resource_action,
                stage_first, stage_first) != 0 || context[41] != 1U ||
            controller[4] != 0x60005U || controller[6] != 0x3FU ||
            controller[9] != 0xFFU) return 126;
    }
    {
        uint8_t bank[80];
        uint32_t index;
        for (index = 0U; index < 80U; ++index) bank[index] = (uint8_t)index;
        selector_write_count = 0U;
        if (open_cfw_case_program_selector_bank(
                bank, attempt_selector, write_selector_byte,
                counted_delay, read_selector_byte) != 0 ||
            selector_write_count != 84U) return 127;
    }
    {
        open_cfw_case_event_waiter second = {
            UINT32_C(0x04000000) | 3U, NULL};
        open_cfw_case_event_waiter first = {
            UINT32_C(0x01000000) | 1U, &second};
        open_cfw_case_event_group group = {0U, &first};
        waiter_unblock_count = 0U;
        action_count = 0U;
        if (open_cfw_case_event_group_set_bits(
                &group, 3U, action, unblock_waiter, action, action) != 2U ||
            waiter_unblock_count != 2U || action_count != 2U ||
            dispatch_values[0] != UINT32_C(0x02000003)) return 128;
    }
    {
        uint8_t context[0x90U] = {0U};
        volatile uint32_t controller[10] = {0U};
        uint8_t output[2] = {0U};
        uint8_t *cursor = output;
        controller[0] = UINT32_MAX;
        controller[2] = UINT32_MAX;
        controller[9] = 0x1234U;
        context[0x8CU] = 0x22U;
        context[0x5EU] = 1U;
        context[0x60U] = 0xFFU;
        context[0x61U] = 0xFFU;
        context[0x6CU] = 1U;
        context[0x5CU] = 0x77U;
        finalized_short = 0U;
        resource_seen = NULL;
        open_cfw_case_receive_u16(
            context, controller, &cursor, status_true, status_true,
            restore_irq, resource_action, finalize_short);
        if (output[0] != 0x34U || output[1] != 0x12U ||
            cursor != output + 2U || context[0x8CU] != 0x20U ||
            finalized_short != 0x77U || resource_seen != context)
            return 129;
        context[0x8CU] = 0x22U;
        context[0x5EU] = 1U;
        context[0x6CU] = 0U;
        cursor = output;
        open_cfw_case_receive_u8(
            context, controller, &cursor, status_true, status_true,
            restore_irq, resource_action, finalize_short);
        if (cursor != output + 1U || resource_seen != context) return 130;
    }
    {
        uint8_t context[0x60U] = {0U};
        volatile uint32_t controller[8] = {0U};
        fake_tick = 0U;
        if (open_cfw_case_start_peripheral(
                context, controller, 0x10U, 0, 0U, 1U,
                stage_first, read_tick) != 1 ||
            context[0x58U] != 0x10U || context[0x5CU] != 1U)
            return 131;
        memset(context, 0, sizeof(context));
        controller[0] = 4U;
        fake_tick = 0U;
        if (open_cfw_case_wait_peripheral(
                context, controller, 10U, read_tick,
                stage_first, stage_first) != 0 || controller[0] != 0xCU ||
            context[0x59U] != 2U) return 132;
    }
    {
        volatile uint32_t controller[12];
        open_cfw_case_pin_state pins;
        uint32_t index;
        for (index = 0U; index < 12U; ++index) controller[index] = UINT32_MAX;
        memset(&pins, 0, sizeof(pins));
        pins.ownership[0] = 2U << 8U;
        for (index = 0U; index < 4U; ++index) pins.active[index] = 2U;
        open_cfw_case_release_pins(controller, 2U, 2U, &pins);
        if ((pins.ownership[0] & 0xF00U) != 0U || pins.active[0] != 0U ||
            (controller[1] & 2U) != 0U) return 133;
    }
    {
        volatile uint32_t clock[17] = {0U};
        volatile uint32_t enable = 0U;
        descriptor_seen = 0U;
        serial_word_count = 0U;
        open_cfw_case_configure_resource_irq(
            1U, 1U, 2U, clock, &enable, record_success,
            configure_record, dispatch, write_serial_word, action);
        if ((clock[16] & 0x4000U) == 0U || enable != 1U ||
            configured_record[0] != 0x600U || serial_words[0] != 0x1BU)
            return 134;
    }
    {
        uint8_t context[0x94U] = {0U};
        volatile uint32_t controller[11] = {0U};
        uint16_t input[2] = {0x1AAU, 0x55U};
        uint16_t output[2] = {0U};
        context[8] = 0x00U;
        context[9] = 0x10U;
        context[0x88U] = 0x20U;
        context[0x8CU] = 0x20U;
        wait_call_count = 0U;
        fake_tick = 0U;
        if (open_cfw_case_write_controller_blocking(
                context, controller, input, 2U, 9U, read_tick,
                wait_condition_success) != 0 || controller[10] != 0x55U ||
            context[0x88U] != 0x20U || wait_call_count != 3U)
            return 135;
        controller[9] = 0xABU;
        wait_call_count = 0U;
        if (open_cfw_case_read_controller_blocking(
                context, controller, output, 2U, 9U, read_tick,
                wait_condition_success) != 0 || output[0] != 0xABU ||
            output[1] != 0xABU || context[0x8CU] != 0x20U)
            return 136;
    }
    {
        volatile uint32_t controller[8] = {0U};
        uint32_t options[20] = {0U};
        uint8_t context[0x94U] = {0U};
        options[10] = 0xFFU;
        options[11] = 0x20000U;
        options[17] = 0x100000U;
        options[18] = 0x200000U;
        open_cfw_case_apply_context_options(controller, options);
        if ((controller[1] & 0x20000U) == 0U ||
            (controller[1] & 0x200000U) == 0U) return 137;
        controller[7] = 0x20U;
        fake_tick = 0U;
        if (open_cfw_case_wait_condition(
                context, controller, 0x20U, 0, 0U, 4U, read_tick,
                status_true, status_true, restore_irq) != 0) return 138;
    }
    {
        uint8_t context[0x94U] = {0U};
        volatile uint32_t controller[3] = {0U};
        uint8_t output[4] = {0U};
        uint8_t *cursor = NULL;
        context[8] = 0x00U;
        context[9] = 0x10U;
        context[0x64U] = 0x00U;
        context[0x65U] = 0x00U;
        context[0x66U] = 0x00U;
        context[0x67U] = 0x20U;
        context[0x68U] = 2U;
        open_cfw_case_begin_receive(
            context, controller, &cursor, output, 4U, 0x1FFU,
            1U, 2U, 3U, 4U, status_true, status_true, restore_irq);
        if (cursor != output || context[0x5EU] != 4U ||
            context[0x8CU] != 0x22U || context[0x74U] != 4U ||
            (controller[2] & 0x10000001U) != 0x10000001U) return 139;
    }
    {
        volatile uint32_t clock = 0U;
        volatile uint32_t enable = 0U;
        serial_word_count = 0U;
        open_cfw_case_configure_platform_routes(
            &clock, &enable, 0x600U, 0x700U, 9U, 10U,
            command, configure_record, dispatch, write_serial_word);
        if (clock != 1U || enable != 7U || dispatch_resource != 7U ||
            serial_word_count != 3U || serial_words[2] != 7U) return 140;
    }
    {
        uint32_t configuration[4] = {7U, 1U, 0x300U, 0x4000U};
        volatile uint32_t selector_register = 0U;
        volatile uint32_t clock_registers[4] = {0U};
        uint8_t shifts[64] = {0U};
        uint32_t derived = 0U;
        fake_tick = 0U;
        if (open_cfw_case_configure_clock_path(
                configuration, 1U, &selector_register, clock_registers,
                5U, shifts, 64U, 48000000U, &derived, read_tick,
                initialize_three) != 1 || derived != 24000000U ||
            (clock_registers[2] & 7U) != 1U) return 141;
    }
    {
        uint8_t context[0x60U] = {0U};
        volatile uint32_t controller[46] = {0U};
        uint32_t sample_resource = 0U;
        uint32_t index;
        for (index = 0U; index < 8U; ++index) sample_values8[index] = 8U;
        sample_index8 = 0U;
        fake_tick = 0U;
        (void)sample_resource;
        if (open_cfw_case_calibrate_controller(
                context, controller, 0xFU, 20U, stage_first,
                stage_first, read_resource_value, read_tick) !=
                    (UINT64_C(8) << 32U) ||
            (controller[45] & 0x7FU) != 8U || context[0x54U] != 0U ||
            sample_index8 != 8U) return 142;
    }
    {
        open_cfw_case_init_entry entries[1];
        const uint8_t packed[4] = {0x33U, 0xAAU, 0xBBU, 0U};
        uint8_t output[4] = {0xFFU, 0xFFU, 0xFFU, 0xFFU};
        entries[0].first = 1U;
        entries[0].second = 2U;
        entries[0].third = 3U;
        entries[0].initialize = init_entry;
        if (open_cfw_case_boot_initialize(
                entries, entries + 1U, packed, packed + 4U,
                output, output + 4U, action) != 0 ||
            dispatch_values[2] != 3U || output[0] != 0xAAU ||
            output[1] != 0xBBU || output[2] != 0U) return 143;
    }
    {
        open_cfw_case_wire_ops ops = {
            action, action, wire_emit, wire_route, wire_check,
            wire_parity_marker, wire_collect};
        uint8_t data[3] = {1U, 2U, 3U};
        uint8_t output[3] = {0U};
        uint32_t error = 0U;
        wire_collect_index = 0U;
        if (open_cfw_case_wire_write_register(
                0x40U, 1U, data, 3U, &error, &ops) !=
                    ((UINT64_C(1) << 32U) | 1U) || error != 0U)
            return 144;
        wire_collect_index = 0U;
        if (open_cfw_case_wire_read_register(
                0x40U, 1U, output, 3U, &error, &ops) != 1 ||
            output[2] != 0xA2U) return 145;
        wire_collect_index = 0U;
        if (open_cfw_case_wire_exchange_register(
                0x20U, 2U, output, 2U, &error, &ops) != 1 ||
            output[1] != 0xA1U) return 146;
    }
    {
        open_cfw_case_frame_parser parser;
        memset(&parser, 0, sizeof(parser));
        frame_notify_value = 0U;
        open_cfw_case_process_frame_byte(
            &parser, 'D', frame_validate, frame_read,
            status_finalize, frame_notify);
        open_cfw_case_process_frame_byte(
            &parser, '\n', frame_validate, frame_read,
            status_finalize, frame_notify);
        if (frame_notify_value != 8U || parser.length != 0U) return 147;
        pulse_write_count = 0U;
        open_cfw_case_emit_probe_train(
            0x80000U, 0x200U, 10U, pulse_write,
            counted_delay, counted_delay);
        if (pulse_write_count != 51U) return 148;
    }
    {
        uint8_t context[0x94U] = {0U};
        volatile uint32_t controller[10] = {0U};
        uint8_t output[4] = {0U};
        uint8_t *cursor = output;
        controller[7] = 1U << 5U;
        controller[9] = 0x1234U;
        context[0x8CU] = 0x22U;
        context[0x5CU] = 1U;
        context[0x5EU] = 1U;
        context[0x60U] = 0xFFU;
        context[0x61U] = 0xFFU;
        open_cfw_case_drain_receive_u16(
            context, controller, &cursor, 4U, 7U,
            resource_action, resource_action, finalize_short);
        if (cursor != output + 2U || output[0] != 0x34U ||
            output[1] != 0x12U || context[0x8CU] != 0x20U)
            return 149;
        cursor = output;
        context[0x8CU] = 0x22U;
        context[0x5EU] = 1U;
        open_cfw_case_drain_receive_u8(
            context, controller, &cursor, 4U, 7U,
            resource_action, resource_action, finalize_short);
        if (cursor != output + 1U) return 150;
    }
    {
        uint8_t context[0x64U] = {0U};
        volatile uint32_t controller[11] = {0U};
        volatile uint32_t clock_control = 0U;
        uint32_t descriptor[3] = {4U, 1U, UINT32_MAX};
        context[28] = 8U;
        if (open_cfw_case_configure_pin_policy(
                context, controller, descriptor, &clock_control,
                0x1C00000U, 0x80000001U, 0x80000002U,
                0x80000004U, stage_first, counted_delay) != 0 ||
            context[0x54U] != 0U || (controller[5] & 0x400U) == 0U)
            return 151;
    }
    {
        uint32_t configuration[14] = {0U};
        volatile uint32_t clock[16] = {0U};
        volatile uint32_t auxiliary[9] = {0U};
        volatile uint32_t oscillator = 0U;
        fake_tick = 0U;
        if (open_cfw_case_configure_system_clock(
                configuration, clock, auxiliary, &oscillator, 4U,
                read_tick, initialize_three) != 0) return 152;
        configuration[0] = 1U;
        configuration[1] = 1U;
        if (open_cfw_case_configure_system_clock(
                configuration, clock, auxiliary, &oscillator, 4U,
                read_tick, initialize_three) != 0 ||
            (clock[0] & 0x10000U) == 0U) return 153;
    }
    return 0;
}
