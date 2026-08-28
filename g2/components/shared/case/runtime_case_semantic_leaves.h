/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_CASE_SEMANTIC_LEAVES_H
#define OPEN_CFW_RUNTIME_CASE_SEMANTIC_LEAVES_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Behaviorally empty callback/reserved-hook candidates, named by entry address. */
#define OPEN_CFW_CASE_NOOP_HOOKS(X) \
    X(080040f8) X(080040fa) X(080040fc) X(080040fe) \
    X(08004324) X(08004326) X(080046a0) X(08004d00) \
    X(08004d2c) X(08005a50) X(08005bd4) X(08005bd6) \
    X(08005bd8) X(08005c26) X(08005c8c) X(08005e14) \
    X(08005e16) X(08005e2c) X(08006776) X(08006e18)

#define OPEN_CFW_CASE_DECLARE_NOOP(address) \
    void open_cfw_case_hook_##address(void);
OPEN_CFW_CASE_NOOP_HOOKS(OPEN_CFW_CASE_DECLARE_NOOP)
#undef OPEN_CFW_CASE_DECLARE_NOOP

uint8_t open_cfw_case_read_byte3(const uint8_t *record);
void open_cfw_case_add_byte0_to_word8(uint8_t *record);
uint32_t open_cfw_case_or_words_88_8c(const uint8_t *context);
void open_cfw_case_copy_head8_to_tail8(uint8_t storage[16]);

void open_cfw_case_delay_10(void);
void open_cfw_case_busy_delay(int32_t iterations);
void open_cfw_case_busy_delay_alt(int32_t iterations);
uint32_t open_cfw_case_parity8(uint32_t value);
uint32_t open_cfw_case_parity8_alt(uint32_t value);

typedef void (*open_cfw_case_void_action_fn)(void);
typedef void (*open_cfw_case_command_fn)(uint32_t command, uint32_t value);
typedef int (*open_cfw_case_mode_action_fn)(uint32_t first, uint32_t second,
                                            uint32_t mode);
typedef int (*open_cfw_case_byte_action_fn)(uint32_t selector, uint8_t value);
typedef void (*open_cfw_case_word_transform_fn)(uint32_t *value);
typedef void (*open_cfw_case_dispatch_fn)(uintptr_t resource, uint32_t first,
                                          uint32_t second, uint32_t third);
typedef void (*open_cfw_case_bool_action_fn)(int enabled);
typedef void (*open_cfw_case_notify_fn)(void *record);
typedef void (*open_cfw_case_index_write_fn)(uint32_t index, uint32_t value);
typedef uint32_t (*open_cfw_case_mask_read_fn)(uintptr_t resource,
                                               uint32_t mask);
typedef void (*open_cfw_case_mask_write_fn)(uintptr_t resource,
                                            uint32_t mask, uint32_t value);
typedef void (*open_cfw_case_resource_action_fn)(void *resource);
typedef int (*open_cfw_case_fill_status_fn)(uint8_t record[28]);
typedef int (*open_cfw_case_query_word_fn)(uint32_t *value);
typedef void (*open_cfw_case_cursor_fn)(uint32_t argument, uint32_t cursor);
typedef int (*open_cfw_case_query_command_fn)(uint32_t command,
                                              uint32_t *value,
                                              uint32_t mode);
typedef void (*open_cfw_case_mask_action_fn)(uint32_t mask);
typedef uint32_t (*open_cfw_case_tick_read_fn)(void);
typedef int (*open_cfw_case_bit_read_fn)(int *value);
typedef int (*open_cfw_case_byte_update_fn)(uint32_t index, uint32_t mode,
                                            uint32_t *value,
                                            uint32_t argument,
                                            uint32_t repeated_index);
typedef int (*open_cfw_case_resource_status_fn)(void *resource);
typedef int (*open_cfw_case_selector_status_fn)(uint32_t selector);
typedef int (*open_cfw_case_status_action_fn)(void);
typedef void (*open_cfw_case_record_config_fn)(uintptr_t resource,
                                               const uint32_t record[5]);
typedef void (*open_cfw_case_context_dispatch_fn)(void *context,
                                                  uint32_t first,
                                                  uint32_t second);
typedef uint32_t (*open_cfw_case_divide_fn)(uint32_t numerator,
                                            uint32_t denominator);
typedef void (*open_cfw_case_register_write_fn)(uint32_t index,
                                                uint32_t value);
typedef void (*open_cfw_case_context_config_fn)(void *resource,
                                                uint8_t *configuration);
typedef uint32_t (*open_cfw_case_value_read_fn)(void);
typedef void (*open_cfw_case_value_write_fn)(uint32_t value);
typedef int (*open_cfw_case_selector_read_fn)(uint32_t selector,
                                              uint32_t *value);
