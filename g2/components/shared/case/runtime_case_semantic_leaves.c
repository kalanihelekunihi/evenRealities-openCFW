/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room charging-case semantic leaves. These behavioral candidates were
 * written from authenticated function boundaries and independently recorded
 * semantic contracts. They do not embed or reproduce stock instruction
 * encodings. Stock fixed-address state is represented by caller-owned buffers,
 * and this unit is not routed into a production image.
 */
#include "runtime_case_semantic_leaves.h"

#include <stddef.h>


#define OPEN_CFW_CASE_DEFINE_NOOP(address) \
    void open_cfw_case_hook_##address(void) { }
OPEN_CFW_CASE_NOOP_HOOKS(OPEN_CFW_CASE_DEFINE_NOOP)
#undef OPEN_CFW_CASE_DEFINE_NOOP


static uint32_t load_le32(const uint8_t *bytes)
{
    return (uint32_t)bytes[0]
        | ((uint32_t)bytes[1] << 8U)
        | ((uint32_t)bytes[2] << 16U)
        | ((uint32_t)bytes[3] << 24U);
}


static void store_le32(uint8_t *bytes, uint32_t value)
{
    bytes[0] = (uint8_t)value;
    bytes[1] = (uint8_t)(value >> 8U);
    bytes[2] = (uint8_t)(value >> 16U);
    bytes[3] = (uint8_t)(value >> 24U);
}


uint8_t open_cfw_case_read_byte3(const uint8_t *record)
{
    return record == NULL ? 0U : record[3];
}


void open_cfw_case_add_byte0_to_word8(uint8_t *record)
{
    if (record != NULL) {
        store_le32(record + 8U, load_le32(record + 8U) + record[0]);
    }
}


uint32_t open_cfw_case_or_words_88_8c(const uint8_t *context)
{
    if (context == NULL) {
        return 0U;
    }
    return load_le32(context + 0x88U) | load_le32(context + 0x8CU);
}


void open_cfw_case_copy_head8_to_tail8(uint8_t storage[16])
{
    uint32_t index;
    if (storage == NULL) {
        return;
    }
    for (index = 0U; index < 8U; ++index) {
        storage[index + 8U] = storage[index];
    }
}


void open_cfw_case_delay_10(void)
{
    volatile uint32_t index;
    for (index = 0U; index < 10U; ++index) {
    }
}


void open_cfw_case_busy_delay(int32_t iterations)
{
    volatile int32_t index;
    for (index = 0U; index < iterations; ++index) {
    }
}


void open_cfw_case_busy_delay_alt(int32_t iterations)
{
    open_cfw_case_busy_delay(iterations);
}


uint32_t open_cfw_case_parity8(uint32_t value)
{
    uint32_t parity = 0U;
    uint32_t bit;
    for (bit = 0U; bit < 8U; ++bit) {
        parity ^= (value >> bit) & 1U;
    }
    return parity;
}


uint32_t open_cfw_case_parity8_alt(uint32_t value)
{
    return open_cfw_case_parity8(value);
}


void open_cfw_case_forward_action(open_cfw_case_void_action_fn action)
{
    if (action != NULL) action();
}


void open_cfw_case_command_a2_clear(open_cfw_case_command_fn command)
{
    if (command != NULL) command(0xA2U, 0U);
}


void open_cfw_case_command_a2_set(open_cfw_case_command_fn command)
{
    if (command != NULL) command(0xA2U, 1U);
}


void open_cfw_case_run_pair(open_cfw_case_void_action_fn first,
                            open_cfw_case_void_action_fn second)
{
    if (first != NULL) first();
    if (second != NULL) second();
}


int open_cfw_case_invoke_mode_one(open_cfw_case_mode_action_fn action,
                                  uint32_t first, uint32_t second)
{
    if (action != NULL) (void)action(first, second, 1U);
    return 0;
}


int open_cfw_case_invoke_byte(open_cfw_case_byte_action_fn action,
                              uint32_t selector, const uint8_t *value)
{
    if (action != NULL && value != NULL) (void)action(selector, *value);
    return 0;
}


void open_cfw_case_transform_word(uint32_t *output, uint32_t value,
                                  open_cfw_case_word_transform_fn transform)
{
    if (output == NULL) return;
    if (transform != NULL) transform(&value);
    *output = value;
}


void open_cfw_case_transform_word_alt(
    uint32_t *output, uint32_t value,
    open_cfw_case_word_transform_fn transform)
{
    open_cfw_case_transform_word(output, value, transform);
}


void open_cfw_case_run_if_token(const int32_t *value, int32_t token,
                                open_cfw_case_void_action_fn action)
{
    if (value != NULL && *value == token && action != NULL) action();
}


void open_cfw_case_dispatch_resource(open_cfw_case_dispatch_fn dispatch,
                                     uintptr_t resource, uint32_t first,
                                     uint32_t second)
{
    if (dispatch != NULL) dispatch(resource, first, second, 0U);
}


void open_cfw_case_dispatch_resource4(open_cfw_case_dispatch_fn dispatch,
                                      uintptr_t resource, uint32_t first,
                                      uint32_t second, uint32_t third)
{
    if (dispatch != NULL) dispatch(resource, first, second, third);
}


void open_cfw_case_route_boolean(int value,
                                 open_cfw_case_void_action_fn true_action,
                                 open_cfw_case_void_action_fn false_action)
{
    open_cfw_case_void_action_fn action = value != 0 ? true_action : false_action;
    if (action != NULL) action();
}


void open_cfw_case_route_boolean_alt(int value,
                                     open_cfw_case_void_action_fn true_action,
                                     open_cfw_case_void_action_fn false_action)
{
    open_cfw_case_route_boolean(value, true_action, false_action);
}


void open_cfw_case_emit_bits(uint32_t value, int seven_bits,
                             open_cfw_case_bool_action_fn emit)
{
    int bit = seven_bits != 0 ? 6 : 7;
    if (emit == NULL) return;
    for (; bit >= 0; --bit) emit((int)((value >> (unsigned int)bit) & 1U));
}


void open_cfw_case_emit_bits_alt(uint32_t value, int seven_bits,
                                 open_cfw_case_bool_action_fn emit)
{
    open_cfw_case_emit_bits(value, seven_bits, emit);
}


void open_cfw_case_nested_delay(int32_t outer, int32_t inner)
{
    volatile int32_t first;
    volatile int32_t second;
    for (first = 0; first < outer; ++first)
        for (second = 0; second < inner; ++second) { }
}


int open_cfw_case_context_word38_is_zero(const uint8_t *context)
{
    return context == NULL || load_le32(context + 0x38U) == 0U;
}


uint32_t open_cfw_case_read_word_protected(
    const uint32_t *value, open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave)
{
    uint32_t result = 0U;
    if (enter != NULL) enter();
    if (value != NULL) result = *value;
    if (leave != NULL) leave();
    return result;
}


void open_cfw_case_run_guarded(uint8_t state[2],
                               open_cfw_case_void_action_fn action)
{
    if (state == NULL || state[1] != 0U) return;
    state[1] = 1U;
    if (action != NULL) action();
    state[1] = 0U;
}


static void transition_word(uint8_t *record, size_t offset, uint32_t value,
                            open_cfw_case_notify_fn notify)
{
    if (record == NULL || load_le32(record + offset) == value) return;
    store_le32(record + offset, value);
    if (notify != NULL) notify(record);
}


void open_cfw_case_transition_word4(uint8_t *record, uint32_t value,
                                    open_cfw_case_notify_fn notify)
{
    transition_word(record, 4U, value, notify);
}


void open_cfw_case_transition_word4_alt(uint8_t *record, uint32_t value,
                                        open_cfw_case_notify_fn notify)
{
    transition_word(record, 4U, value, notify);
}


void open_cfw_case_transition_word8(uint8_t *record, uint32_t value,
                                    open_cfw_case_notify_fn notify)
{
    transition_word(record, 8U, value, notify);
}


void open_cfw_case_transition_word8_alt(uint8_t *record, uint32_t value,
                                        open_cfw_case_notify_fn notify)
{
    transition_word(record, 8U, value, notify);
}


static void write_profile(open_cfw_case_index_write_fn write,
                          uint32_t last_index)
{
    if (write == NULL) return;
    write(7U, 0x20U);
    write(6U, 0x81U);
    write(5U, 3U);
    write(last_index, 0xFFU);
}


void open_cfw_case_write_profile_three(open_cfw_case_index_write_fn write)
{
    write_profile(write, 3U);
}


void open_cfw_case_write_profile_four(open_cfw_case_index_write_fn write)
{
    write_profile(write, 4U);
}


uint32_t open_cfw_case_select_mask(const uint8_t *wide_first,
                                   uintptr_t resource,
                                   open_cfw_case_mask_read_fn read)
{
    uint32_t mask = wide_first != NULL && *wide_first != 0U ? 8U : 0x10U;
    return read == NULL ? 0U : read(resource, mask);
}


void open_cfw_case_write_selected_mask(const uint8_t *wide_first,
                                       uintptr_t resource, uint32_t value,
                                       open_cfw_case_mask_write_fn write)
{
    uint32_t mask = wide_first != NULL && *wide_first != 0U ? 0x10U : 8U;
    if (write != NULL) write(resource, mask, value);
}


void open_cfw_case_write_selected_mask_alt(
    const uint8_t *wide_first, uintptr_t resource, uint32_t value,
    open_cfw_case_mask_write_fn write)
{
    uint32_t mask = wide_first != NULL && *wide_first != 0U ? 8U : 0x10U;
    if (write != NULL) write(resource, mask, value);
}


void open_cfw_case_forward_resource(void *resource,
                                    open_cfw_case_resource_action_fn action)
{
    if (action != NULL) action(resource);
}


int open_cfw_case_run_guarded_status(uint8_t state[2],
                                     open_cfw_case_void_action_fn action)
{
    open_cfw_case_run_guarded(state, action);
    return 0;
}


void open_cfw_case_read_mask4(uintptr_t resource,
                              open_cfw_case_mask_read_fn read)
{
    if (read != NULL) (void)read(resource, 4U);
}


void open_cfw_case_read_mask8(uintptr_t resource,
                              open_cfw_case_mask_read_fn read)
{
    if (read != NULL) (void)read(resource, 8U);
}


static void write_fixed_mask(uintptr_t resource, uint32_t mask,
                             uint32_t value,
                             open_cfw_case_mask_write_fn write)
{
    if (write != NULL) write(resource, mask, value);
}


void open_cfw_case_write_mask4_set(uintptr_t resource,
                                   open_cfw_case_mask_write_fn write)
{
    write_fixed_mask(resource, 4U, 1U, write);
}


void open_cfw_case_write_mask4_clear(uintptr_t resource,
                                     open_cfw_case_mask_write_fn write)
{
    write_fixed_mask(resource, 4U, 0U, write);
}


void open_cfw_case_write_mask8_set(uintptr_t resource,
                                   open_cfw_case_mask_write_fn write)
{
    write_fixed_mask(resource, 8U, 1U, write);
}


void open_cfw_case_write_mask8_clear(uintptr_t resource,
                                     open_cfw_case_mask_write_fn write)
{
    write_fixed_mask(resource, 8U, 0U, write);
}


void open_cfw_case_dispatch_tagged(open_cfw_case_dispatch_fn dispatch,
                                   uintptr_t resource, uint32_t first,
                                   uint32_t second, uint32_t tag)
{
    if (dispatch != NULL) dispatch(resource, first, second, tag);
}


void open_cfw_case_route_parity(uint32_t value,
                                open_cfw_case_void_action_fn odd_action,
                                open_cfw_case_void_action_fn even_action)
{
    open_cfw_case_route_boolean(
        open_cfw_case_parity8(value) == 1U, odd_action, even_action);
}


void open_cfw_case_route_parity_alt(uint32_t value,
                                    open_cfw_case_void_action_fn odd_action,
                                    open_cfw_case_void_action_fn even_action)
{
    open_cfw_case_route_parity(value, odd_action, even_action);
}


void open_cfw_case_reset_timer_fields(uint8_t *state,
                                      open_cfw_case_void_action_fn action)
{
    if (state == NULL) return;
    state[0x56U] = 0U;
    state[0x57U] = 0U;
    state[0x5EU] = 0U;
    state[0x5FU] = 0U;
    if (action != NULL) action();
}


int open_cfw_case_expand_runs(const uint8_t *input, uint32_t input_length,
                              uint8_t *output, uint32_t output_length)
{
    uint32_t in = 0U;
    uint32_t out = 0U;
    if (input == NULL || output == NULL) return -1;
    while (out < output_length) {
        uint32_t literal;
        uint32_t zeroes;
        uint8_t header;
        if (in >= input_length) return -1;
        header = input[in++];
        literal = header & 0x0FU;
        zeroes = header >> 4U;
        if (literal == 0U) {
            if (in >= input_length) return -1;
            literal = input[in++];
        }
        if (zeroes == 0U) {
            if (in >= input_length) return -1;
            zeroes = input[in++];
        }
        if (literal != 0U) --literal;
        if (zeroes != 0U) --zeroes;
        if (literal > input_length - in || literal > output_length - out)
            return -1;
        while (literal-- != 0U) output[out++] = input[in++];
        if (zeroes > output_length - out) return -1;
        while (zeroes-- != 0U) output[out++] = 0U;
    }
    return 0;
}


uint32_t open_cfw_case_classify_status(open_cfw_case_fill_status_fn fill)
{
    uint8_t record[28];
    size_t index;
    for (index = 0U; index < sizeof(record); ++index) record[index] = 0U;
    if (fill != NULL) (void)fill(record);
    return (load_le32(record + 24U) & (1U << 20U)) != 0U ? 1U : 2U;
}


uint32_t open_cfw_case_shift_selected(uint32_t value, uint32_t control,
                                      const uint8_t *shift_table,
                                      uint32_t shift_count)
{
    uint32_t index = (control & 0x7FFFU) >> 12U;
    if (shift_table == NULL || index >= shift_count) return 0U;
    return value >> (shift_table[index * 4U] & 0x1FU);
}


int open_cfw_case_query_low_byte(uint32_t *output, uint32_t initial,
                                 open_cfw_case_query_word_fn query)
{
    if (output == NULL || query == NULL || query(&initial) != 0) return -1;
    *output = initial & 0xFFU;
    return 0;
}


void open_cfw_case_advance_cursor(uint32_t record[17], uint32_t argument,
                                  open_cfw_case_cursor_fn publish)
{
    uint32_t cursor;
    if (record == NULL || record[16] == 0U) return;
    cursor = record[3] + record[16];
    record[3] = cursor < record[2] ? cursor : record[0];
    if (publish != NULL) publish(argument, record[3]);
}