typedef int (*open_cfw_case_resource_read_fn)(uintptr_t resource,
                                              uint32_t *value,
                                              uint32_t length);
typedef int (*open_cfw_case_context_value_status_fn)(void *context,
                                                     uint32_t value);
typedef int (*open_cfw_case_context_pair_status_fn)(void *context,
                                                    uint32_t first,
                                                    uint32_t second);
typedef int (*open_cfw_case_context_transfer_status_fn)(void *context,
                                                        uint32_t option,
                                                        int enabled);
typedef int (*open_cfw_case_context_descriptor_status_fn)(
    void *context, const uint32_t descriptor[3]);
typedef int (*open_cfw_case_record_status_fn)(const uint32_t *record,
                                              uint32_t words);
typedef int (*open_cfw_case_context_mask_status_fn)(void *context,
                                                    uint32_t mask,
                                                    uint32_t started,
                                                    uint32_t budget);
typedef void (*open_cfw_case_counted_delay_fn)(int32_t iterations);
typedef void (*open_cfw_case_line_write_fn)(int enabled);
typedef int (*open_cfw_case_line_read_fn)(void);
typedef uint32_t (*open_cfw_case_resource_value_read_fn)(void *resource);
typedef void (*open_cfw_case_irq_restore_fn)(int enabled);
typedef void (*open_cfw_case_pair_action_fn)(uint32_t first,
                                             uint32_t second);
typedef void (*open_cfw_case_copy_action_fn)(uint32_t *destination,
                                             const uint32_t *source);
typedef int (*open_cfw_case_byte_read_fn)(uint32_t selector,
                                          uint8_t *value);
typedef void (*open_cfw_case_waiter_unblock_fn)(void *waiter,
                                                uint32_t value);
typedef void (*open_cfw_case_context_short_fn)(void *context,
                                               int16_t value);

typedef struct open_cfw_case_event_waiter {
    uint32_t event_item_value;
    struct open_cfw_case_event_waiter *next;
} open_cfw_case_event_waiter;

typedef struct {
    uint32_t bits;
    open_cfw_case_event_waiter *waiters;
} open_cfw_case_event_group;

typedef struct {
    uint32_t ownership[8];
    uint32_t active[4];
} open_cfw_case_pin_state;

typedef int (*open_cfw_case_wait_condition_fn)(
    uint8_t *context, volatile uint32_t *controller, uint32_t mask,
    int expected, uint32_t started, uint32_t timeout);
typedef void (*open_cfw_case_emit_word_fn)(uint32_t value, int seven_bits);
typedef int (*open_cfw_case_check_word_fn)(uint32_t *value);
typedef int (*open_cfw_case_collect_byte_fn)(uint8_t *value);
typedef int (*open_cfw_case_frame_validate_fn)(const uint8_t *data,
                                               uint32_t length);
typedef int (*open_cfw_case_frame_read_fn)(uint8_t *output, uint32_t length,
                                           uint32_t timeout);

typedef struct {
    open_cfw_case_void_action_fn sequence_start;
    open_cfw_case_void_action_fn frame_stop;
    open_cfw_case_emit_word_fn emit;
    open_cfw_case_bool_action_fn route;
    open_cfw_case_check_word_fn check;
    open_cfw_case_value_read_fn parity;
    open_cfw_case_collect_byte_fn collect;
} open_cfw_case_wire_ops;

typedef struct {
    uint8_t data[1200];
    uint16_t length;
    uint8_t current;
} open_cfw_case_frame_parser;

typedef void (*open_cfw_case_init_entry_fn)(uint32_t first,
                                            uint32_t second,
                                            uint32_t third);
typedef struct {
    uint32_t first;
    uint32_t second;
    uint32_t third;
    open_cfw_case_init_entry_fn initialize;
} open_cfw_case_init_entry;

typedef struct {
    open_cfw_case_void_action_fn mask4_set;
    open_cfw_case_void_action_fn mask4_clear;
    open_cfw_case_void_action_fn mask8_set;
    open_cfw_case_void_action_fn mask8_clear;
    open_cfw_case_void_action_fn word4_primary;
    open_cfw_case_void_action_fn word4_alternate;
    open_cfw_case_counted_delay_fn delay;
} open_cfw_case_pulse_ops;

typedef struct {
    open_cfw_case_line_write_fn clock;
    open_cfw_case_line_write_fn data;
    open_cfw_case_line_read_fn sample;
    open_cfw_case_void_action_fn delay;
} open_cfw_case_serial_line_ops;

typedef struct {
    open_cfw_case_void_action_fn word8_set;
    open_cfw_case_void_action_fn mask4_set;
    open_cfw_case_void_action_fn word4_set;
    open_cfw_case_void_action_fn mask4_clear;
    open_cfw_case_void_action_fn word4_clear;
    open_cfw_case_counted_delay_fn delay;
    open_cfw_case_value_read_fn read;
} open_cfw_case_probe_ops;