static int pulse_ops_ready(const open_cfw_case_pulse_ops *ops)
{
    return ops != NULL && ops->mask4_set != NULL &&
        ops->mask4_clear != NULL && ops->mask8_set != NULL &&
        ops->mask8_clear != NULL && ops->word4_primary != NULL &&
        ops->word4_alternate != NULL && ops->delay != NULL;
}


static void pulse_sequence(const open_cfw_case_pulse_ops *ops, int lane8,
                           int32_t first_delay, int extended)
{
    open_cfw_case_void_action_fn set;
    open_cfw_case_void_action_fn clear;
    open_cfw_case_void_action_fn word;
    if (!pulse_ops_ready(ops)) return;
    set = lane8 != 0 ? ops->mask8_set : ops->mask4_set;
    clear = lane8 != 0 ? ops->mask8_clear : ops->mask4_clear;
    word = lane8 != 0 ? ops->word4_alternate : ops->word4_primary;
    set();
    word();
    set();
    if (extended != 0) {
        ops->delay(23);
        clear();
        ops->delay(350);
    } else {
        clear();
        ops->delay(first_delay);
    }
    set();
}


void open_cfw_case_pulse4_short(const open_cfw_case_pulse_ops *ops)
{
    pulse_sequence(ops, 0, 23, 0);
}


void open_cfw_case_pulse8_short(const open_cfw_case_pulse_ops *ops)
{
    pulse_sequence(ops, 1, 23, 0);
}


void open_cfw_case_pulse4_long(const open_cfw_case_pulse_ops *ops)
{
    pulse_sequence(ops, 0, 90, 0);
}


void open_cfw_case_pulse8_long(const open_cfw_case_pulse_ops *ops)
{
    pulse_sequence(ops, 1, 90, 0);
}


void open_cfw_case_pulse4_extended(const open_cfw_case_pulse_ops *ops)
{
    pulse_sequence(ops, 0, 0, 1);
}


void open_cfw_case_pulse8_extended(const open_cfw_case_pulse_ops *ops)
{
    pulse_sequence(ops, 1, 0, 1);
}


static void delay_repeated(const open_cfw_case_pulse_ops *ops,
                           uint32_t repetitions)
{
    uint32_t index;
    for (index = 0U; index < repetitions; ++index) ops->delay(350);
}


void open_cfw_case_pulse4_train_pre_delay(const open_cfw_case_pulse_ops *ops)
{
    if (!pulse_ops_ready(ops)) return;
    ops->mask4_set();
    ops->word4_primary();
    ops->mask4_set();
    ops->delay(350);
    ops->mask4_clear();
    delay_repeated(ops, 40U);
    ops->mask4_set();
}


void open_cfw_case_pulse4_train(const open_cfw_case_pulse_ops *ops)
{
    if (!pulse_ops_ready(ops)) return;
    ops->mask4_set();
    ops->word4_primary();
    ops->mask4_set();
    ops->mask4_clear();
    delay_repeated(ops, 40U);
    ops->mask4_set();
}


void open_cfw_case_pulse8_double_train(const open_cfw_case_pulse_ops *ops)
{
    if (!pulse_ops_ready(ops)) return;
    ops->mask8_set();
    ops->word4_alternate();
    ops->mask8_set();
    ops->mask8_clear();
    delay_repeated(ops, 10U);
    ops->mask8_set();
    ops->delay(23);
    ops->mask8_clear();
    delay_repeated(ops, 10U);
    ops->mask8_set();
}


static int serial_ops_ready(const open_cfw_case_serial_line_ops *ops)
{
    return ops != NULL && ops->clock != NULL && ops->data != NULL &&
        ops->delay != NULL;
}


static void serial_clock(const open_cfw_case_serial_line_ops *ops, int value)
{
    ops->clock(value);
    ops->delay();
}


void open_cfw_case_serial_preamble(const open_cfw_case_serial_line_ops *ops)
{
    if (!serial_ops_ready(ops)) return;
    serial_clock(ops, 0);
    ops->data(0);
    ops->delay();
    serial_clock(ops, 1);
    serial_clock(ops, 0);
    ops->data(1);
    ops->delay();
}


void open_cfw_case_serial_ack(const open_cfw_case_serial_line_ops *ops)
{
    if (!serial_ops_ready(ops)) return;
    ops->data(1);
    ops->delay();
    serial_clock(ops, 1);
    serial_clock(ops, 0);
}


void open_cfw_case_serial_start(const open_cfw_case_serial_line_ops *ops)
{
    if (!serial_ops_ready(ops)) return;
    ops->clock(1);
    ops->data(1);
    ops->delay();
    ops->data(0);
    ops->delay();
    serial_clock(ops, 0);
}


void open_cfw_case_serial_stop(const open_cfw_case_serial_line_ops *ops)
{
    if (!serial_ops_ready(ops)) return;
    ops->data(0);
    ops->clock(1);
    ops->delay();
    ops->data(1);
    ops->delay();
}


uint32_t open_cfw_case_serial_read_byte(
    const open_cfw_case_serial_line_ops *ops)
{
    uint32_t value = 0U;
    uint32_t bit;
    if (!serial_ops_ready(ops) || ops->sample == NULL) return 0U;
    for (bit = 0U; bit < 8U; ++bit) {
        value = (value & 0x7FU) << 1U;
        ops->clock(1);
        ops->delay();
        if (ops->sample() != 0) ++value;
        serial_clock(ops, 0);
    }
    return value;
}


void open_cfw_case_serial_write_byte(const open_cfw_case_serial_line_ops *ops,
                                     uint32_t value)
{
    uint32_t bit;
    if (!serial_ops_ready(ops)) return;
    for (bit = 0U; bit < 8U; ++bit) {
        ops->data((value & 0x80U) != 0U);
        ops->delay();
        serial_clock(ops, 1);
        serial_clock(ops, 0);
        if (bit == 7U) {
            ops->data(1);
            ops->delay();
        }
        value = (value & 0x7FU) << 1U;
    }
}


int open_cfw_case_query_command_a2_is_one(
    uint32_t initial, open_cfw_case_query_command_fn query)
{
    uint32_t value = initial & UINT32_C(0xFFFFFF00);
    if (query != NULL) (void)query(0xA2U, &value, 1U);
    return (value & 0xFFU) == 1U;
}


void open_cfw_case_clear_irq(int32_t index, volatile uint32_t *clear_register,
                             open_cfw_case_void_action_fn data_barrier,
                             open_cfw_case_void_action_fn instruction_barrier)
{
    if (index < 0 || clear_register == NULL) return;
    *clear_register = UINT32_C(1) << ((uint32_t)index & 31U);
    if (data_barrier != NULL) data_barrier();
    if (instruction_barrier != NULL) instruction_barrier();
}


void open_cfw_case_dispatch_pending(
    volatile uint32_t *first_status, volatile uint32_t *second_status,
    uint32_t mask, open_cfw_case_mask_action_fn first_action,
    open_cfw_case_mask_action_fn second_action)
{
    if (first_status != NULL && (*first_status & mask) != 0U) {
        *first_status = mask;
        if (first_action != NULL) first_action(mask);
    }
    if (second_status != NULL && (*second_status & mask) != 0U) {
        *second_status = mask;
        if (second_action != NULL) second_action(mask);
    }
}


void open_cfw_case_mark_controller_ready(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_resource_action_fn notify)
{
    if (context == NULL || controller == NULL) return;
    if ((controller[0x50U / 4U] & 4U) != 0U) {
        controller[0x5CU / 4U] |= 4U;
        if (notify != NULL) notify(context);
    }
    context[0x29U] = 1U;
}


void open_cfw_case_wait_elapsed(uint32_t delay, uint32_t compensation,
                                open_cfw_case_tick_read_fn tick_read)
{
    uint32_t start;
    if (tick_read == NULL) return;
    start = tick_read();
    if (delay != UINT32_MAX) delay += compensation;
    while ((uint32_t)(tick_read() - start) < delay) { }
}


uint32_t open_cfw_case_guarded_controller_disable(
    uint8_t *context, volatile uint32_t *control_register)
{
    uint32_t value;
    if (context == NULL || control_register == NULL) return 2U;
    if (context[0x84U] == 1U) return 2U;
    context[0x84U] = 1U;
    store_le32(context + 0x88U, 0x24U);
    value = *control_register;
    *control_register = value & UINT32_C(0xFFFFFFFE);
    store_le32(context + 0x64U, 0U);
    *control_register = value & UINT32_C(0xDFFFFFFF);
    store_le32(context + 0x88U, 0x20U);
    context[0x84U] = 0U;
    return 0U;
}


int32_t open_cfw_case_start_scheduler(
    int requested, uint32_t exception_number,
    open_cfw_case_void_action_fn start)
{
    if ((exception_number & 0x1FU) != 0U) return -6;
    if (requested == 0) return -4;
    if (start != NULL) start();
    return 0;
}


int open_cfw_case_serial_ack_sample(
    const open_cfw_case_serial_line_ops *ops)
{
    int result;
    if (!serial_ops_ready(ops) || ops->sample == NULL) return 0;
    ops->data(1);
    ops->clock(1);
    ops->delay();
    result = ops->sample();
    ops->clock(0);
    ops->delay();
    return result != 0;
}


int open_cfw_case_collect_bits(uint8_t *output, int initial,
                               open_cfw_case_bit_read_fn read_bit)
{
    uint32_t result = 0U;
    int bit_value = initial;
    int bit;
    int status = 1;
    if (output == NULL || read_bit == NULL) return 0;
    for (bit = 7; bit >= 0; --bit) {
        if (read_bit(&bit_value) == 0) {
            status = 0;
            break;
        }
        result = (result + ((uint32_t)bit_value << (unsigned int)bit)) & 0xFFU;
    }
    *output = (uint8_t)result;
    return status;
}


void open_cfw_case_update_cached_byte(
    uint8_t *cache, uint32_t index, uint32_t value, uint32_t argument,
    open_cfw_case_byte_update_fn update)
{
    uint32_t local = value;
    if (cache == NULL || cache[index] == (uint8_t)value || update == NULL)
        return;
    if (update(index, 1U, &local, argument, index) != 0)
        cache[index] = (uint8_t)local;
}


int open_cfw_case_guarded_two_stage(
    uint8_t *context, open_cfw_case_resource_status_fn first,
    open_cfw_case_resource_status_fn second)
{
    int status;
    uint32_t value;
    if (context == NULL || context[0x54U] == 1U) return 2;
    context[0x54U] = 1U;
    status = first == NULL ? -1 : first(context);
    if (status == 0) status = second == NULL ? -1 : second(context);
    if (status == 0) {
        value = load_le32(context + 0x58U);
        store_le32(context + 0x58U, (value & UINT32_C(0xFFFFFEFF)) | 1U);
    }
    context[0x54U] = 0U;
    return status;
}


void open_cfw_case_configure_two_bit_field(
    uint32_t selector, uint32_t value, uint32_t *positive_registers,
    uint8_t *negative_register_block)
{
    uint32_t shift = (selector & 3U) << 3U;
    uint32_t mask = UINT32_C(0xFF) << shift;
    uint32_t field = ((value & 3U) << 6U) << shift;
    if ((int32_t)selector >= 0) {
        uint32_t *target;
        if (positive_registers == NULL) return;
        target = &positive_registers[(selector & UINT32_C(0xFFFFFFFC)) / 4U];
        *target = (*target & ~mask) | field;
    } else {
        uint32_t offset = ((((selector & 0xFU) - 8U) &
                            UINT32_C(0xFFFFFFFC)) + 0x1CU);
        uint32_t current;
        if (negative_register_block == NULL) return;
        current = load_le32(negative_register_block + offset);
        store_le32(negative_register_block + offset,
                   (current & ~mask) | field);
    }
}


int open_cfw_case_retry_selector8(open_cfw_case_selector_status_fn attempt,
                                  open_cfw_case_counted_delay_fn delay)
{
    if (attempt == NULL || attempt(8U) != 0) return -1;
    if (delay != NULL) delay(21);
    if (attempt(8U) != 0) return -1;
    if (delay != NULL) delay(11);
    return 0;
}


int open_cfw_case_wait_status_bit5(volatile uint32_t *status_register,
                                   open_cfw_case_tick_read_fn tick_read)
{
    uint32_t start;
    if (status_register == NULL || tick_read == NULL) return 3;
    *status_register &= UINT32_C(0xFFFFFF5F);
    start = tick_read();
    do {
        if ((*status_register & (1U << 5U)) != 0U) return 0;
    } while ((uint32_t)(tick_read() - start) < 1001U);
    return 3;
}


uint32_t open_cfw_case_critical_read_word28(
    const uint8_t *record, open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave,
    open_cfw_case_void_action_fn panic)
{
    uint32_t result;
    if (record == NULL) {
        if (panic != NULL) panic();
        return 0U;
    }
    if (enter != NULL) enter();
    result = load_le32(record + 0x1CU);
    if (leave != NULL) leave();
    return result;
}


int open_cfw_case_critical_read_flag40(
    const uint8_t *record, open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave,
    open_cfw_case_void_action_fn panic)
{
    uint8_t value;
    if (record == NULL) {
        if (panic != NULL) panic();
        return 0;
    }
    if (enter != NULL) enter();
    value = record[0x28U];
    if (leave != NULL) leave();
    return (value & 1U) != 0U;
}


uint32_t open_cfw_case_atomic_clear_word(
    uint32_t *value, uint32_t mask, open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave,
    open_cfw_case_void_action_fn panic)
{
    uint32_t prior;
    if (value == NULL || (mask >> 24U) != 0U) {
        if (panic != NULL) panic();
        return 0U;
    }
    if (enter != NULL) enter();
    prior = *value;
    *value = prior & ~mask;
    if (leave != NULL) leave();
    return prior;
}


static int guarded_controller_field(
    uint8_t *context, volatile uint32_t *controller, uint32_t value,
    uint32_t preserve_mask, open_cfw_case_resource_action_fn apply)
{
    uint32_t saved;
    if (context == NULL || controller == NULL) return 2;
    if (context[0x84U] == 1U) return 2;
    context[0x84U] = 1U;
    store_le32(context + 0x88U, 0x24U);
    saved = controller[0];
    controller[0] &= UINT32_C(0xFFFFFFFE);
    controller[2] = (controller[2] & preserve_mask) | value;
    if (apply != NULL) apply(context);
    controller[0] = saved;
    store_le32(context + 0x88U, 0x20U);
    context[0x84U] = 0U;
    return 0;
}


int open_cfw_case_guarded_controller_field_high(
    uint8_t *context, volatile uint32_t *controller, uint32_t value,
    open_cfw_case_resource_action_fn apply)
{
    return guarded_controller_field(
        context, controller, value, UINT32_C(0x1FFFFFFF), apply);
}


int open_cfw_case_guarded_controller_field_mid(
    uint8_t *context, volatile uint32_t *controller, uint32_t value,
    open_cfw_case_resource_action_fn apply)
{
    return guarded_controller_field(
        context, controller, value, UINT32_C(0xF1FFFFFF), apply);
}


int open_cfw_case_start_validated(
    uint32_t initial, open_cfw_case_query_word_fn query,
    open_cfw_case_status_action_fn start,
    open_cfw_case_status_action_fn finalize)
{
    int status;
    uint32_t value = initial;
    if (query == NULL) return -1;
    status = query(&value);
    if (status != 0) return status;
    if (value != 0xA0U) return -2;
    status = start == NULL ? -1 : start();
    if (status < 0) return status;
    if (status != 0) {
        status = finalize == NULL ? -1 : finalize();
        if (status < 0) return status;
    }
    return 0;
}


void open_cfw_case_toggle_lines_three(
    open_cfw_case_line_write_fn first, open_cfw_case_line_write_fn second,
    open_cfw_case_counted_delay_fn delay)
{
    uint32_t index;
    if (first == NULL || second == NULL || delay == NULL) return;
    for (index = 0U; index < 3U; ++index) {
        first(1);
        second(0);
        delay(200);
        first(0);
        second(1);
        delay(200);
    }
    first(0);
    second(0);
}


void open_cfw_case_configure_record_and_stop(
    uintptr_t resource, open_cfw_case_record_config_fn configure,
    open_cfw_case_void_action_fn stop)
{
    uint32_t record[5];
    uint32_t index;
    for (index = 0U; index < 5U; ++index) record[index] = 0U;
    record[0] = 0x18U;
    record[1] = 0x11U;
    if (configure != NULL) configure(resource, record);
    if (stop != NULL) stop();
}


void open_cfw_case_normalize_context(
    uint8_t *context, uint32_t first, uint32_t second,
    open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave,
    open_cfw_case_context_dispatch_fn dispatch,
    open_cfw_case_resource_action_fn finalize)
{
    if (context == NULL) return;
    if (enter != NULL) enter();
    if (context[0x44U] == 0xFFU) context[0x44U] = 0U;
    if (context[0x45U] == 0xFFU) context[0x45U] = 0U;
    if (leave != NULL) leave();
    if (load_le32(context + 0x38U) == 0U && dispatch != NULL)
        dispatch(context + 0x24U, first, second);
    if (finalize != NULL) finalize(context);
}


int open_cfw_case_reset_controller_context(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_resource_action_fn release)
{
    if (context == NULL || controller == NULL) return 1;
    store_le32(context + 0x88U, 0x24U);
    controller[0] &= UINT32_C(0xFFFFFFFE);
    controller[0] = 0U;
    controller[1] = 0U;
    controller[2] = 0U;
    if (release != NULL) release(context);
    store_le32(context + 0x90U, 0U);
    store_le32(context + 0x88U, 0U);
    store_le32(context + 0x8CU, 0U);
    store_le32(context + 0x6CU, 0U);
    store_le32(context + 0x70U, 0U);
    context[0x84U] = 0U;
    return 0;
}


int open_cfw_case_wait_controller_ready(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_tick_read_fn tick_read)
{
    uint32_t start;
    if (context == NULL || controller == NULL || tick_read == NULL) return 3;
    if ((controller[3] & (1U << 6U)) != 0U) return 0;
    controller[3] |= 1U << 7U;
    start = tick_read();
    while ((controller[3] & (1U << 6U)) == 0U) {
        if ((uint32_t)(tick_read() - start) > 1000U) {
            context[0x29U] = 3U;
            return 3;
        }
    }
    return 0;
}


int open_cfw_case_prepare_controller_wait(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_resource_status_fn wait_ready)
{
    int status;
    int restore;
    if (context == NULL || controller == NULL || wait_ready == NULL) return 3;
    controller[3] &= UINT32_C(0xFFFFFF7F);
    restore = (controller[6] & (1U << 5U)) != 0U;
    if (restore) controller[6] &= UINT32_C(0xFFFFFFDF);
    status = wait_ready(context);
    if (status != 0) context[0x29U] = 3U;
    if (restore) controller[6] |= 1U << 5U;
    return status == 0 ? 0 : 3;
}


int open_cfw_case_configure_mode_wait(
    volatile uint32_t *registers, uint32_t value, uint32_t clock,
    uint32_t divisor, open_cfw_case_divide_fn divide)
{
    uint32_t budget;
    if (registers == NULL) return 3;
    registers[0] = (registers[0] & UINT32_C(0xFFFFF9FF)) | value;
    if (value != 0x200U) return 0;
    if (divide == NULL || divisor == 0U) return 3;
    budget = divide(clock * 6U, divisor) + 1U;
    while ((registers[5] & (1U << 10U)) != 0U) {
        if (budget == 0U) return 3;
        --budget;
    }
    return 0;
}


void open_cfw_case_configure_register_sequence(
    open_cfw_case_register_write_fn write,
    open_cfw_case_counted_delay_fn delay)
{
    if (write == NULL || delay == NULL) return;
    write(0x13U, 0x90U); delay(2);
    write(0x16U, 0x00U); delay(2);
    write(0x19U, 0x02U); delay(2);
    write(0x17U, 0x28U); delay(2);
    write(0x18U, 0x01U); delay(2);
    write(0x1AU, 0x00U); delay(2);
    write(0x1BU, 0x01U); delay(2);
}


int open_cfw_case_initialize_peripheral_context(
    uint8_t *context, open_cfw_case_resource_action_fn reset,
    open_cfw_case_context_config_fn configure)
{
    uint32_t resource;
    uint32_t index;
    if (context == NULL) return 1;
    if (context[0x3DU] == 0U) {
        context[0x3CU] = 0U;
        if (reset != NULL) reset(context);
    }
    context[0x3DU] = 2U;
    resource = load_le32(context);
    if (configure != NULL)
        configure((void *)(uintptr_t)resource, context + 4U);
    for (index = 0x3EU; index <= 0x48U; ++index)
        context[index] = 1U;
    context[0x3DU] = 1U;
    return 0;
}


int open_cfw_case_enable_peripheral_context(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t mode_mask, int special_controller)
{
    uint32_t mode;
    if (context == NULL || controller == NULL) return 1;
    if (context[0x3DU] != 1U) return 1;
    context[0x3DU] = 2U;
    controller[3] |= 1U;
    if (special_controller != 0) {
        mode = controller[2] & mode_mask;
        if (mode == 6U || mode == mode_mask - 7U) return 0;
    }
    controller[0] |= 1U;
    return 0;
}


int open_cfw_case_wait_serial_idle(
    volatile uint32_t *registers, volatile uint32_t *error_registers,
    uint32_t timeout, uint32_t status_mask, uint32_t idle_value,
    open_cfw_case_tick_read_fn tick_read)
{
    uint32_t start;
    uint32_t pending;
    if (registers == NULL || tick_read == NULL) return 3;
    start = tick_read();
    while ((registers[4] & UINT32_C(0x00030000)) != 0U) {
        if ((uint32_t)(tick_read() - start) >= timeout) return 3;
    }
    pending = registers[4] & status_mask;
    registers[4] = idle_value;
    if (pending != 0U) {
        if (error_registers != NULL) error_registers[1] = pending;
        return 1;
    }
    start = tick_read();
    while ((registers[4] & (1U << 18U)) != 0U) {
        if ((uint32_t)(tick_read() - start) >= timeout) return 3;
    }
    return 0;
}


int open_cfw_case_probe_low_signal(
    uint32_t state[4], uint32_t *observed, uint32_t limit,
    const open_cfw_case_probe_ops *ops)
{
    uint32_t count;
    uint32_t sample;
    if (state == NULL || observed == NULL || ops == NULL ||
        ops->read == NULL) return 1;
    state[2] = 0U;
    state[3] = 0U;
    if (ops->word8_set != NULL) ops->word8_set();
    if (ops->mask4_set != NULL) ops->mask4_set();
    if (ops->word4_set != NULL) ops->word4_set();
    if (ops->mask4_set != NULL) ops->mask4_set();
    if (ops->mask4_clear != NULL) ops->mask4_clear();
    if (ops->word4_clear != NULL) ops->word4_clear();
    if (ops->delay != NULL) ops->delay(23);
    sample = ops->read();
    *observed = (~sample) & 1U;
    for (count = 0U; count < limit; ++count) {
        if (ops->read() != 0U) return 1;
    }
    state[3] = 1U;
    return 0;
}


uint64_t open_cfw_case_probe_high_signal(
    uint32_t state[5], uint32_t *observed, uint32_t limit,
    open_cfw_case_void_action_fn word4_clear,
    open_cfw_case_void_action_fn word8_set,
    open_cfw_case_counted_delay_fn delay,
    open_cfw_case_value_read_fn read)
{
    uint32_t count;
    uint32_t sample;
    uint32_t status = 1U;
    if (state == NULL || observed == NULL || read == NULL) return 0U;
    state[3] = 0U;
    state[4] = 0U;
    if (word4_clear != NULL) word4_clear();
    if (word8_set != NULL) word8_set();
    for (count = 0U; count < limit; ++count) {
        if (read() != 1U) break;
    }
    if (count == limit) {
        status = 0U;
        state[3] = 1U;
    }
    if (delay != NULL) delay(50);
    sample = read();
    *observed = (~sample) & 1U;
    for (count = 0U; count < limit; ++count) {
        if (read() != 0U) break;
    }
    if (count == limit) {
        status = 0U;
        state[4] = 1U;
    }
    *observed = (~sample) & 1U;
    return ((uint64_t)((~sample) & 1U) << 32U) | status;
}


void open_cfw_case_fail_stop(open_cfw_case_void_action_fn disable,
                             open_cfw_case_void_action_fn idle)
{
    if (disable != NULL) disable();
    for (;;) {
        if (idle != NULL) idle();
    }
}


uint32_t open_cfw_case_switch8_offset(uint32_t selector,
                                      const uint8_t *table)
{
    uint32_t selected;
    if (table == NULL) return 0U;
    selected = selector < table[0] ? selector : table[0];
    return (uint32_t)table[1U + selected] * 2U;
}


int open_cfw_case_initialize_serial_block(
    volatile uint32_t *control, uint32_t enable_mask,
    open_cfw_case_selector_status_fn initialize,
    open_cfw_case_void_action_fn configure)
{
    int status;
    if (control == NULL || initialize == NULL) return 1;
    *control |= enable_mask;
    status = initialize(3U);
    if (status == 0 && configure != NULL) configure();
    return status != 0;
}


static int serial_write_pair(
    uint32_t address, uint32_t first, uint32_t second,
    volatile uint8_t *state, open_cfw_case_void_action_fn start,
    open_cfw_case_value_write_fn write,
    open_cfw_case_status_action_fn acknowledge,
    open_cfw_case_void_action_fn stop)
{
    uint32_t retry;
    int success = 0;
    if (state != NULL) *state = 0U;
    if (start == NULL || write == NULL || acknowledge == NULL || stop == NULL)
        return 0;
    for (retry = 0U; retry < 200U; ++retry) {
        start();
        write(address);
        if (acknowledge() == 0) break;
    }
    if (retry < 200U) {
        write(first);
        if (acknowledge() == 0) {
            write(second);
            if (acknowledge() == 0) success = 1;
        }
    }
    stop();
    return success;
}


int open_cfw_case_serial_write_pair_200(
    uint32_t first, uint32_t second, volatile uint8_t *state,
    open_cfw_case_void_action_fn start,
    open_cfw_case_value_write_fn write,
    open_cfw_case_status_action_fn acknowledge,
    open_cfw_case_void_action_fn stop)
{
    return serial_write_pair(
        200U, first, second, state, start, write, acknowledge, stop);
}


int open_cfw_case_serial_write_pair_70(
    uint32_t first, uint32_t second, volatile uint8_t *state,
    open_cfw_case_void_action_fn start,
    open_cfw_case_value_write_fn write,
    open_cfw_case_status_action_fn acknowledge,
    open_cfw_case_void_action_fn stop)
{
    return serial_write_pair(
        0x70U, first, second, state, start, write, acknowledge, stop);
}


int open_cfw_case_start_context_transfer(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t option, int enabled,
    open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave,
    open_cfw_case_resource_status_fn transfer)
{
    uint32_t mode;
    if (context == NULL || controller == NULL) return 2;
    if (load_le32(context + 0x8CU) != 0x20U) return 2;
    mode = load_le32(context + 8U);
    if (option == 0U || enabled == 0 ||
        (mode == 0x1000U &&
         (load_le32(context + 0x10U) == 0U || (option & 1U) == 0U)))
        return 1;
    store_le32(context + 0x6CU, 0U);
    if ((controller[1] & (1U << 23U)) != 0U) {
        if (enter != NULL) enter();
        controller[0] |= 1U << 26U;
        if (leave != NULL) leave();
    }
    return transfer == NULL ? 1 : transfer(context);
}


void open_cfw_case_reset_context_transfer(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t controller2_mask,
    open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave)
{
    if (context == NULL || controller == NULL) return;
    if (enter != NULL) enter();
    controller[0] &= UINT32_C(0xFFFFFEDF);
    if (leave != NULL) leave();
    if (enter != NULL) enter();
    controller[2] &= controller2_mask;
    if (leave != NULL) leave();
    if (load_le32(context + 0x6CU) == 1U) {
        if (enter != NULL) enter();
        controller[0] &= UINT32_C(0xFFFFFFEF);
        if (leave != NULL) leave();
    }
    store_le32(context + 0x8CU, 0x20U);
    store_le32(context + 0x6CU, 0U);
    store_le32(context + 0x74U, 0U);
}


int open_cfw_case_verify_selector_bank(
    const uint8_t expected[80], open_cfw_case_selector_read_fn read)
{
    uint32_t value;
    uint32_t index;
    if (expected == NULL || read == NULL) return -1;
    if (read(8U, &value) != 0) return -1;
    if ((uint8_t)value != 0U) return 1;
    if (read(0x0BU, &value) != 0) return -1;
    if (((uint8_t)value & 0x80U) == 0U) return 2;
    for (index = 0U; index < 80U; ++index) {
        if (read(0x10U + index, &value) != 0) return -1;
        if (expected[index] != (uint8_t)value) return 3;
    }
    return 0;
}