typedef struct {
    open_cfw_case_resource_action_fn reset;
    open_cfw_case_status_action_fn prepare;
    open_cfw_case_context_value_status_fn field_high;
    open_cfw_case_context_value_status_fn field_mid;
    open_cfw_case_resource_status_fn disable;
    open_cfw_case_context_transfer_status_fn transfer;
    open_cfw_case_void_action_fn failure;
} open_cfw_case_controller_init_ops;

typedef struct {
    open_cfw_case_void_action_fn start;
    open_cfw_case_value_write_fn write;
    open_cfw_case_status_action_fn acknowledge;
    open_cfw_case_value_read_fn read;
    open_cfw_case_void_action_fn acknowledge_more;
    open_cfw_case_void_action_fn acknowledge_last;
    open_cfw_case_void_action_fn stop;
} open_cfw_case_serial_bus_ops;

void open_cfw_case_forward_action(open_cfw_case_void_action_fn action);
void open_cfw_case_command_a2_clear(open_cfw_case_command_fn command);
void open_cfw_case_command_a2_set(open_cfw_case_command_fn command);
void open_cfw_case_run_pair(open_cfw_case_void_action_fn first,
                            open_cfw_case_void_action_fn second);
int open_cfw_case_invoke_mode_one(open_cfw_case_mode_action_fn action,
                                  uint32_t first, uint32_t second);
int open_cfw_case_invoke_byte(open_cfw_case_byte_action_fn action,
                              uint32_t selector, const uint8_t *value);
void open_cfw_case_transform_word(uint32_t *output, uint32_t value,
                                  open_cfw_case_word_transform_fn transform);
void open_cfw_case_transform_word_alt(
    uint32_t *output, uint32_t value,
    open_cfw_case_word_transform_fn transform);
void open_cfw_case_run_if_token(const int32_t *value, int32_t token,
                                open_cfw_case_void_action_fn action);
void open_cfw_case_dispatch_resource(open_cfw_case_dispatch_fn dispatch,
                                     uintptr_t resource, uint32_t first,
                                     uint32_t second);
void open_cfw_case_dispatch_resource4(open_cfw_case_dispatch_fn dispatch,
                                      uintptr_t resource, uint32_t first,
                                      uint32_t second, uint32_t third);
void open_cfw_case_route_boolean(int value,
                                 open_cfw_case_void_action_fn true_action,
                                 open_cfw_case_void_action_fn false_action);
void open_cfw_case_route_boolean_alt(int value,
                                     open_cfw_case_void_action_fn true_action,
                                     open_cfw_case_void_action_fn false_action);
void open_cfw_case_emit_bits(uint32_t value, int seven_bits,
                             open_cfw_case_bool_action_fn emit);
void open_cfw_case_emit_bits_alt(uint32_t value, int seven_bits,
                                 open_cfw_case_bool_action_fn emit);
void open_cfw_case_nested_delay(int32_t outer, int32_t inner);
int open_cfw_case_context_word38_is_zero(const uint8_t *context);
uint32_t open_cfw_case_read_word_protected(
    const uint32_t *value, open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave);
void open_cfw_case_run_guarded(uint8_t state[2],
                               open_cfw_case_void_action_fn action);
void open_cfw_case_transition_word4(uint8_t *record, uint32_t value,
                                    open_cfw_case_notify_fn notify);
void open_cfw_case_transition_word4_alt(uint8_t *record, uint32_t value,
                                        open_cfw_case_notify_fn notify);
void open_cfw_case_transition_word8(uint8_t *record, uint32_t value,
                                    open_cfw_case_notify_fn notify);
void open_cfw_case_transition_word8_alt(uint8_t *record, uint32_t value,
                                        open_cfw_case_notify_fn notify);
void open_cfw_case_write_profile_three(open_cfw_case_index_write_fn write);
void open_cfw_case_write_profile_four(open_cfw_case_index_write_fn write);
uint32_t open_cfw_case_select_mask(const uint8_t *wide_first,
                                   uintptr_t resource,
                                   open_cfw_case_mask_read_fn read);
void open_cfw_case_write_selected_mask(const uint8_t *wide_first,
                                       uintptr_t resource, uint32_t value,
                                       open_cfw_case_mask_write_fn write);
void open_cfw_case_write_selected_mask_alt(
    const uint8_t *wide_first, uintptr_t resource, uint32_t value,
    open_cfw_case_mask_write_fn write);
void open_cfw_case_forward_resource(void *resource,
                                    open_cfw_case_resource_action_fn action);
int open_cfw_case_run_guarded_status(uint8_t state[2],
                                     open_cfw_case_void_action_fn action);