int open_cfw_case_read_stable_u16(
    uintptr_t resource, int32_t *value,
    open_cfw_case_resource_read_fn read,
    open_cfw_case_counted_delay_fn delay)
{
    uint32_t first = 0U;
    uint32_t next = 0U;
    uint32_t first_swapped;
    uint32_t next_swapped;
    if (value == NULL || read == NULL) return -1;
    if (read(resource, &first, 2U) != 0) return -1;
    first_swapped = ((first & 0xFFU) << 8U) | ((first >> 8U) & 0xFFU);
    if (delay != NULL) delay(5);
    if (read(resource, &next, 2U) != 0) return -1;
    next_swapped = ((next & 0xFFU) << 8U) | ((next >> 8U) & 0xFFU);
    if (first_swapped != next_swapped) {
        if (delay != NULL) delay(5);
        if (read(resource, &next, 2U) != 0) return -1;
        next_swapped = ((next & 0xFFU) << 8U) | ((next >> 8U) & 0xFFU);
    }
    *value = (int32_t)next_swapped;
    return 0;
}


void open_cfw_case_build_register_descriptor(
    uint32_t descriptor[7], const volatile uint32_t *registers,
    uint32_t fixed_value, open_cfw_case_value_read_fn read_first,
    open_cfw_case_value_read_fn read_second)
{
    uint32_t word;
    uint32_t selector;
    if (descriptor == NULL || registers == NULL) return;
    descriptor[0] = 7U;
    selector = descriptor[1];
    if (selector == 1U) word = registers[11];
    else if (selector == 4U) word = registers[19];
    else if (selector == 8U) word = registers[20];
    else word = registers[12];
    descriptor[2] = word & 0x7FU;
    descriptor[3] = (word & UINT32_C(0x007FFFFF)) >> 16U;
    descriptor[4] = read_first == NULL ? 0U : read_first();
    descriptor[5] = fixed_value;
    descriptor[6] = read_second == NULL ? 0U : read_second();
}


void open_cfw_case_release_peripheral(
    uint32_t current_resource, uint32_t first_resource,
    uint32_t second_resource, volatile uint32_t *first_control,
    volatile uint32_t *second_control, uint32_t second_config_resource,
    open_cfw_case_command_fn configure,
    open_cfw_case_value_write_fn clear_interrupt)
{
    if (current_resource == first_resource) {
        if (first_control != NULL) *first_control &= UINT32_C(0xFFFFBFFF);
        if (configure != NULL) configure(UINT32_C(0x50000000), 0x600U);
        if (clear_interrupt != NULL) clear_interrupt(0x1BU);
    } else if (current_resource == second_resource) {
        if (second_control != NULL)
            *second_control &= UINT32_C(0xFFFBFFFF);
        if (configure != NULL) configure(second_config_resource, 0x300U);
    }
}


int open_cfw_case_initialize_channel_profile(
    uint32_t context[10], uint32_t resource,
    open_cfw_case_resource_status_fn initialize,
    open_cfw_case_context_pair_status_fn configure,
    open_cfw_case_resource_action_fn finalize,
    open_cfw_case_void_action_fn failure)
{
    int status;
    if (context == NULL) return 1;
    context[0] = resource;
    context[2] = 0U;
    context[3] = 0x7FU;
    context[4] = 0x1FU;
    context[5] = 0U;
    context[6] = 0U;
    context[7] = 0U;
    context[8] = UINT32_C(0x40000000);
    context[9] = 0U;
    status = initialize == NULL ? 1 : initialize(context);
    if (status == 0)
        status = configure == NULL ? 1 : configure(context, 0xF0U, 4U);
    if (status != 0 && failure != NULL) failure();
    if (status == 0 && finalize != NULL) finalize(context);
    return status;
}


int open_cfw_case_initialize_controller_profile(
    uint8_t context[64], uint32_t resource, uint32_t secondary,
    uint32_t mode, int reset_first, int start_transfer,
    uint32_t transfer_option, const open_cfw_case_controller_init_ops *ops)
{
    int status;
    if (context == NULL || ops == NULL) return 1;
    if (reset_first != 0 && ops->reset != NULL) ops->reset(context);
    store_le32(context + 0U, resource);
    store_le32(context + 4U, secondary);
    store_le32(context + 8U, 0U);
    store_le32(context + 12U, 0U);
    store_le32(context + 16U, 0U);
    store_le32(context + 20U, mode);
    store_le32(context + 24U, 0U);
    store_le32(context + 28U, 0U);
    store_le32(context + 32U, 0U);
    store_le32(context + 36U, 0U);
    store_le32(context + 40U, 0x10U);
    store_le32(context + 60U, 0x1000U);
    status = ops->prepare == NULL ? 1 : ops->prepare();
    if (status == 0)
        status = ops->field_high == NULL ? 1 : ops->field_high(context, 0U);
    if (status == 0)
        status = ops->field_mid == NULL ? 1 : ops->field_mid(context, 0U);
    if (status == 0)
        status = ops->disable == NULL ? 1 : ops->disable(context);
    if (status != 0) {
        if (ops->failure != NULL) ops->failure();
        return status;
    }
    if (start_transfer != 0 && ops->transfer != NULL)
        (void)ops->transfer(context, transfer_option, 1);
    return 0;
}


int open_cfw_case_initialize_transport_record(
    uint8_t record[80], uint32_t resource, uint32_t descriptor_resource,
    open_cfw_case_status_action_fn platform_initialize,
    open_cfw_case_context_descriptor_status_fn attach,
    open_cfw_case_resource_action_fn finalize,
    open_cfw_case_void_action_fn failure)
{
    uint32_t index;
    uint32_t descriptor[3];
    int status;
    if (record == NULL) return 1;
    descriptor[0] = descriptor_resource;
    descriptor[1] = 0U;
    descriptor[2] = 0U;
    for (index = 0U; index < 80U; ++index) record[index] = 0U;
    store_le32(record + 0U, resource);
    store_le32(record + 4U, resource << 20U);
    store_le32(record + 20U, 4U);
    record[0x1AU] = 1U;
    store_le32(record + 28U, 1U);
    store_le32(record + 52U, 5U);
    status = platform_initialize == NULL ? 1 : platform_initialize();
    if (status != 0) {
        if (failure != NULL) failure();
        return status;
    }
    status = attach == NULL ? 1 : attach(record, descriptor);
    if (status != 0) {
        if (failure != NULL) failure();
        return status;
    }
    if (finalize != NULL) finalize(record);
    return 0;
}


int open_cfw_case_wait_controller_flag2(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t control_mask, open_cfw_case_selector_status_fn query,
    open_cfw_case_tick_read_fn tick_read)
{
    uint32_t start;
    if (context == NULL || controller == NULL || query == NULL ||
        tick_read == NULL) return 1;
    if (query(controller[0]) == 0) return 0;
    if ((controller[2] & (1U << 1U)) == 0U)
        controller[2] = (controller[2] & control_mask) + 0x10U;
    start = tick_read();
    while ((controller[2] & (1U << 2U)) != 0U) {
        if ((uint32_t)(tick_read() - start) > 2U &&
            (controller[2] & (1U << 2U)) != 0U) {
            store_le32(context + 0x58U,
                       load_le32(context + 0x58U) | 0x10U);
            store_le32(context + 0x5CU,
                       load_le32(context + 0x5CU) | 1U);
            return 1;
        }
    }
    return 0;
}


int open_cfw_case_start_controller_flag0(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t control_mask, open_cfw_case_status_action_fn ready,
    open_cfw_case_tick_read_fn tick_read)
{
    uint32_t start;
    uint32_t initial;
    if (context == NULL || controller == NULL || ready == NULL ||
        tick_read == NULL) return 1;
    initial = controller[2];
    if (ready() == 0 || ((initial & 3U) >> 1U) != 0U) return 0;
    if ((controller[2] & 5U) == 1U) {
        controller[2] = (controller[2] & control_mask) + 2U;
        controller[0] = 3U;
        start = tick_read();
        while ((controller[2] & 1U) != 0U) {
            if ((uint32_t)(tick_read() - start) >= 3U) break;
        }
        if ((controller[2] & 1U) == 0U) return 0;
    }
    store_le32(context + 0x58U,
               load_le32(context + 0x58U) | 0x10U);
    store_le32(context + 0x5CU,
               load_le32(context + 0x5CU) | 1U);
    return 1;
}


void open_cfw_case_configure_irq_resource(
    uint32_t current_resource, uint32_t expected_resource,
    volatile uint32_t *clock_control, volatile uint32_t *enable_control,
    open_cfw_case_record_config_fn configure,
    open_cfw_case_dispatch_fn dispatch,
    open_cfw_case_value_write_fn clear_interrupt)
{
    uint32_t record[5];
    uint32_t index;
    if (current_resource != expected_resource) return;
    for (index = 0U; index < 5U; ++index) record[index] = 0U;
    if (clock_control != NULL) *clock_control |= 1U << 20U;
    if (enable_control != NULL) *enable_control |= 1U;
    record[0] = 0x10U;
    record[1] = 3U;
    record[3] = enable_control == NULL ? 0U : (*enable_control & 1U);
    if (configure != NULL) configure(UINT32_C(0x50000000), record);
    if (dispatch != NULL)
        dispatch(0xCU, 3U, 0U, 0U);
    if (clear_interrupt != NULL) clear_interrupt(0xCU);
}


int open_cfw_case_configure_controller_irq(
    uint32_t current_resource, uint32_t expected_resource,
    volatile uint32_t *clock_control, volatile uint32_t *enable_control,
    open_cfw_case_record_status_fn initialize,
    open_cfw_case_dispatch_fn dispatch,
    open_cfw_case_value_write_fn clear_interrupt,
    open_cfw_case_void_action_fn failure)
{
    uint32_t record[11];
    uint32_t index;
    int status;
    if (current_resource != expected_resource) return 0;
    for (index = 0U; index < 11U; ++index) record[index] = 0U;
    record[0] = 0x20000U;
    record[10] = 0x200U;
    status = initialize == NULL ? 1 : initialize(record, 11U);
    if (status != 0) {
        if (failure != NULL) failure();
        return status;
    }
    if (clock_control != NULL) *clock_control |= 0x8000U;
    if (enable_control != NULL) *enable_control |= 1U;
    if (dispatch != NULL) dispatch(2U, 3U, 0U, 0U);
    if (clear_interrupt != NULL) clear_interrupt(2U);
    return 0;
}


int open_cfw_case_initialize_application_profile(
    open_cfw_case_context_value_status_fn configure_mode,
    open_cfw_case_record_status_fn initialize,
    open_cfw_case_context_pair_status_fn attach,
    open_cfw_case_void_action_fn failure)
{
    uint32_t profile[14];
    uint32_t command_record[4];
    uint32_t index;
    int status;
    for (index = 0U; index < 14U; ++index) profile[index] = 0U;
    status = configure_mode == NULL ? 1 : configure_mode(NULL, 0x200U);
    if (status != 0) goto failed;
    profile[0] = 10U;
    profile[3] = 0x100U;
    profile[5] = 0x40U;
    profile[6] = 1U;
    profile[7] = 2U;
    profile[8] = 2U;
    profile[9] = 0U;
    profile[10] = 0U;
    profile[11] = 8U;
    profile[12] = 0x20000U;
    profile[13] = 0x2000000U;
    status = initialize == NULL ? 1 : initialize(profile, 14U);
    if (status != 0) goto failed;
    command_record[0] = 7U;
    command_record[1] = 2U;
    command_record[2] = 0U;
    command_record[3] = 0U;
    status = attach == NULL ? 1 : attach(command_record, 2U, 0U);
    if (status != 0) goto failed;
    return 0;
failed:
    if (failure != NULL) failure();
    return status;
}


uint64_t open_cfw_case_wait_controller_channels(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t result_tag, uint32_t budget,
    open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_context_mask_status_fn wait_channel)
{
    uint32_t started;
    uint32_t tag = result_tag;
    if (context == NULL || controller == NULL || tick_read == NULL ||
        wait_channel == NULL) return 3U;
    store_le32(context + 0x90U, 0U);
    started = tick_read();
    if ((controller[0] & (1U << 3U)) != 0U) {
        tag = budget;
        if (wait_channel(context, 0x200000U, started, budget) != 0)
            return ((uint64_t)tag << 32U) | 3U;
    }
    if ((controller[0] & (1U << 2U)) != 0U) {
        if (wait_channel(context, 0x400000U, started, budget) != 0)
            return ((uint64_t)tag << 32U) | 3U;
    }
    store_le32(context + 0x88U, 0x20U);
    store_le32(context + 0x8CU, 0x20U);
    store_le32(context + 0x6CU, 0U);
    store_le32(context + 0x70U, 0U);
    context[0x84U] = 0U;
    return (uint64_t)tag << 32U;
}


static int serial_read_register(
    uint32_t write_address, uint32_t read_address, uint32_t selector,
    uint8_t *output, uint32_t length, volatile uint8_t *state,
    const open_cfw_case_serial_bus_ops *ops)
{
    uint32_t index;
    if (state != NULL) *state = 0U;
    if ((output == NULL && length != 0U) || ops == NULL ||
        ops->start == NULL || ops->write == NULL ||
        ops->acknowledge == NULL || ops->read == NULL ||
        ops->acknowledge_more == NULL || ops->acknowledge_last == NULL ||
        ops->stop == NULL) return 0;
    ops->start();
    ops->write(write_address);
    if (ops->acknowledge() != 0) goto failed;
    ops->write(selector);
    if (ops->acknowledge() != 0) goto failed;
    ops->start();
    ops->write(read_address);
    if (ops->acknowledge() != 0) goto failed;
    for (index = 0U; index < length; ++index) {
        output[index] = (uint8_t)ops->read();
        if (index == length - 1U)
            ops->acknowledge_last();
        else
            ops->acknowledge_more();
    }
    ops->stop();
    return 1;
failed:
    ops->stop();
    return 0;
}


int open_cfw_case_serial_read_200(
    uint32_t selector, uint8_t *output, uint32_t length,
    volatile uint8_t *state, const open_cfw_case_serial_bus_ops *ops)
{
    return serial_read_register(
        200U, 0xC9U, selector, output, length, state, ops);
}


int open_cfw_case_serial_read_70(
    uint32_t selector, uint8_t *output, uint32_t length,
    volatile uint8_t *state, const open_cfw_case_serial_bus_ops *ops)
{
    return serial_read_register(
        0x70U, 0x71U, selector, output, length, state, ops);
}


uint16_t open_cfw_case_trimmed_average8(
    void *resource, open_cfw_case_resource_action_fn initialize,
    open_cfw_case_context_value_status_fn configure,
    open_cfw_case_resource_value_read_fn sample,
    open_cfw_case_resource_action_fn finalize)
{
    uint32_t index;
    uint32_t value;
    uint32_t minimum = UINT32_MAX;
    uint32_t maximum = 0U;
    uint32_t sum = 0U;
    if (sample == NULL) return 0U;
    if (initialize != NULL) initialize(resource);
    if (configure != NULL) (void)configure(resource, 10U);
    for (index = 0U; index < 8U; ++index) {
        value = sample(resource);
        if (value < minimum) minimum = value;
        if (value > maximum) maximum = value;
        sum += value;
    }
    if (finalize != NULL) finalize(resource);
    return (uint16_t)((sum - minimum - maximum) / 6U);
}


uint32_t open_cfw_case_derive_clock(const uint32_t registers[4],
                                    uint32_t base_clock)
{
    uint32_t mode;
    uint32_t clock;
    uint32_t divider;
    if (registers == NULL) return 0U;
    mode = (registers[2] & 0x3FU) >> 3U;
    if (mode == 0U) {
        divider = 1U << ((registers[0] & 0x3FFFU) >> 11U);
        return base_clock / divider;
    }
    if (mode == 1U) return base_clock >> 1U;
    if (mode == 2U) {
        clock = (registers[3] & 3U) == 3U ? base_clock >> 1U : base_clock;
        clock /= ((registers[3] & 0x7FU) >> 4U) + 1U;
        clock *= (registers[3] & 0x7FFFU) >> 8U;
        return clock / ((registers[3] >> 29U) + 1U);
    }
    if (mode == 3U) return 32000U;
    if (mode == 4U) return 0x8000U;
    return 0U;
}


int open_cfw_case_start_controller(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_tick_read_fn tick_read)
{
    uint32_t started;
    if (context == NULL || controller == NULL || tick_read == NULL) return 3;
    if (context[40] == 1U) return 2;
    context[40] = 1U;
    context[41] = 2U;
    controller[9] = 0xCAU;
    controller[9] = 0x53U;
    controller[6] &= ~(1U << 10U);
    controller[6] &= ~(1U << 14U);
    started = tick_read();
    while ((uint32_t)(tick_read() - started) < 1001U) {
        if ((controller[3] & (1U << 2U)) != 0U) {
            controller[9] = 0xFFU;
            context[41] = 1U;
            context[40] = 0U;
            return 0;
        }
    }
    controller[9] = 0xFFU;
    context[41] = 3U;
    context[40] = 0U;
    return 3;
}


void open_cfw_case_apply_controller_profile(
    volatile uint32_t *controller, const uint32_t profile[6],
    int apply_field_4_6, int apply_field_8_9, int apply_word12)
{
    uint32_t control;
    if (controller == NULL || profile == NULL) return;
    control = controller[0];
    if (apply_field_4_6 != 0)
        control = (control & UINT32_C(0xFFFFFF8F)) | profile[1];
    if (apply_field_8_9 != 0)
        control = (control & UINT32_C(0xFFFFFCFF)) | profile[3];
    controller[0] = (control & UINT32_C(0xFFFFFF7F)) | profile[5];
    controller[11] = profile[2];
    controller[10] = profile[0];
    if (apply_word12 != 0) controller[12] = profile[4];
    controller[5] = 1U;
}


void open_cfw_case_copy64_protected(
    uint32_t destination[64], const uint32_t source[64],
    volatile uint32_t *controller,
    open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_void_action_fn disable_irq,
    open_cfw_case_irq_restore_fn restore_irq)
{
    uint32_t index;
    int privileged = is_privileged != NULL && is_privileged() != 0;
    int enabled = privileged && irq_enabled != NULL && irq_enabled() != 0;
    if (destination == NULL || source == NULL || controller == NULL) return;
    controller[5] |= 0x40000U;
    if (disable_irq != NULL) disable_irq();
    for (index = 0U; index < 64U; ++index) destination[index] = source[index];
    while (((controller[4] & 0x3FFFFU) >> 16U) != 0U) {
    }
    if (privileged && restore_irq != NULL) restore_irq(enabled);
}


int open_cfw_case_run_controller_range(
    uint8_t state[8], volatile uint32_t *controller,
    const uint32_t operation[4], uint32_t *failed_index,
    open_cfw_case_selector_status_fn wait,
    open_cfw_case_value_write_fn single_action,
    open_cfw_case_pair_action_fn range_action)
{
    uint32_t index;
    int status;
    if (state == NULL || controller == NULL || operation == NULL ||
        failed_index == NULL || wait == NULL) return 1;
    if (state[0] == 1U) return 2;
    state[0] = 1U;
    store_le32(state + 4U, 0U);
    status = wait(1000U);
    if (status == 0) {
        if (operation[0] == 4U) {
            if (single_action != NULL) single_action(operation[1]);
            status = wait(1000U);
        } else {
            *failed_index = UINT32_MAX;
            for (index = operation[2];
                 index < operation[2] + operation[3]; ++index) {
                if (range_action != NULL) range_action(operation[1], index);
                status = wait(1000U);
                if (status != 0) {
                    *failed_index = index;
                    break;
                }
            }
            controller[5] &= ~2U;
        }
    }
    state[0] = 0U;
    return status;
}


int open_cfw_case_copy_controller_words(
    uint8_t state[8], volatile uint32_t *controller, uint32_t mask,
    uint32_t destination[64], const uint32_t source[64],
    open_cfw_case_selector_status_fn wait,
    open_cfw_case_copy_action_fn single_copy)
{
    uint32_t index;
    int status;
    if (state == NULL || controller == NULL || destination == NULL ||
        source == NULL || wait == NULL) return 1;
    if (state[0] == 1U) return 2;
    state[0] = 1U;
    store_le32(state + 4U, 0U);
    status = wait(1000U);
    if (status == 0) {
        if (mask == 1U && single_copy != NULL) {
            single_copy(destination, source);
        } else {
            for (index = 0U; index < 64U; ++index)
                destination[index] = source[index];
        }
        status = wait(1000U);
        controller[5] &= ~mask;
    }
    state[0] = 0U;
    return status;
}


int open_cfw_case_prepare_controller_context(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_resource_action_fn initialize,
    open_cfw_case_resource_status_fn query,
    open_cfw_case_resource_action_fn stop,
    open_cfw_case_resource_status_fn wait_channels)
{
    int status;
    if (context == NULL || controller == NULL || query == NULL ||
        wait_channels == NULL) return 1;
    if (load_le32(context + 0x88U) == 0U) {
        context[0x84U] = 0U;
        if (initialize != NULL) initialize(context);
    }
    store_le32(context + 0x88U, 0x24U);
    controller[0] &= ~1U;
    status = query(context);
    if (status == 1) return 1;
    if (load_le32(context + 40U) != 0U && stop != NULL) stop(context);
    controller[1] &= UINT32_C(0xFFFFB7FF);
    controller[2] &= UINT32_C(0xFFFFFFD5);
    controller[0] |= 1U;
    return wait_channels(context);
}


void open_cfw_case_enable_interrupt_source(
    volatile uint32_t *enable, volatile uint32_t *route,
    uint32_t route_mask, open_cfw_case_dispatch_fn dispatch,
    open_cfw_case_selector_status_fn configure)
{
    if (enable != NULL) *enable |= 1U;
    if (route != NULL) *route |= route_mask;
    if (dispatch != NULL) dispatch(UINT32_C(0xFFFFFFFE), 3U, 0U, 0U);
    if (configure != NULL) (void)configure(0x600U);
}


int open_cfw_case_initialize_interrupt_path(
    uint32_t selector, uint32_t resource, uint32_t secondary,
    uint32_t period, uint32_t divisor, int double_period,
    uint32_t profile[7], volatile uint32_t *control,
    uint32_t *selected, open_cfw_case_resource_status_fn initialize,
    open_cfw_case_resource_status_fn enable,
    open_cfw_case_value_write_fn configure_interrupt,
    open_cfw_case_dispatch_fn dispatch)
{
    int status;
    if (profile == NULL || control == NULL || divisor == 0U ||
        initialize == NULL || enable == NULL) return 1;
    *control |= 0x40000U;
    if (double_period != 0) period <<= 1U;
    period /= divisor;
    profile[0] = resource;
    profile[1] = period - 1U;
    profile[2] = 0U;
    profile[3] = secondary;
    profile[4] = 0U;
    profile[6] = 0U;
    status = initialize(profile);
    if (status == 0) status = enable(profile);
    if (status == 0) {
        if (configure_interrupt != NULL) configure_interrupt(0x16U);
        if (selector < 4U) {
            if (dispatch != NULL) dispatch(0x16U, selector, 0U, 0U);
            if (selected != NULL) *selected = selector;
        } else {
            status = 1;
        }
    }
    return status;
}


int open_cfw_case_activate_controller(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t controller6_mask,
    open_cfw_case_resource_action_fn configure_irq,
    open_cfw_case_resource_status_fn wait_ready,
    open_cfw_case_resource_status_fn prepare)
{
    int status = 0;
    if (context == NULL || controller == NULL || wait_ready == NULL ||
        prepare == NULL) return 1;
    if (context[41] == 0U) {
        context[40] = 0U;
        store_le32(context + 4U, 0x8800U);
        if (configure_irq != NULL) configure_irq(context);
    }
    context[41] = 2U;
    if ((controller[3] & (1U << 4U)) == 0U) {
        controller[9] = 0xCAU;
        controller[9] = 0x53U;
        status = wait_ready(context);
        if (status == 0) {
            controller[6] &= controller6_mask;
            controller[6] |= load_le32(context + 8U) |
                             load_le32(context + 20U) |
                             load_le32(context + 28U);
            controller[4] = load_le32(context + 16U) |
                            ((uint32_t)(context[12] |
                             ((uint16_t)context[13] << 8U)) << 16U);
            status = prepare(context);
            if (status == 0) {
                controller[6] &= UINT32_C(0x1FFFFFFF);
                controller[6] |= load_le32(context + 36U) |
                                 load_le32(context + 32U) |
                                 load_le32(context + 24U);
            }
        }
        controller[9] = 0xFFU;
        if (status != 0) return status;
    }
    context[41] = 1U;
    return 0;
}


int open_cfw_case_program_selector_bank(
    const uint8_t bank[80], open_cfw_case_selector_status_fn reset,
    open_cfw_case_byte_action_fn write,
    open_cfw_case_counted_delay_fn delay,
    open_cfw_case_byte_read_fn read)
{
    uint32_t index;
    uint8_t value;
    if (bank == NULL || reset == NULL || write == NULL || read == NULL)
        return -1;
    if (reset(8U) < 0) return -1;
    for (index = 0U; index < 80U; ++index) {
        if (write((index + 0x10U) & 0xFFU, bank[index]) != 0) return -1;
    }
    if (write(0xBU, 0x80U) != 0 || write(0xAU, 0U) != 0 ||
        write(8U, 0x30U) != 0) return -1;
    if (delay != NULL) delay(0x15);
    if (write(8U, 0U) < 0) return -1;
    if (delay != NULL) delay(0xB);
    for (index = 0U; index < 50U; ++index) {
        if (delay != NULL) delay(0x65);
        value = 0U;
        if (read(0xA7U, &value) == 0 && ((value & 0xFU) >> 2U) == 3U)
            return 0;
    }
    (void)reset(8U);
    return -1;
}


uint32_t open_cfw_case_event_group_set_bits(
    open_cfw_case_event_group *group, uint32_t bits,
    open_cfw_case_void_action_fn suspend_scheduler,
    open_cfw_case_waiter_unblock_fn unblock,
    open_cfw_case_void_action_fn resume_scheduler,
    open_cfw_case_void_action_fn failure)
{
    open_cfw_case_event_waiter *waiter;
    open_cfw_case_event_waiter *next;
    uint32_t clear_bits = 0U;
    if (group == NULL || (bits >> 24U) != 0U) {
        if (failure != NULL) failure();
        return group == NULL ? 0U : group->bits;
    }
    if (suspend_scheduler != NULL) suspend_scheduler();
    group->bits |= bits;
    waiter = group->waiters;
    while (waiter != NULL) {
        uint32_t control = waiter->event_item_value & UINT32_C(0xFF000000);
        uint32_t waited = waiter->event_item_value & UINT32_C(0x00FFFFFF);
        int matched = (control & UINT32_C(0x04000000)) != 0U
            ? (waited & ~group->bits) == 0U
            : (waited & group->bits) != 0U;
        next = waiter->next;
        if (matched) {
            if ((control & UINT32_C(0x01000000)) != 0U)
                clear_bits |= waited;
            if (unblock != NULL)
                unblock(waiter, group->bits | UINT32_C(0x02000000));
        }
        waiter = next;
    }
    group->bits &= ~clear_bits;
    if (resume_scheduler != NULL) resume_scheduler();
    return group->bits;
}


static void receive_value(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    uint32_t width, open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_irq_restore_fn restore_irq,
    open_cfw_case_resource_action_fn service,
    open_cfw_case_context_short_fn finalize)
{
    uint16_t remaining;
    uint16_t mask;
    uint32_t value;
    int privileged;
    int enabled;
    if (context == NULL || controller == NULL || cursor == NULL ||
        *cursor == NULL) return;
    if (load_le32(context + 0x8CU) != 0x22U) {
        controller[6] |= 8U;
        return;
    }
    mask = (uint16_t)(context[0x60U] | ((uint16_t)context[0x61U] << 8U));
    value = controller[9] & mask;
    (*cursor)[0] = (uint8_t)value;
    if (width == 2U) (*cursor)[1] = (uint8_t)(value >> 8U);
    *cursor += width;
    remaining = (uint16_t)(context[0x5EU] |
                           ((uint16_t)context[0x5FU] << 8U));
    --remaining;
    context[0x5EU] = (uint8_t)remaining;
    context[0x5FU] = (uint8_t)(remaining >> 8U);
    if (remaining != 0U) return;
    privileged = is_privileged != NULL && is_privileged() != 0;
    enabled = privileged && irq_enabled != NULL && irq_enabled() != 0;
    controller[0] &= UINT32_C(0xFFFFFEDF);
    controller[2] &= UINT32_C(0xFFFFFFFE);
    if (privileged && restore_irq != NULL) restore_irq(enabled);
    store_le32(context + 0x8CU, 0x20U);
    store_le32(context + 0x74U, 0U);
    store_le32(context + 0x70U, 0U);
    if (load_le32(context + 0x6CU) != 1U) {
        if (service != NULL) service(context);
        return;
    }
    store_le32(context + 0x6CU, 0U);
    controller[0] &= UINT32_C(0xFFFFFFEF);
    if ((controller[7] & (1U << 4U)) == 0U) controller[8] = 0x10U;
    if (finalize != NULL)
        finalize(context, (int16_t)(context[0x5CU] |
                 ((uint16_t)context[0x5DU] << 8U)));
}