void open_cfw_case_read_mask4(uintptr_t resource,
                              open_cfw_case_mask_read_fn read);
void open_cfw_case_read_mask8(uintptr_t resource,
                              open_cfw_case_mask_read_fn read);
void open_cfw_case_write_mask4_set(uintptr_t resource,
                                   open_cfw_case_mask_write_fn write);
void open_cfw_case_write_mask4_clear(uintptr_t resource,
                                     open_cfw_case_mask_write_fn write);
void open_cfw_case_write_mask8_set(uintptr_t resource,
                                   open_cfw_case_mask_write_fn write);
void open_cfw_case_write_mask8_clear(uintptr_t resource,
                                     open_cfw_case_mask_write_fn write);
void open_cfw_case_dispatch_tagged(open_cfw_case_dispatch_fn dispatch,
                                   uintptr_t resource, uint32_t first,
                                   uint32_t second, uint32_t tag);
void open_cfw_case_route_parity(uint32_t value,
                                open_cfw_case_void_action_fn odd_action,
                                open_cfw_case_void_action_fn even_action);
void open_cfw_case_route_parity_alt(uint32_t value,
                                    open_cfw_case_void_action_fn odd_action,
                                    open_cfw_case_void_action_fn even_action);
void open_cfw_case_reset_timer_fields(uint8_t *state,
                                      open_cfw_case_void_action_fn action);
int open_cfw_case_expand_runs(const uint8_t *input, uint32_t input_length,
                              uint8_t *output, uint32_t output_length);
uint32_t open_cfw_case_classify_status(open_cfw_case_fill_status_fn fill);
uint32_t open_cfw_case_shift_selected(uint32_t value, uint32_t control,
                                      const uint8_t *shift_table,
                                      uint32_t shift_count);
int open_cfw_case_query_low_byte(uint32_t *output, uint32_t initial,
                                 open_cfw_case_query_word_fn query);
void open_cfw_case_advance_cursor(uint32_t record[17], uint32_t argument,
                                  open_cfw_case_cursor_fn publish);
void open_cfw_case_pulse4_short(const open_cfw_case_pulse_ops *ops);
void open_cfw_case_pulse8_short(const open_cfw_case_pulse_ops *ops);
void open_cfw_case_pulse4_long(const open_cfw_case_pulse_ops *ops);
void open_cfw_case_pulse8_long(const open_cfw_case_pulse_ops *ops);
void open_cfw_case_pulse4_extended(const open_cfw_case_pulse_ops *ops);
void open_cfw_case_pulse8_extended(const open_cfw_case_pulse_ops *ops);
void open_cfw_case_pulse4_train_pre_delay(const open_cfw_case_pulse_ops *ops);
void open_cfw_case_pulse4_train(const open_cfw_case_pulse_ops *ops);
void open_cfw_case_pulse8_double_train(const open_cfw_case_pulse_ops *ops);
void open_cfw_case_serial_preamble(const open_cfw_case_serial_line_ops *ops);
void open_cfw_case_serial_ack(const open_cfw_case_serial_line_ops *ops);
void open_cfw_case_serial_start(const open_cfw_case_serial_line_ops *ops);
void open_cfw_case_serial_stop(const open_cfw_case_serial_line_ops *ops);
uint32_t open_cfw_case_serial_read_byte(
    const open_cfw_case_serial_line_ops *ops);
void open_cfw_case_serial_write_byte(const open_cfw_case_serial_line_ops *ops,
                                     uint32_t value);
int open_cfw_case_query_command_a2_is_one(
    uint32_t initial, open_cfw_case_query_command_fn query);
void open_cfw_case_clear_irq(int32_t index, volatile uint32_t *clear_register,
                             open_cfw_case_void_action_fn data_barrier,
                             open_cfw_case_void_action_fn instruction_barrier);
void open_cfw_case_dispatch_pending(
    volatile uint32_t *first_status, volatile uint32_t *second_status,
    uint32_t mask, open_cfw_case_mask_action_fn first_action,
    open_cfw_case_mask_action_fn second_action);
void open_cfw_case_mark_controller_ready(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_resource_action_fn notify);
void open_cfw_case_wait_elapsed(uint32_t delay, uint32_t compensation,
                                open_cfw_case_tick_read_fn tick_read);
uint32_t open_cfw_case_guarded_controller_disable(
    uint8_t *context, volatile uint32_t *control_register);
int32_t open_cfw_case_start_scheduler(
    int requested, uint32_t exception_number,
    open_cfw_case_void_action_fn start);
int open_cfw_case_serial_ack_sample(
    const open_cfw_case_serial_line_ops *ops);
int open_cfw_case_collect_bits(uint8_t *output, int initial,
                               open_cfw_case_bit_read_fn read_bit);
void open_cfw_case_update_cached_byte(
    uint8_t *cache, uint32_t index, uint32_t value, uint32_t argument,
    open_cfw_case_byte_update_fn update);
int open_cfw_case_guarded_two_stage(
    uint8_t *context, open_cfw_case_resource_status_fn first,
    open_cfw_case_resource_status_fn second);
void open_cfw_case_configure_two_bit_field(
    uint32_t selector, uint32_t value, uint32_t *positive_registers,
    uint8_t *negative_register_block);
int open_cfw_case_retry_selector8(open_cfw_case_selector_status_fn attempt,
                                  open_cfw_case_counted_delay_fn delay);
int open_cfw_case_wait_status_bit5(volatile uint32_t *status_register,
                                   open_cfw_case_tick_read_fn tick_read);
uint32_t open_cfw_case_critical_read_word28(
    const uint8_t *record, open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave,
    open_cfw_case_void_action_fn panic);
int open_cfw_case_critical_read_flag40(
    const uint8_t *record, open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave,
    open_cfw_case_void_action_fn panic);
uint32_t open_cfw_case_atomic_clear_word(
    uint32_t *value, uint32_t mask, open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave,
    open_cfw_case_void_action_fn panic);
int open_cfw_case_guarded_controller_field_high(
    uint8_t *context, volatile uint32_t *controller, uint32_t value,
    open_cfw_case_resource_action_fn apply);
int open_cfw_case_guarded_controller_field_mid(
    uint8_t *context, volatile uint32_t *controller, uint32_t value,
    open_cfw_case_resource_action_fn apply);
int open_cfw_case_start_validated(
    uint32_t initial, open_cfw_case_query_word_fn query,
    open_cfw_case_status_action_fn start,
    open_cfw_case_status_action_fn finalize);
void open_cfw_case_toggle_lines_three(
    open_cfw_case_line_write_fn first, open_cfw_case_line_write_fn second,
    open_cfw_case_counted_delay_fn delay);
void open_cfw_case_configure_record_and_stop(
    uintptr_t resource, open_cfw_case_record_config_fn configure,
    open_cfw_case_void_action_fn stop);
void open_cfw_case_normalize_context(
    uint8_t *context, uint32_t first, uint32_t second,
    open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave,
    open_cfw_case_context_dispatch_fn dispatch,
    open_cfw_case_resource_action_fn finalize);
int open_cfw_case_reset_controller_context(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_resource_action_fn release);
int open_cfw_case_wait_controller_ready(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_tick_read_fn tick_read);
int open_cfw_case_prepare_controller_wait(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_resource_status_fn wait_ready);
int open_cfw_case_configure_mode_wait(
    volatile uint32_t *registers, uint32_t value, uint32_t clock,
    uint32_t divisor, open_cfw_case_divide_fn divide);
void open_cfw_case_configure_register_sequence(
    open_cfw_case_register_write_fn write,
    open_cfw_case_counted_delay_fn delay);
int open_cfw_case_initialize_peripheral_context(
    uint8_t *context, open_cfw_case_resource_action_fn reset,
    open_cfw_case_context_config_fn configure);
int open_cfw_case_enable_peripheral_context(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t mode_mask, int special_controller);
int open_cfw_case_wait_serial_idle(
    volatile uint32_t *registers, volatile uint32_t *error_registers,
    uint32_t timeout, uint32_t status_mask, uint32_t idle_value,
    open_cfw_case_tick_read_fn tick_read);
int open_cfw_case_probe_low_signal(
    uint32_t state[4], uint32_t *observed, uint32_t limit,
    const open_cfw_case_probe_ops *ops);
uint64_t open_cfw_case_probe_high_signal(
    uint32_t state[5], uint32_t *observed, uint32_t limit,
    open_cfw_case_void_action_fn word4_clear,
    open_cfw_case_void_action_fn word8_set,
    open_cfw_case_counted_delay_fn delay,
    open_cfw_case_value_read_fn read);
void open_cfw_case_fail_stop(open_cfw_case_void_action_fn disable,
                             open_cfw_case_void_action_fn idle);
uint32_t open_cfw_case_switch8_offset(uint32_t selector,
                                      const uint8_t *table);
int open_cfw_case_initialize_serial_block(
    volatile uint32_t *control, uint32_t enable_mask,
    open_cfw_case_selector_status_fn initialize,
    open_cfw_case_void_action_fn configure);
int open_cfw_case_serial_write_pair_200(
    uint32_t first, uint32_t second, volatile uint8_t *state,
    open_cfw_case_void_action_fn start,
    open_cfw_case_value_write_fn write,
    open_cfw_case_status_action_fn acknowledge,
    open_cfw_case_void_action_fn stop);