void open_cfw_case_receive_u16(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_irq_restore_fn restore_irq,
    open_cfw_case_resource_action_fn service,
    open_cfw_case_context_short_fn finalize)
{
    receive_value(context, controller, cursor, 2U, is_privileged,
                  irq_enabled, restore_irq, service, finalize);
}


void open_cfw_case_receive_u8(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_irq_restore_fn restore_irq,
    open_cfw_case_resource_action_fn service,
    open_cfw_case_context_short_fn finalize)
{
    receive_value(context, controller, cursor, 1U, is_privileged,
                  irq_enabled, restore_irq, service, finalize);
}


int open_cfw_case_start_peripheral(
    uint8_t *context, volatile uint32_t *controller, uint32_t status_mask,
    int require_delay, uint32_t delay_numerator, uint32_t delay_divisor,
    open_cfw_case_resource_status_fn query,
    open_cfw_case_tick_read_fn tick_read)
{
    uint32_t start;
    uint32_t delay;
    if (context == NULL || controller == NULL || query == NULL ||
        tick_read == NULL) return 1;
    if (query((void *)controller) != 0) return 0;
    if ((controller[2] & status_mask) == 0U) {
        controller[2] = (controller[2] & ~status_mask) + 1U;
        if (require_delay != 0 && delay_divisor != 0U) {
            delay = delay_numerator / delay_divisor + 1U;
            while (delay-- != 0U) {
            }
        }
        if (context[25] == 1U) return 0;
        start = tick_read();
        do {
            if ((controller[0] & 1U) != 0U) return 0;
            if (query((void *)controller) == 0)
                controller[2] = (controller[2] & ~status_mask) + 1U;
        } while ((uint32_t)(tick_read() - start) < 3U ||
                 (controller[0] & 1U) != 0U);
    }
    store_le32(context + 0x58U, load_le32(context + 0x58U) | 0x10U);
    store_le32(context + 0x5CU, load_le32(context + 0x5CU) | 1U);
    return 1;
}


int open_cfw_case_wait_peripheral(
    uint8_t *context, volatile uint32_t *controller, uint32_t timeout,
    open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_resource_status_fn status_query,
    open_cfw_case_resource_status_fn clear_error)
{
    uint32_t mask;
    uint32_t start;
    if (context == NULL || controller == NULL || tick_read == NULL)
        return 3;
    if (load_le32(context + 20U) == 8U) {
        mask = 8U;
    } else {
        if ((controller[3] & 1U) != 0U) {
            store_le32(context + 0x58U,
                       load_le32(context + 0x58U) | 0x20U);
            return 1;
        }
        mask = 4U;
    }
    start = tick_read();
    do {
        if ((controller[0] & mask) != 0U) {
            store_le32(context + 0x58U,
                       load_le32(context + 0x58U) | 0x200U);
            if (status_query != NULL && status_query((void *)controller) != 0 &&
                context[26] == 0U && (controller[0] & 8U) != 0U) {
                if (clear_error != NULL && clear_error((void *)controller) == 0) {
                    controller[1] &= UINT32_C(0xFFFFFFF3);
                    store_le32(context + 0x58U,
                               (load_le32(context + 0x58U) & ~0x100U) | 1U);
                } else {
                    store_le32(context + 0x58U,
                               load_le32(context + 0x58U) | 0x20U);
                    store_le32(context + 0x5CU,
                               load_le32(context + 0x5CU) | 1U);
                }
            }
            if (context[24] == 0U) controller[0] = 0xCU;
            return 0;
        }
    } while (timeout == UINT32_MAX ||
             (timeout != 0U &&
              (uint32_t)(tick_read() - start) <= timeout));
    store_le32(context + 0x58U, load_le32(context + 0x58U) | 4U);
    context[0x54U] = 0U;
    return 3;
}


void open_cfw_case_release_pins(
    volatile uint32_t *controller, uint32_t pin_mask,
    uint32_t controller_index, open_cfw_case_pin_state *state)
{
    uint32_t pin;
    if (controller == NULL || state == NULL) return;
    for (pin = 0U; (pin_mask >> pin) != 0U && pin < 32U; ++pin) {
        uint32_t bit = 1U << pin;
        uint32_t owner_shift;
        uint32_t owner_mask;
        uint32_t field_mask;
        if ((pin_mask & bit) == 0U) continue;
        owner_shift = (pin & 3U) << 3U;
        owner_mask = 0xFU << owner_shift;
        if ((state->ownership[pin >> 2U] & owner_mask) ==
            (controller_index << owner_shift)) {
            state->active[0] &= ~bit;
            state->active[1] &= ~bit;
            state->active[2] &= ~bit;
            state->active[3] &= ~bit;
            state->ownership[pin >> 2U] &= ~owner_mask;
        }
        field_mask = 3U << ((pin & 0x7FU) << 1U);
        controller[0] |= field_mask;
        controller[(pin >> 3U) + 8U] &=
            ~(0xFU << ((pin & 7U) << 2U));
        controller[2] &= ~field_mask;
        controller[1] &= ~bit;
        controller[3] &= ~field_mask;
    }
}


void open_cfw_case_configure_resource_irq(
    uint32_t resource, uint32_t first_resource, uint32_t second_resource,
    volatile uint32_t *clock, volatile uint32_t *enable,
    open_cfw_case_record_status_fn initialize,
    open_cfw_case_record_config_fn configure,
    open_cfw_case_dispatch_fn dispatch,
    open_cfw_case_value_write_fn clear_interrupt,
    open_cfw_case_void_action_fn failure)
{
    uint32_t init_record[11];
    uint32_t config_record[5];
    uint32_t index;
    int status;
    for (index = 0U; index < 11U; ++index) init_record[index] = 0U;
    for (index = 0U; index < 5U; ++index) config_record[index] = 0U;
    if (resource == first_resource) {
        init_record[0] = 1U;
        init_record[1] = 2U;
        status = initialize == NULL ? 1 : initialize(init_record, 11U);
        if (status != 0) {
            if (failure != NULL) failure();
            return;
        }
        if (clock != NULL) clock[16] |= 0x4000U;
        if (enable != NULL) *enable |= 1U;
        config_record[0] = 0x600U;
        config_record[1] = 2U;
        config_record[3] = enable == NULL ? 0U : (*enable & 1U);
        if (configure != NULL)
            configure(UINT32_C(0x50000000), config_record);
        if (dispatch != NULL) dispatch(0x1BU, 3U, 0U, 0U);
        if (clear_interrupt != NULL) clear_interrupt(0x1BU);
    } else if (resource == second_resource) {
        init_record[0] = 4U;
        status = initialize == NULL ? 1 : initialize(init_record, 11U);
        if (status != 0) {
            if (failure != NULL) failure();
            return;
        }
        if (clock != NULL) clock[15] |= 0x40000U;
        if (enable != NULL) *enable |= 2U;
        config_record[0] = 0x300U;
        config_record[1] = 2U;
        config_record[3] = enable == NULL ? 0U : (*enable & 2U);
        if (configure != NULL) configure(second_resource, config_record);
    }
}


int open_cfw_case_read_controller_blocking(
    uint8_t *context, volatile uint32_t *controller, void *output,
    uint32_t count, uint32_t timeout, open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_wait_condition_fn wait)
{
    uint8_t *bytes = output;
    uint16_t *words = output;
    uint32_t mode;
    uint16_t mask;
    uint32_t index;
    uint32_t started;
    int word_mode;
    if (context == NULL || controller == NULL || output == NULL ||
        count == 0U || tick_read == NULL || wait == NULL) return 1;
    if (load_le32(context + 0x8CU) != 0x20U) return 2;
    mode = load_le32(context + 8U);
    word_mode = mode == 0x1000U && load_le32(context + 16U) == 0U;
    if (word_mode && ((uintptr_t)output & 1U) != 0U) return 1;
    store_le32(context + 0x90U, 0U);
    store_le32(context + 0x8CU, 0x22U);
    store_le32(context + 0x6CU, 0U);
    context[0x5CU] = (uint8_t)count;
    context[0x5DU] = (uint8_t)(count >> 8U);
    context[0x5EU] = (uint8_t)count;
    context[0x5FU] = (uint8_t)(count >> 8U);
    if (word_mode) mask = 0xFFU;
    else if (mode == 0U && load_le32(context + 16U) != 0U) mask = 0x7FU;
    else if (mode == 0x10000000U && load_le32(context + 16U) != 0U)
        mask = 0x3FU;
    else mask = 0U;
    context[0x60U] = (uint8_t)mask;
    context[0x61U] = (uint8_t)(mask >> 8U);
    started = tick_read();
    for (index = 0U; index < count; ++index) {
        if (wait(context, controller, 0x20U, 0, started, timeout) != 0)
            return 3;
        if (word_mode) words[index] = (uint16_t)controller[9] & mask;
        else bytes[index] = (uint8_t)controller[9] & (uint8_t)mask;
        context[0x5EU] = (uint8_t)(count - index - 1U);
        context[0x5FU] = (uint8_t)((count - index - 1U) >> 8U);
    }
    store_le32(context + 0x8CU, 0x20U);
    return 0;
}


int open_cfw_case_write_controller_blocking(
    uint8_t *context, volatile uint32_t *controller, const void *input,
    uint32_t count, uint32_t timeout, open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_wait_condition_fn wait)
{
    const uint8_t *bytes = input;
    const uint16_t *words = input;
    uint32_t mode;
    uint32_t index;
    uint32_t started;
    int word_mode;
    if (context == NULL || controller == NULL || input == NULL ||
        count == 0U || tick_read == NULL || wait == NULL) return 1;
    if (load_le32(context + 0x88U) != 0x20U) return 2;
    mode = load_le32(context + 8U);
    word_mode = mode == 0x1000U && load_le32(context + 16U) == 0U;
    if (word_mode && ((uintptr_t)input & 1U) != 0U) return 1;
    store_le32(context + 0x90U, 0U);
    store_le32(context + 0x88U, 0x21U);
    context[0x54U] = (uint8_t)count;
    context[0x55U] = (uint8_t)(count >> 8U);
    context[0x56U] = (uint8_t)count;
    context[0x57U] = (uint8_t)(count >> 8U);
    started = tick_read();
    for (index = 0U; index < count; ++index) {
        if (wait(context, controller, 0x80U, 0, started, timeout) != 0)
            return 3;
        controller[10] = word_mode ? (words[index] & 0x1FFU) : bytes[index];
        context[0x56U] = (uint8_t)(count - index - 1U);
        context[0x57U] = (uint8_t)((count - index - 1U) >> 8U);
    }
    if (wait(context, controller, 0x40U, 0, started, timeout) != 0) return 3;
    store_le32(context + 0x88U, 0x20U);
    return 0;
}


void open_cfw_case_apply_context_options(
    volatile uint32_t *controller, const uint32_t options[20])
{
    uint16_t flags;
    if (controller == NULL || options == NULL) return;
    flags = (uint16_t)options[10];
    if ((flags & (1U << 0U)) != 0U)
        controller[1] = (controller[1] & UINT32_C(0xFFFDFFFF)) | options[11];
    if ((flags & (1U << 1U)) != 0U)
        controller[1] = (controller[1] & UINT32_C(0xFFFEFFFF)) | options[12];
    if ((flags & (1U << 2U)) != 0U)
        controller[1] = (controller[1] & UINT32_C(0xFFFBFFFF)) | options[13];
    if ((flags & (1U << 3U)) != 0U)
        controller[1] = (controller[1] & UINT32_C(0xFFFF7FFF)) | options[14];
    if ((flags & (1U << 4U)) != 0U)
        controller[2] = (controller[2] & UINT32_C(0xFFFFEFFF)) | options[15];
    if ((flags & (1U << 5U)) != 0U)
        controller[2] = (controller[2] & UINT32_C(0xFFFFDFFF)) | options[16];
    if ((flags & (1U << 6U)) != 0U) {
        controller[1] = (controller[1] & UINT32_C(0xFFEFFFFF)) | options[17];
        if (options[17] == 0x100000U)
            controller[1] = (controller[1] & UINT32_C(0xFF9FFFFF)) | options[18];
    }
    if ((flags & (1U << 7U)) != 0U)
        controller[1] = (controller[1] & UINT32_C(0xFFF7FFFF)) | options[19];
}


int open_cfw_case_wait_condition(
    uint8_t *context, volatile uint32_t *controller, uint32_t mask,
    int expected, uint32_t started, uint32_t timeout,
    open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_irq_restore_fn restore_irq)
{
    int privileged;
    int enabled;
    if (context == NULL || controller == NULL || tick_read == NULL) return 3;
    for (;;) {
        if ((((mask & ~controller[7]) == 0U) ? 1 : 0) != (expected != 0))
            return 0;
        if (timeout != UINT32_MAX &&
            (timeout == 0U || (uint32_t)(tick_read() - started) > timeout))
            break;
        if ((controller[0] & (1U << 2U)) != 0U &&
            (controller[7] & (1U << 11U)) != 0U) {
            controller[8] = 0x800U;
            break;
        }
    }
    privileged = is_privileged != NULL && is_privileged() != 0;
    enabled = privileged && irq_enabled != NULL && irq_enabled() != 0;
    controller[0] &= UINT32_C(0xFFFFFE5F);
    controller[2] &= UINT32_C(0xFFFFFFFE);
    if (privileged && restore_irq != NULL) restore_irq(enabled);
    store_le32(context + 0x88U, 0x20U);
    store_le32(context + 0x8CU, 0x20U);
    store_le32(context + 0x90U, 0x20U);
    context[0x84U] = 0U;
    return 3;
}


void open_cfw_case_begin_receive(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    uint8_t *output, uint32_t count, uint16_t special_mask,
    uint32_t direct_descriptor, uint32_t direct_word_descriptor,
    uint32_t dma_descriptor, uint32_t dma_word_descriptor,
    open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_irq_restore_fn restore_irq)
{
    uint32_t mode;
    uint16_t mask;
    int word_mode;
    int privileged;
    int enabled;
    if (context == NULL || controller == NULL || cursor == NULL) return;
    *cursor = output;
    context[0x5CU] = (uint8_t)count;
    context[0x5DU] = (uint8_t)(count >> 8U);
    context[0x5EU] = (uint8_t)count;
    context[0x5FU] = (uint8_t)(count >> 8U);
    store_le32(context + 0x74U, 0U);
    mode = load_le32(context + 8U);
    word_mode = mode == 0x1000U && load_le32(context + 16U) == 0U;
    if (word_mode) mask = special_mask;
    else if (mode == 0U && load_le32(context + 16U) == 0U) mask = 0xFFU;
    else if (mode == 0U) mask = 0x7FU;
    else if (mode == 0x10000000U && load_le32(context + 16U) != 0U)
        mask = 0x3FU;
    else mask = 0U;
    context[0x60U] = (uint8_t)mask;
    context[0x61U] = (uint8_t)(mask >> 8U);
    store_le32(context + 0x90U, 0U);
    store_le32(context + 0x8CU, 0x22U);
    privileged = is_privileged != NULL && is_privileged() != 0;
    enabled = privileged && irq_enabled != NULL && irq_enabled() != 0;
    controller[2] |= 1U;
    if (privileged && restore_irq != NULL) restore_irq(enabled);
    if (load_le32(context + 0x64U) == 0x20000000U &&
        (uint16_t)(context[0x68U] | ((uint16_t)context[0x69U] << 8U)) <= count) {
        store_le32(context + 0x74U,
                   word_mode ? dma_word_descriptor : dma_descriptor);
        if (!word_mode && load_le32(context + 16U) != 0U)
            controller[0] |= 0x100U;
        controller[2] |= 0x10000000U;
    } else {
        store_le32(context + 0x74U,
                   word_mode ? direct_word_descriptor : direct_descriptor);
        controller[0] |= word_mode || load_le32(context + 16U) == 0U
            ? 0x20U : 0x120U;
    }
}


static void configure_route_record(
    uintptr_t resource, uint32_t first, uint32_t second, uint32_t third,
    uint32_t fourth, open_cfw_case_record_config_fn configure)
{
    uint32_t record[5];
    record[0] = first;
    record[1] = second;
    record[2] = third;
    record[3] = fourth;
    record[4] = 0U;
    if (configure != NULL) configure(resource, record);
}


void open_cfw_case_configure_platform_routes(
    volatile uint32_t *clock, volatile uint32_t *enable,
    uint32_t secondary_resource, uint32_t profile_resource,
    uint32_t profile_value_a, uint32_t profile_value_b,
    open_cfw_case_command_fn command,
    open_cfw_case_record_config_fn configure,
    open_cfw_case_dispatch_fn dispatch,
    open_cfw_case_value_write_fn clear_interrupt)
{
    if (enable != NULL) *enable |= 7U;
    if (command != NULL) {
        command(UINT32_C(0x50000000), 0xCAU);
        command(secondary_resource, 4U);
    }
    configure_route_record(profile_resource, profile_value_a, 3U, 0U,
                           enable == NULL ? 0U : (*enable & 1U), configure);
    configure_route_record(UINT32_C(0x50000000), 1U, 0x210000U, 0U, 0U,
                           configure);
    configure_route_record(UINT32_C(0x50000000), 0xCAU, 1U, 0U, 0U,
                           configure);
    configure_route_record(UINT32_C(0x50000000), 4U, 0x310000U, 0U, 0U,
                           configure);
    configure_route_record(UINT32_C(0x50000000), profile_value_b, 3U, 0U, 0U,
                           configure);
    configure_route_record(secondary_resource, 0xC1U, 3U, 0U, 0U, configure);
    configure_route_record(secondary_resource, 2U, 0x110000U, 0U, 0U,
                           configure);
    configure_route_record(secondary_resource, 4U, 1U, 0U, 0U, configure);
    configure_route_record(secondary_resource, 0x20U, 0x310000U, 0U, 0U,
                           configure);
    if (clock != NULL) *clock |= 1U;
    if (dispatch != NULL) {
        dispatch(5U, 3U, 0U, 0U);
        dispatch(6U, 3U, 0U, 0U);
        dispatch(7U, 3U, 0U, 0U);
    }
    if (clear_interrupt != NULL) {
        clear_interrupt(5U);
        clear_interrupt(6U);
        clear_interrupt(7U);
    }
}


int open_cfw_case_configure_clock_path(
    const uint32_t configuration[4], uint32_t selector,
    volatile uint32_t *selector_register, volatile uint32_t clock_registers[4],
    uint32_t selector_timeout, const uint8_t *shift_table,
    uint32_t shift_table_length, uint32_t base_clock,
    uint32_t *derived_clock,
    open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_selector_status_fn initialize_interrupt)
{
    uint32_t started;
    uint32_t mode;
    uint32_t shift_index;
    uint32_t clock;
    if (configuration == NULL || selector_register == NULL ||
        clock_registers == NULL || derived_clock == NULL || tick_read == NULL)
        return 1;
    if ((*selector_register & 7U) < selector) {
        *selector_register = (*selector_register & ~7U) | selector;
        started = tick_read();
        while ((*selector_register & 7U) != selector) {
            if ((uint32_t)(tick_read() - started) > selector_timeout) return 3;
        }
    }
    if ((configuration[0] & 2U) != 0U) {
        if ((configuration[0] & 4U) != 0U) clock_registers[2] |= 0x7000U;
        clock_registers[2] = (clock_registers[2] & UINT32_C(0xFFFFF0FF)) |
                             configuration[2];
    }
    if ((configuration[0] & 1U) != 0U) {
        mode = configuration[1];
        if (mode > 4U) return 1;
        clock_registers[2] = (clock_registers[2] & ~7U) | mode;
        clock_registers[2] = (clock_registers[2] & ~0x38U) | (mode << 3U);
    }
    if ((configuration[0] & 4U) != 0U)
        clock_registers[2] = (clock_registers[2] & UINT32_C(0xFFFF8FFF)) |
                             configuration[3];
    clock = open_cfw_case_derive_clock((const uint32_t *)clock_registers,
                                       base_clock);
    shift_index = (clock_registers[2] >> 6U) & 0x3CU;
    if (shift_table != NULL && shift_index < shift_table_length)
        clock >>= shift_table[shift_index] & 0x1FU;
    *derived_clock = clock;
    return initialize_interrupt == NULL ? 0 : initialize_interrupt(selector);
}


uint64_t open_cfw_case_calibrate_controller(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t status_mask, uint32_t spin_limit,
    open_cfw_case_resource_status_fn start,
    open_cfw_case_resource_status_fn status,
    open_cfw_case_resource_value_read_fn sample,
    open_cfw_case_tick_read_fn tick_read)
{
    uint32_t saved_status;
    uint32_t spin_count = 0U;
    uint32_t sum = 0U;
    uint32_t index;
    uint32_t started;
    int start_status;
    if (context == NULL || controller == NULL || start == NULL ||
        status == NULL || sample == NULL || tick_read == NULL) return 1U;
    if (context[0x54U] == 1U) return 2U;
    context[0x54U] = 1U;
    start_status = start(context);
    if (status((void *)controller) == 0) {
        store_le32(context + 0x58U,
                   (load_le32(context + 0x58U) & ~0x100U) | 2U);
        saved_status = controller[3] & status_mask;
        controller[3] &= ~status_mask;
        for (index = 0U; index < 8U; ++index) {
            controller[2] = (controller[2] & UINT32_C(0xFFFFFFE8)) |
                            UINT32_C(0x80000000);
            while ((controller[2] & UINT32_C(0x80000000)) != 0U) {
                ++spin_count;
                controller[2] &= ~UINT32_C(0x80000000);
                if (spin_count >= spin_limit) {
                    store_le32(context + 0x58U,
                               (load_le32(context + 0x58U) & ~2U) | 0x10U);
                    context[0x54U] = 0U;
                    return ((uint64_t)spin_count << 32U) | 1U;
                }
            }
            sum += sample((void *)controller) & 0x7FU;
        }
        controller[2] = (controller[2] & UINT32_C(0xFFFFFFE8)) + 1U;
        controller[45] = (controller[45] & UINT32_C(0xFFFFFF80)) |
                         ((sum / 8U) & 0x7FU);
        controller[2] = (controller[2] & UINT32_C(0xFFFFFFE8)) + 2U;
        started = tick_read();
        while (status((void *)controller) != 0) {
            if ((uint32_t)(tick_read() - started) > 2U) {
                store_le32(context + 0x58U,
                           load_le32(context + 0x58U) | 0x10U);
                store_le32(context + 0x5CU,
                           load_le32(context + 0x5CU) | 1U);
                return ((uint64_t)spin_count << 32U) | 1U;
            }
        }
        controller[3] |= saved_status;
        store_le32(context + 0x58U,
                   (load_le32(context + 0x58U) & ~3U) + 1U);
    } else {
        store_le32(context + 0x58U,
                   load_le32(context + 0x58U) | 0x10U);
    }
    context[0x54U] = 0U;
    return ((uint64_t)spin_count << 32U) | (uint32_t)start_status;
}


int open_cfw_case_boot_initialize(
    const open_cfw_case_init_entry *begin,
    const open_cfw_case_init_entry *end,
    const uint8_t *packed_begin, const uint8_t *packed_end,
    uint8_t *destination, uint8_t *destination_end,
    open_cfw_case_void_action_fn failure)
{
    const open_cfw_case_init_entry *entry;
    const uint8_t *source = packed_begin;
    uint8_t *output = destination;
    if (begin == NULL || end == NULL || packed_begin == NULL ||
        packed_end == NULL || destination == NULL || destination_end == NULL)
        return 1;
    for (entry = begin; entry < end; ++entry) {
        if (entry->initialize != NULL)
            entry->initialize(entry->first, entry->second, entry->third);
    }
    while (source < packed_end && output < destination_end) {
        uint32_t literal = *source & 0xFU;
        uint32_t zero = *source >> 4U;
        ++source;
        if (literal == 0U) {
            if (source >= packed_end) break;
            literal = *source++;
        }
        if (zero == 0U) {
            if (source >= packed_end) break;
            zero = *source++;
        }
        while (literal-- > 1U && source < packed_end &&
               output < destination_end) *output++ = *source++;
        while (zero-- > 1U && output < destination_end) *output++ = 0U;
    }
    if (output != destination_end) {
        if (failure != NULL) failure();
        return 1;
    }
    return 0;
}


static int wire_ops_ready(const open_cfw_case_wire_ops *ops)
{
    return ops != NULL && ops->sequence_start != NULL &&
        ops->frame_stop != NULL && ops->emit != NULL &&
        ops->route != NULL && ops->check != NULL && ops->parity != NULL;
}


static int wire_check(uint32_t value, uint32_t *observed,
                      const open_cfw_case_wire_ops *ops)
{
    if (ops->check(observed) == 0) return 0;
    return open_cfw_case_parity8(value) == *observed;
}


int open_cfw_case_wire_read_register(
    uint32_t address, uint32_t selector, uint8_t *output,
    uint32_t length, uint32_t *error,
    const open_cfw_case_wire_ops *ops)
{
    uint32_t observed = 0U;
    uint32_t index;
    uint32_t bus_address;
    if (error != NULL) *error = 0U;
    if ((address & 0x40U) == 0U || output == NULL || !wire_ops_ready(ops) ||
        ops->collect == NULL) {
        if (error != NULL) *error = 0x29U;
        return 0;
    }
    bus_address = ((address & ~0xFU) + selector) & 0xFFU;
    ops->sequence_start();
    ops->frame_stop();
    ops->emit(bus_address, 1);
    ops->route(1);
    if (!wire_check((bus_address * 2U + 1U) & 0xFFU, &observed, ops)) {
        ops->frame_stop();
        if (error != NULL) *error = observed == 0U ? 0x2AU : 0x2BU;
        return 0;
    }
    for (index = 0U; index < length; ++index) {
        if (ops->collect(output + index) == 0) {
            ops->frame_stop();
            if (error != NULL) *error = 0x2CU;
            return 0;
        }
        if (index + 1U < length) ops->route(output[index]);
    }
    ops->frame_stop();
    return 1;
}


uint64_t open_cfw_case_wire_write_register(
    uint32_t address, uint32_t selector, const uint8_t *input,
    uint32_t length, uint32_t *error,
    const open_cfw_case_wire_ops *ops)
{
    uint32_t observed = 0U;
    uint32_t index;
    uint32_t bus_address;
    if (error != NULL) *error = 0U;
    if ((address & 0x40U) == 0U || input == NULL || !wire_ops_ready(ops)) {
        if (error != NULL) *error = 0x15U;
        return UINT64_C(1) << 32U;
    }
    bus_address = (address & ~0xFU) + selector;
    ops->sequence_start();
    ops->frame_stop();
    ops->emit(bus_address & 0xFFU, 1);
    ops->route(0);
    if (!wire_check((bus_address & 0x7FU) << 1U, &observed, ops)) {
        ops->frame_stop();
        if (error != NULL) *error = observed == 0U ? 0x16U : 0x17U;
        return UINT64_C(1) << 32U;
    }
    for (index = 0U; index < length; ++index) {
        ops->emit(input[index], 0);
        if (!wire_check(input[index], &observed, ops)) {
            ops->frame_stop();
            if (error != NULL) *error = observed == 0U ? 0x18U : 0x19U;
            return UINT64_C(1) << 32U;
        }
    }
    ops->frame_stop();
    return (UINT64_C(1) << 32U) | 1U;
}


int open_cfw_case_wire_exchange_register(
    uint32_t address, uint8_t value,
    uint8_t *output, uint32_t length, uint32_t *error,
    const open_cfw_case_wire_ops *ops)
{
    uint32_t observed = 0U;
    uint32_t index;
    if (error != NULL) *error = 0U;
    if ((address & 0x40U) != 0U || output == NULL || !wire_ops_ready(ops) ||
        ops->collect == NULL) {
        if (error != NULL) *error = 0x1FU;
        return 0;
    }
    ops->sequence_start();
    ops->frame_stop();
    ops->emit(address & 0xFFU, 1);
    ops->route(0);
    if (!wire_check((address * 2U) & 0xFFU, &observed, ops)) {
        if (error != NULL) *error = observed == 0U ? 0x20U : 0x21U;
        goto failed;
    }
    ops->emit(value, 0);
    if (!wire_check(value, &observed, ops)) {
        if (error != NULL) *error = observed == 0U ? 0x22U : 0x23U;
        goto failed;
    }
    ops->frame_stop();
    ops->emit(address & 0xFFU, 1);
    ops->route(1);
    if (!wire_check((address * 2U + 1U) & 0xFFU, &observed, ops)) {
        if (error != NULL) *error = observed == 0U ? 0x24U : 0x25U;
        goto failed;
    }
    for (index = 0U; index < length; ++index) {
        if (ops->collect(output + index) == 0) {
            if (error != NULL) *error = 0x26U;
            goto failed;
        }
        if (index + 1U < length) ops->route(output[index]);
    }
    ops->frame_stop();
    return 1;
failed:
    ops->frame_stop();
    return 0;
}


static void reset_frame(open_cfw_case_frame_parser *parser)
{
    parser->length = 0U;
    parser->current = 0U;
}