int open_cfw_case_serial_write_pair_70(
    uint32_t first, uint32_t second, volatile uint8_t *state,
    open_cfw_case_void_action_fn start,
    open_cfw_case_value_write_fn write,
    open_cfw_case_status_action_fn acknowledge,
    open_cfw_case_void_action_fn stop);
int open_cfw_case_start_context_transfer(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t option, int enabled,
    open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave,
    open_cfw_case_resource_status_fn transfer);
void open_cfw_case_reset_context_transfer(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t controller2_mask,
    open_cfw_case_void_action_fn enter,
    open_cfw_case_void_action_fn leave);
int open_cfw_case_verify_selector_bank(
    const uint8_t expected[80], open_cfw_case_selector_read_fn read);
int open_cfw_case_read_stable_u16(
    uintptr_t resource, int32_t *value,
    open_cfw_case_resource_read_fn read,
    open_cfw_case_counted_delay_fn delay);
void open_cfw_case_build_register_descriptor(
    uint32_t descriptor[7], const volatile uint32_t *registers,
    uint32_t fixed_value, open_cfw_case_value_read_fn read_first,
    open_cfw_case_value_read_fn read_second);
void open_cfw_case_release_peripheral(
    uint32_t current_resource, uint32_t first_resource,
    uint32_t second_resource, volatile uint32_t *first_control,
    volatile uint32_t *second_control, uint32_t second_config_resource,
    open_cfw_case_command_fn configure,
    open_cfw_case_value_write_fn clear_interrupt);
int open_cfw_case_initialize_channel_profile(
    uint32_t context[10], uint32_t resource,
    open_cfw_case_resource_status_fn initialize,
    open_cfw_case_context_pair_status_fn configure,
    open_cfw_case_resource_action_fn finalize,
    open_cfw_case_void_action_fn failure);
int open_cfw_case_initialize_controller_profile(
    uint8_t context[64], uint32_t resource, uint32_t secondary,
    uint32_t mode, int reset_first, int start_transfer,
    uint32_t transfer_option, const open_cfw_case_controller_init_ops *ops);
int open_cfw_case_initialize_transport_record(
    uint8_t record[80], uint32_t resource, uint32_t descriptor_resource,
    open_cfw_case_status_action_fn platform_initialize,
    open_cfw_case_context_descriptor_status_fn attach,
    open_cfw_case_resource_action_fn finalize,
    open_cfw_case_void_action_fn failure);
int open_cfw_case_wait_controller_flag2(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t control_mask, open_cfw_case_selector_status_fn query,
    open_cfw_case_tick_read_fn tick_read);
int open_cfw_case_start_controller_flag0(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t control_mask, open_cfw_case_status_action_fn ready,
    open_cfw_case_tick_read_fn tick_read);
void open_cfw_case_configure_irq_resource(
    uint32_t current_resource, uint32_t expected_resource,
    volatile uint32_t *clock_control, volatile uint32_t *enable_control,
    open_cfw_case_record_config_fn configure,
    open_cfw_case_dispatch_fn dispatch,
    open_cfw_case_value_write_fn clear_interrupt);
int open_cfw_case_configure_controller_irq(
    uint32_t current_resource, uint32_t expected_resource,
    volatile uint32_t *clock_control, volatile uint32_t *enable_control,
    open_cfw_case_record_status_fn initialize,
    open_cfw_case_dispatch_fn dispatch,
    open_cfw_case_value_write_fn clear_interrupt,
    open_cfw_case_void_action_fn failure);
int open_cfw_case_initialize_application_profile(
    open_cfw_case_context_value_status_fn configure_mode,
    open_cfw_case_record_status_fn initialize,
    open_cfw_case_context_pair_status_fn attach,
    open_cfw_case_void_action_fn failure);
uint64_t open_cfw_case_wait_controller_channels(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t result_tag, uint32_t budget,
    open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_context_mask_status_fn wait_channel);
int open_cfw_case_serial_read_200(
    uint32_t selector, uint8_t *output, uint32_t length,
    volatile uint8_t *state, const open_cfw_case_serial_bus_ops *ops);
int open_cfw_case_serial_read_70(
    uint32_t selector, uint8_t *output, uint32_t length,
    volatile uint8_t *state, const open_cfw_case_serial_bus_ops *ops);
uint16_t open_cfw_case_trimmed_average8(
    void *resource, open_cfw_case_resource_action_fn initialize,
    open_cfw_case_context_value_status_fn configure,
    open_cfw_case_resource_value_read_fn sample,
    open_cfw_case_resource_action_fn finalize);
uint32_t open_cfw_case_derive_clock(const uint32_t registers[4],
                                    uint32_t base_clock);
int open_cfw_case_start_controller(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_tick_read_fn tick_read);
void open_cfw_case_apply_controller_profile(
    volatile uint32_t *controller, const uint32_t profile[6],
    int apply_field_4_6, int apply_field_8_9, int apply_word12);
void open_cfw_case_copy64_protected(
    uint32_t destination[64], const uint32_t source[64],
    volatile uint32_t *controller,
    open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_void_action_fn disable_irq,
    open_cfw_case_irq_restore_fn restore_irq);
int open_cfw_case_run_controller_range(
    uint8_t state[8], volatile uint32_t *controller,
    const uint32_t operation[4], uint32_t *failed_index,
    open_cfw_case_selector_status_fn wait,
    open_cfw_case_value_write_fn single_action,
    open_cfw_case_pair_action_fn range_action);
int open_cfw_case_copy_controller_words(
    uint8_t state[8], volatile uint32_t *controller, uint32_t mask,
    uint32_t destination[64], const uint32_t source[64],
    open_cfw_case_selector_status_fn wait,
    open_cfw_case_copy_action_fn single_copy);
int open_cfw_case_prepare_controller_context(
    uint8_t *context, volatile uint32_t *controller,
    open_cfw_case_resource_action_fn initialize,
    open_cfw_case_resource_status_fn query,
    open_cfw_case_resource_action_fn stop,
    open_cfw_case_resource_status_fn wait_channels);
void open_cfw_case_enable_interrupt_source(
    volatile uint32_t *enable, volatile uint32_t *route,
    uint32_t route_mask, open_cfw_case_dispatch_fn dispatch,
    open_cfw_case_selector_status_fn configure);
int open_cfw_case_initialize_interrupt_path(
    uint32_t selector, uint32_t resource, uint32_t secondary,
    uint32_t period, uint32_t divisor, int double_period,
    uint32_t profile[7], volatile uint32_t *control,
    uint32_t *selected, open_cfw_case_resource_status_fn initialize,
    open_cfw_case_resource_status_fn enable,
    open_cfw_case_value_write_fn configure_interrupt,
    open_cfw_case_dispatch_fn dispatch);
int open_cfw_case_activate_controller(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t controller6_mask,
    open_cfw_case_resource_action_fn configure_irq,
    open_cfw_case_resource_status_fn wait_ready,
    open_cfw_case_resource_status_fn prepare);
int open_cfw_case_program_selector_bank(
    const uint8_t bank[80], open_cfw_case_selector_status_fn reset,
    open_cfw_case_byte_action_fn write,
    open_cfw_case_counted_delay_fn delay,
    open_cfw_case_byte_read_fn read);
uint32_t open_cfw_case_event_group_set_bits(
    open_cfw_case_event_group *group, uint32_t bits,
    open_cfw_case_void_action_fn suspend_scheduler,
    open_cfw_case_waiter_unblock_fn unblock,
    open_cfw_case_void_action_fn resume_scheduler,
    open_cfw_case_void_action_fn failure);
void open_cfw_case_receive_u16(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_irq_restore_fn restore_irq,
    open_cfw_case_resource_action_fn service,
    open_cfw_case_context_short_fn finalize);
void open_cfw_case_receive_u8(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_irq_restore_fn restore_irq,
    open_cfw_case_resource_action_fn service,
    open_cfw_case_context_short_fn finalize);
int open_cfw_case_start_peripheral(
    uint8_t *context, volatile uint32_t *controller, uint32_t status_mask,
    int require_delay, uint32_t delay_numerator, uint32_t delay_divisor,
    open_cfw_case_resource_status_fn query,
    open_cfw_case_tick_read_fn tick_read);
int open_cfw_case_wait_peripheral(
    uint8_t *context, volatile uint32_t *controller, uint32_t timeout,
    open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_resource_status_fn status_query,
    open_cfw_case_resource_status_fn clear_error);
void open_cfw_case_release_pins(
    volatile uint32_t *controller, uint32_t pin_mask,
    uint32_t controller_index, open_cfw_case_pin_state *state);
void open_cfw_case_configure_resource_irq(
    uint32_t resource, uint32_t first_resource, uint32_t second_resource,
    volatile uint32_t *clock, volatile uint32_t *enable,
    open_cfw_case_record_status_fn initialize,
    open_cfw_case_record_config_fn configure,
    open_cfw_case_dispatch_fn dispatch,
    open_cfw_case_value_write_fn clear_interrupt,
    open_cfw_case_void_action_fn failure);
int open_cfw_case_read_controller_blocking(
    uint8_t *context, volatile uint32_t *controller, void *output,
    uint32_t count, uint32_t timeout, open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_wait_condition_fn wait);
int open_cfw_case_write_controller_blocking(
    uint8_t *context, volatile uint32_t *controller, const void *input,
    uint32_t count, uint32_t timeout, open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_wait_condition_fn wait);
void open_cfw_case_apply_context_options(
    volatile uint32_t *controller, const uint32_t options[20]);