void open_cfw_case_process_frame_byte(
    open_cfw_case_frame_parser *parser, uint8_t value,
    open_cfw_case_frame_validate_fn validate,
    open_cfw_case_frame_read_fn read,
    open_cfw_case_status_action_fn start_transfer,
    open_cfw_case_mask_action_fn notify)
{
    uint32_t expected = 0U;
    int complete = 0;
    if (parser == NULL) return;
    parser->current = value;
    if (parser->length == 0U && value != 'Z' && value != 'D' && value != 'd')
        goto start_next;
    if (parser->length < sizeof(parser->data))
        parser->data[parser->length++] = value;
    if (value == '\n' && validate != NULL &&
        validate(parser->data, parser->length) != 0) complete = 1;
    if (parser->data[0] != 'Z') {
        if ((parser->length >= 2U && validate != NULL &&
             validate(parser->data, parser->length) != 0) ||
            parser->length >= 61U) complete = 1;
    } else if (parser->length >= 2U) {
        if (parser->data[1] != 0xA5U) complete = 1;
        else if (parser->length >= 3U && parser->data[2] == 0x7FU) {
            if (parser->length >= 4U) expected = (uint32_t)parser->data[3] + 5U;
        } else if (parser->length >= 3U && parser->data[2] == 0xCFU) {
            if (parser->length >= 5U) {
                uint32_t payload = parser->data[3] |
                                   ((uint32_t)parser->data[4] << 8U);
                expected = payload + 6U;
                if (parser->length == 5U && read != NULL &&
                    payload <= sizeof(parser->data) - parser->length &&
                    read(parser->data + parser->length, payload, 20U) != 3)
                    parser->length = (uint16_t)(parser->length + payload);
            }
        } else if (parser->length >= 3U) {
            complete = 1;
        }
        if (expected != 0U && parser->length == expected) complete = 1;
    }
    if (complete) {
        if (notify != NULL) notify(8U);
        reset_frame(parser);
    } else if (parser->length == sizeof(parser->data)) {
        reset_frame(parser);
    }
start_next:
    if (start_transfer != NULL && start_transfer() != 0 && notify != NULL)
        notify(0x40U);
}


void open_cfw_case_emit_probe_train(
    uintptr_t resource, uint32_t mask, uint32_t long_delay,
    open_cfw_case_mask_write_fn write,
    open_cfw_case_counted_delay_fn delay,
    open_cfw_case_counted_delay_fn short_delay)
{
    uint32_t index;
    uint32_t half_period = (uint32_t)(resource >> 19U);
    if (write == NULL || delay == NULL || short_delay == NULL) return;
    write(UINT32_C(0x50000000), 8U, 1U);
    short_delay(10);
    write(resource, mask, 1U);
    short_delay(10);
    write(resource, mask, 0U);
    delay(0x26C);
    write(resource, mask, 1U);
    delay((int32_t)long_delay);
    for (index = 0U; index < 5U; ++index) {
        write(resource, mask, 0U); delay((int32_t)half_period);
        write(resource, mask, 1U); delay((int32_t)half_period);
    }
    write(resource, mask, 1U); delay((int32_t)long_delay);
    write(resource, mask, 0U); short_delay(0x28);
    write(resource, mask, 1U); short_delay(1);
    for (index = 0U; index < 2U; ++index) {
        uint32_t pulses;
        write(resource, mask, 0U); delay(0x26C);
        write(resource, mask, 1U); delay((int32_t)long_delay);
        for (pulses = 0U; pulses < 7U; ++pulses) {
            write(resource, mask, 0U); delay((int32_t)half_period);
            write(resource, mask, 1U); delay((int32_t)half_period);
        }
        write(resource, mask, 1U); delay((int32_t)long_delay);
        if (index == 0U) short_delay(1);
    }
}


static void drain_receive(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    uint32_t width, uint16_t fifo_threshold, uint32_t reload_descriptor,
    open_cfw_case_resource_action_fn error,
    open_cfw_case_resource_action_fn service,
    open_cfw_case_context_short_fn finalize)
{
    uint16_t remaining;
    uint16_t mask;
    if (context == NULL || controller == NULL || cursor == NULL ||
        *cursor == NULL) return;
    if (load_le32(context + 0x8CU) != 0x22U) {
        controller[6] |= 8U;
        return;
    }
    remaining = (uint16_t)(context[0x5EU] |
                           ((uint16_t)context[0x5FU] << 8U));
    mask = (uint16_t)(context[0x60U] |
                      ((uint16_t)context[0x61U] << 8U));
    while (remaining != 0U && (controller[7] & (1U << 5U)) != 0U) {
        uint32_t value = controller[9] & mask;
        (*cursor)[0] = (uint8_t)value;
        if (width == 2U) (*cursor)[1] = (uint8_t)(value >> 8U);
        *cursor += width;
        --remaining;
        context[0x5EU] = (uint8_t)remaining;
        context[0x5FU] = (uint8_t)(remaining >> 8U);
        if ((controller[7] & 7U) != 0U) {
            uint32_t flags = 0U;
            if ((controller[7] & 1U) != 0U &&
                (controller[0] & (1U << 8U)) != 0U) flags |= 1U;
            if ((controller[7] & 2U) != 0U && (controller[2] & 1U) != 0U)
                flags |= 4U;
            if ((controller[7] & 4U) != 0U && (controller[2] & 1U) != 0U)
                flags |= 2U;
            if (flags != 0U) {
                store_le32(context + 0x90U,
                           load_le32(context + 0x90U) | flags);
                if (error != NULL) error(context);
                store_le32(context + 0x90U, 0U);
            }
        }
        if (remaining == 0U) {
            controller[0] &= UINT32_C(0xFFFFFEFF);
            controller[2] &= UINT32_C(0xEFFFFFFE);
            store_le32(context + 0x8CU, 0x20U);
            store_le32(context + 0x74U, 0U);
            store_le32(context + 0x70U, 0U);
            if (load_le32(context + 0x6CU) == 1U) {
                store_le32(context + 0x6CU, 0U);
                controller[0] &= UINT32_C(0xFFFFFFEF);
                if (finalize != NULL)
                    finalize(context, (int16_t)(context[0x5CU] |
                             ((uint16_t)context[0x5DU] << 8U)));
            } else if (service != NULL) service(context);
        }
    }
    if (remaining != 0U && remaining < fifo_threshold) {
        controller[2] &= UINT32_C(0xEFFFFFFF);
        store_le32(context + 0x74U, reload_descriptor);
        controller[0] |= 0x20U;
    }
}


void open_cfw_case_drain_receive_u16(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    uint16_t fifo_threshold, uint32_t reload_descriptor,
    open_cfw_case_resource_action_fn error,
    open_cfw_case_resource_action_fn service,
    open_cfw_case_context_short_fn finalize)
{
    drain_receive(context, controller, cursor, 2U, fifo_threshold,
                  reload_descriptor, error, service, finalize);
}


void open_cfw_case_drain_receive_u8(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    uint16_t fifo_threshold, uint32_t reload_descriptor,
    open_cfw_case_resource_action_fn error,
    open_cfw_case_resource_action_fn service,
    open_cfw_case_context_short_fn finalize)
{
    drain_receive(context, controller, cursor, 1U, fifo_threshold,
                  reload_descriptor, error, service, finalize);
}


static uint32_t pin_encoded_value(uint32_t value)
{
    uint32_t bit;
    uint32_t low = value & 0x7FFFFU;
    if (low == 0U) return (value & UINT32_C(0x7FFFFFFF)) >> 26U;
    if ((low & 1U) != 0U) return 0U;
    for (bit = 1U; bit <= 18U; ++bit) {
        if ((low & (1U << bit)) != 0U) return bit;
    }
    return 0U;
}


int open_cfw_case_configure_pin_policy(
    uint8_t *context, volatile uint32_t *controller,
    const uint32_t descriptor[3], volatile uint32_t *clock_control,
    uint32_t clock_mask, uint32_t special_a, uint32_t special_b,
    uint32_t special_c, open_cfw_case_resource_status_fn clear_error,
    open_cfw_case_counted_delay_fn delay)
{
    uint32_t value;
    uint32_t shift;
    uint32_t encoded;
    if (context == NULL || controller == NULL || descriptor == NULL)
        return 1;
    if (context[0x54U] == 1U) return 2;
    context[0x54U] = 1U;
    if (clear_error != NULL && clear_error((void *)controller) != 0) {
        store_le32(context + 0x58U,
                   load_le32(context + 0x58U) | 0x20U);
        context[0x54U] = 0U;
        return 1;
    }
    value = descriptor[0];
    if (descriptor[1] == 2U) {
        if (load_le32(context + 16U) == UINT32_C(0x80000000) ||
            load_le32(context + 16U) == UINT32_C(0x80000004))
            controller[10] &= ~(value & 0x7FFFFU);
        if ((value & UINT32_C(0x80000000)) != 0U && clock_control != NULL) {
            if (value == special_a) *clock_control &= ~(clock_mask << 11U);
            else if (value == special_b) *clock_control &= ~(clock_mask << 10U);
            else if (value == special_c) *clock_control &= ~(clock_mask << 9U);
        }
    } else {
        if (load_le32(context + 16U) == UINT32_C(0x80000000) ||
            load_le32(context + 16U) == UINT32_C(0x80000004)) {
            controller[10] |= value & 0x7FFFFU;
        } else {
            shift = descriptor[1] & 0x1FU;
            encoded = pin_encoded_value(value);
            store_le32(context + 0x60U,
                       (load_le32(context + 0x60U) & ~(0xFU << shift)) |
                       (encoded << shift));
            if ((descriptor[1] >> 2U) + 1U <= load_le32(context + 28U))
                controller[10] = (controller[10] & ~(0xFU << shift)) |
                    (((value & UINT32_C(0x3FFFFFFF)) >> 26U) << shift);
        }
        controller[5] = (controller[5] & ~(value << 8U)) |
            ((value << 8U) & descriptor[2] & 0x7FFFFFFU);
        if ((value & UINT32_C(0x80000000)) != 0U && clock_control != NULL) {
            uint32_t prior = *clock_control & clock_mask;
            if (value == special_a && (prior & (1U << 23U)) == 0U) {
                *clock_control = prior | (value << 11U);
                if (delay != NULL) delay(12);
            } else if (value == special_b && (prior & (1U << 24U)) == 0U) {
                *clock_control = prior | (value << 10U);
            } else if (value == special_c && (prior & (1U << 22U)) == 0U) {
                *clock_control = prior | (value << 9U);
            }
        }
    }
    context[0x54U] = 0U;
    return 0;
}


static int wait_register_bit(
    volatile uint32_t *value, uint32_t mask, int set, uint32_t timeout,
    open_cfw_case_tick_read_fn tick_read)
{
    uint32_t started = tick_read();
    while (((*value & mask) != 0U) != (set != 0)) {
        if ((uint32_t)(tick_read() - started) > timeout) return 3;
    }
    return 0;
}


int open_cfw_case_configure_system_clock(
    const uint32_t configuration[14], volatile uint32_t clock[16],
    volatile uint32_t auxiliary[9], volatile uint32_t *oscillator,
    uint32_t timeout, open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_selector_status_fn initialize_interrupt)
{
    uint32_t flags;
    uint32_t mode;
    uint32_t fields;
    int status;
    if (configuration == NULL || clock == NULL || auxiliary == NULL ||
        oscillator == NULL || tick_read == NULL) return 1;
    flags = configuration[0];
    if ((flags & 1U) != 0U) {
        mode = configuration[1];
        if (mode != 0U && mode != 1U && mode != 5U) return 1;
        clock[0] &= ~(0x50000U);
        if (mode == 1U) clock[0] |= 0x10000U;
        else if (mode == 5U) clock[0] |= 0x50000U;
        if (mode == 0U) {
            status = wait_register_bit(clock, 1U << 17U, 0, 100U, tick_read);
            if (status != 0) return status;
        }
    }
    if ((flags & 2U) != 0U) {
        mode = configuration[3];
        if (mode == 0U) {
            clock[0] &= ~0x100U;
            status = wait_register_bit(clock, 1U << 10U, 0, 2U, tick_read);
        } else {
            clock[0] = (clock[0] & UINT32_C(0xFFFFC7FF)) |
                       configuration[4] | 0x100U;
            status = wait_register_bit(clock, 1U << 10U, 1, 2U, tick_read);
            if (status == 0)
                clock[1] = (clock[1] & UINT32_C(0xFFFF80FF)) |
                           (configuration[5] << 8U);
        }
        if (status != 0) return status;
    }
    if ((flags & 4U) != 0U && ((clock[2] & 0x3FU) >> 3U) != 3U) {
        if (configuration[6] == 0U) auxiliary[8] &= ~1U;
        else auxiliary[8] |= 1U;
        status = wait_register_bit(auxiliary + 8U, 2U,
                                   configuration[6] != 0U, 2U, tick_read);
        if (status != 0) return status;
    }
    if ((flags & 8U) != 0U) {
        if (((clock[2] & 0x3FU) >> 3U) == 4U &&
            (auxiliary[7] & 2U) != 0U && configuration[8] == 0U) return 1;
        clock[15] |= UINT32_C(0x10000000);
        if ((*oscillator & (1U << 8U)) == 0U) *oscillator |= 1U << 9U;
        if (configuration[8] == 1U) auxiliary[7] |= 1U;
        else if (configuration[8] == 5U) auxiliary[7] |= 5U;
        else auxiliary[7] &= ~5U;
        status = wait_register_bit(auxiliary + 7U, 2U,
                                   configuration[8] != 0U, timeout, tick_read);
        clock[15] &= UINT32_C(0xEFFFFFFF);
        if (status != 0) return status;
    }
    mode = configuration[7];
    if (mode == 0U) return 0;
    if (((clock[2] & 0x3FU) >> 3U) == 2U) {
        if (mode == 1U) return 1;
        fields = configuration[8] | configuration[9] |
                 (configuration[10] << 8U) | configuration[11] |
                 configuration[12] | configuration[13];
        if ((clock[3] & (3U | 0x70U | 0x7F00U | 0x3E0000U |
                         0xE000000U | 0xE0000000U)) == fields)
            return 0;
        return 1;
    }
    clock[0] &= UINT32_C(0xFEFFFFFF);
    status = wait_register_bit(clock, 1U << 25U, 0, 3U, tick_read);
    if (status != 0) return status;
    if (mode == 2U) {
        clock[3] = configuration[8] | configuration[9] |
                   (configuration[10] << 8U) | configuration[11] |
                   configuration[12] | configuration[13];
        clock[0] |= UINT32_C(0x01000000);
        clock[3] |= UINT32_C(0x10000000);
        status = wait_register_bit(clock, 1U << 25U, 1, 3U, tick_read);
        if (status != 0) return status;
    } else {
        clock[3] = 0U;
    }
    return initialize_interrupt == NULL ? 0 : initialize_interrupt(mode);
}