int open_cfw_case_wait_condition(
    uint8_t *context, volatile uint32_t *controller, uint32_t mask,
    int expected, uint32_t started, uint32_t timeout,
    open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_irq_restore_fn restore_irq);
void open_cfw_case_begin_receive(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    uint8_t *output, uint32_t count, uint16_t special_mask,
    uint32_t direct_descriptor, uint32_t direct_word_descriptor,
    uint32_t dma_descriptor, uint32_t dma_word_descriptor,
    open_cfw_case_status_action_fn is_privileged,
    open_cfw_case_status_action_fn irq_enabled,
    open_cfw_case_irq_restore_fn restore_irq);
void open_cfw_case_configure_platform_routes(
    volatile uint32_t *clock, volatile uint32_t *enable,
    uint32_t secondary_resource, uint32_t profile_resource,
    uint32_t profile_value_a, uint32_t profile_value_b,
    open_cfw_case_command_fn command,
    open_cfw_case_record_config_fn configure,
    open_cfw_case_dispatch_fn dispatch,
    open_cfw_case_value_write_fn clear_interrupt);
int open_cfw_case_configure_clock_path(
    const uint32_t configuration[4], uint32_t selector,
    volatile uint32_t *selector_register, volatile uint32_t clock_registers[4],
    uint32_t selector_timeout, const uint8_t *shift_table,
    uint32_t shift_table_length, uint32_t base_clock,
    uint32_t *derived_clock,
    open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_selector_status_fn initialize_interrupt);
uint64_t open_cfw_case_calibrate_controller(
    uint8_t *context, volatile uint32_t *controller,
    uint32_t status_mask, uint32_t spin_limit,
    open_cfw_case_resource_status_fn start,
    open_cfw_case_resource_status_fn status,
    open_cfw_case_resource_value_read_fn sample,
    open_cfw_case_tick_read_fn tick_read);
int open_cfw_case_boot_initialize(
    const open_cfw_case_init_entry *begin,
    const open_cfw_case_init_entry *end,
    const uint8_t *packed_begin, const uint8_t *packed_end,
    uint8_t *destination, uint8_t *destination_end,
    open_cfw_case_void_action_fn failure);
int open_cfw_case_wire_read_register(
    uint32_t address, uint32_t selector, uint8_t *output,
    uint32_t length, uint32_t *error,
    const open_cfw_case_wire_ops *ops);
uint64_t open_cfw_case_wire_write_register(
    uint32_t address, uint32_t selector, const uint8_t *input,
    uint32_t length, uint32_t *error,
    const open_cfw_case_wire_ops *ops);
int open_cfw_case_wire_exchange_register(
    uint32_t address, uint8_t value,
    uint8_t *output, uint32_t length, uint32_t *error,
    const open_cfw_case_wire_ops *ops);
void open_cfw_case_process_frame_byte(
    open_cfw_case_frame_parser *parser, uint8_t value,
    open_cfw_case_frame_validate_fn validate,
    open_cfw_case_frame_read_fn read,
    open_cfw_case_status_action_fn start_transfer,
    open_cfw_case_mask_action_fn notify);
void open_cfw_case_emit_probe_train(
    uintptr_t resource, uint32_t mask, uint32_t long_delay,
    open_cfw_case_mask_write_fn write,
    open_cfw_case_counted_delay_fn delay,
    open_cfw_case_counted_delay_fn short_delay);
void open_cfw_case_drain_receive_u16(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    uint16_t fifo_threshold, uint32_t reload_descriptor,
    open_cfw_case_resource_action_fn error,
    open_cfw_case_resource_action_fn service,
    open_cfw_case_context_short_fn finalize);
void open_cfw_case_drain_receive_u8(
    uint8_t *context, volatile uint32_t *controller, uint8_t **cursor,
    uint16_t fifo_threshold, uint32_t reload_descriptor,
    open_cfw_case_resource_action_fn error,
    open_cfw_case_resource_action_fn service,
    open_cfw_case_context_short_fn finalize);
int open_cfw_case_configure_pin_policy(
    uint8_t *context, volatile uint32_t *controller,
    const uint32_t descriptor[3], volatile uint32_t *clock_control,
    uint32_t clock_mask, uint32_t special_a, uint32_t special_b,
    uint32_t special_c, open_cfw_case_resource_status_fn clear_error,
    open_cfw_case_counted_delay_fn delay);
int open_cfw_case_configure_system_clock(
    const uint32_t configuration[14], volatile uint32_t clock[16],
    volatile uint32_t auxiliary[9], volatile uint32_t *oscillator,
    uint32_t timeout, open_cfw_case_tick_read_fn tick_read,
    open_cfw_case_selector_status_fn initialize_interrupt);

#ifdef __cplusplus
}
#endif

#endif
