/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdarg.h>
#include <string.h>
#include <stdint.h>


static uint8_t display_state[4];
static volatile uint32_t codec_identifier = 0xA1B2C3D4U;
static uint32_t last_message[3];
static uint8_t device[80];
static void *last_assign_address;
static uint32_t last_assign_mode;
static uint8_t lens_side;
static uint32_t ambient_encoded;
static volatile uint32_t ambient_route_word = 0x11223344U;
static volatile uint32_t ambient_init_register;
static volatile uint32_t ambient_reset_register;
static uint32_t route_code;
static uint32_t route_value;
static uint32_t delay_ticks;
static uint32_t delay_history[10];
static unsigned int delay_call_count;
static unsigned int buzzer_prepare_calls;
static volatile uint32_t buzzer_route_word = 0x55667788U;
static uint32_t buzzer_frequency;
static uint8_t buzzer_duty;
static unsigned int buzzer_pwm_start_calls;
static unsigned int buzzer_pwm_stop_calls;
static unsigned int buzzer_pin_configure_calls;
static uint32_t buzzer_pin;
static volatile uint32_t buzzer_pin_configuration = 0xA5A55A5AU;
static int buzzer_timer_storage;
static void *buzzer_timer_link = &buzzer_timer_storage;
static volatile uint32_t buzzer_script_state = 7U;
static volatile uint8_t buzzer_active_flag = 1U;
static volatile uint8_t buzzer_pending_flag = 1U;
static uint32_t identifier_selector;
static uint32_t uart_timeout;
static int uart_result;
static uint8_t uart_initialized;
static uint8_t uart_error_flag;
static uint32_t uart_device_storage[11];
static int uart_mutex_storage;
static int uart_semaphore_storage;
static void *uart_device_link = &uart_device_storage;
static void *uart_mutex_link = &uart_mutex_storage;
static void *uart_semaphore_link = &uart_semaphore_storage;
static uint8_t uart_tx_buffer[0x400];
static volatile uint32_t uart_cache_clean_register;
static volatile uint32_t uart_registers[0x1000U / sizeof(uint32_t)];
static unsigned int uart_data_barriers;
static uint8_t uart_cache_barrier_sequence[12];
static unsigned int uart_cache_barrier_calls;
static unsigned int uart_delay_calls;
static uint8_t audio_status[3] = {7U, 8U, 9U};
static uint32_t codec_route_code;
static uint8_t codec_route_enabled;
static int codec_route_result;
static volatile uint32_t display_stage_1_word;
static volatile uint32_t display_stage_3_word;
static volatile uint32_t display_stage_2_first_word;
static volatile uint32_t display_stage_2_second_word;
static unsigned int display_reinitialize_calls;
static unsigned int display_apply_calls;
static uint8_t audio_path_table[24];
static uint8_t audio_path_selector;
static uint16_t audio_path_identifier;
static char *audio_path_output;
static uint32_t audio_path_capacity;
static uint8_t time_configuration[9];
static const uint8_t *time_configuration_link = time_configuration;
static uint32_t time_output_seconds;
static void *time_output_record;
struct open_cfw_pt_uled_operations;
static const struct open_cfw_pt_uled_operations *uled_operations_link;
static uint16_t uled_identifier = 0x4567U;
static uint32_t uled_brightness_arguments[3];
static uint8_t uled_offset_arguments[2];
static int uled_brightness_result;
static int uled_offset_result;
static int32_t identifier_2_result = (int32_t)0x2BAD0000U;
static uint8_t identifier_2_value;
static const uint8_t identifier_2_device;
static int charger_device_storage;
static void *charger_open_result = &charger_device_storage;
static uint32_t charger_disable_argument;
static uint32_t charger_enable_argument;
static volatile uint32_t audio_capture_active;
static uint32_t audio_register_listener;
static uint32_t audio_register_mode;
static const void *audio_register_callback;
static int audio_remove_result;
static uint32_t audio_remove_listener;
static uint32_t audio_remove_mode;
static uint32_t codec_mic_enabled;
static uint32_t pdm_mic_enabled;
static uint32_t pcm_route_mode;
static uint32_t audio_unregister_mode;
static union { uint64_t align; uint8_t bytes[6000]; } lc3_encoder_storage;
static const uint8_t audio_single_callback;
static const uint8_t audio_stereo_callback;
static union { uint32_t words[0xA44U / 4U]; uint8_t bytes[0xA44U]; }
    audio_codec_buffer_0;
static union { uint32_t words[0xA44U / 4U]; uint8_t bytes[0xA44U]; }
    audio_codec_buffer_1;
static union { uint32_t words[0xA44U / 4U]; uint8_t bytes[0xA44U]; }
    audio_pdm_buffer;
static volatile uint32_t identifier_1_state;
static int identifier_1_initialize_result;
static int identifier_1_read_result;
static uint32_t identifier_1_read_value;
static unsigned int identifier_1_sequence;
static uint32_t configured_seconds;
static unsigned int rtc_set_calls;
static int display_mutex_storage;
static int display_queue_storage;
static void *display_mutex_link = &display_mutex_storage;
static void *display_queue_link = &display_queue_storage;
static uint8_t display_buffer[0x2800];
static uintptr_t display_write_source;
static uint32_t display_write_length;
static uint8_t submitted_display_message[12];
static int display_queue_result;
static unsigned int fail_stop_calls;
static int lens_queue_storage;
static int lens_event_storage;
static void *lens_queue_link = &lens_queue_storage;
static void *lens_event_link = &lens_event_storage;
static int lens_queue_result;
static void *submitted_lens_message;
static uint32_t event_flags;
static unsigned int allocation_count;
static unsigned int allocation_fail_at;
static unsigned int allocation_fail_first;
static uint8_t allocation_fail_always;
static void *released_allocations[2];
static unsigned int released_allocation_count;
static union { uint64_t align; uint8_t bytes[32]; } allocation_0;
static union { uint64_t align; uint8_t bytes[0x10000]; } allocation_1;
static unsigned int system_reset_inner_calls;
static volatile uint32_t system_reset_control;
static unsigned int system_reset_wait_calls;
static unsigned int system_reset_barrier_calls;
static uint32_t system_reset_barrier_values[2];
static int input_queue_storage;
static int input_thread_storage;
static int audio_queue_storage;
static int audio_thread_storage;
static void *input_queue_link = &input_queue_storage;
static void *input_thread_link = &input_thread_storage;
static void *audio_queue_link = &audio_queue_storage;
static void *audio_thread_link = &audio_thread_storage;
static uint32_t direct_audio_message[4];
static uint32_t direct_thread_flags;
static void *direct_thread;
static int direct_queue_result;
static unsigned int direct_queue_calls;
static unsigned int input_log_calls;
static int input_log_result;
static uint32_t audio_log_filter;
static unsigned int audio_log_filter_calls;
static unsigned int audio_structured_log_calls;
static unsigned int audio_trace_log_calls;
static int audio_log_result;
static uint32_t audio_log_level;
static uint32_t audio_log_line;
static uint32_t audio_trace_flags;
static const char *audio_log_function;
static const char *audio_log_message;
static uint32_t audio_log_arguments[2];
static unsigned int audio_log_argument_count;
static unsigned int ring_acquire_barriers;
static unsigned int ring_release_barriers;
static unsigned int ring_callback_calls;
static void *ring_callback_descriptor;
static uint32_t ring_callback_event;
static uint32_t ring_callback_count;
static volatile uint32_t *ring_callback_write_index;
static uint32_t ring_callback_observed_write_index;
static const char *audio_name_table[2] = {"codec", "pdm"};
static union { uint64_t align; uint8_t bytes[32]; } audio_registration_storage;
static union { uint64_t align; uint8_t bytes[32]; } audio_recorder_storage;
static int direct_audio_file;
static unsigned int direct_file_close_calls;
static uint16_t ambient_registers[256];
static unsigned int ambient_bus_write_calls;
static int font_mutex_storage;
static int font_device_storage;
static void *font_mutex_link = &font_mutex_storage;
static void *font_device_link = &font_device_storage;
static volatile uint8_t font_configuration_flag;
static volatile uint8_t font_xip_active;
static uint32_t mspi_control_operation;
static uint32_t mspi_control_argument;
static unsigned int mspi_control_calls;
static int font_mutex_acquire_result;
static int font_mutex_release_result;
static unsigned int mram_delete_all_calls;
static unsigned int privacy_clear_calls;
static volatile uint8_t pairing_flag_0;
static volatile uint32_t pairing_word;
static volatile uint8_t pairing_flag_1;
static const uint8_t direct_charger_configuration;
static const void *direct_charger_interface_link;
static uint32_t direct_charger_registers[2];
static uint8_t direct_charger_values[2];
static unsigned int direct_charger_write_calls;
static uint8_t direct_identifier_value = 0x42U;
static uint8_t postprocess_state_0;
static uint8_t postprocess_state_1;
static uint8_t postprocess_state_2;
static uint8_t postprocess_ready;
static volatile uint32_t postprocess_active;
static volatile uint32_t postprocess_primary;
static volatile uint32_t postprocess_mode;
static volatile uint32_t time_format_word;
static unsigned int postprocess_send_calls;
static uint16_t postprocess_transport_first;
static const void *postprocess_transport_second;
static uint32_t postprocess_transport_third;
static uint32_t postprocess_transport_fourth;
static uint8_t postprocess_transport_command;
static uint8_t postprocess_transport_route;
static uint32_t postprocess_transport_auxiliary;
static unsigned int postprocess_refresh_calls;
static unsigned int postprocess_onboarding_calls;
static unsigned int postprocess_remove_calls;
static unsigned int postprocess_commit_calls;
enum {
    HOST_FONT_XIP_START = 0x10000000U,
    HOST_FONT_XIP_END = 0x10020000U,
    HOST_FONT_0_BASE = 0x10000000U,
    HOST_FONT_1_BASE = 0x10010000U
};
static uint8_t font_xip[HOST_FONT_XIP_END - HOST_FONT_XIP_START];
static uint32_t font_xip_read_calls;


static void host_input_message_send(const void *message)
{
    const uint32_t *words = message;
    last_message[0] = words[0];
    last_message[1] = words[1];
    last_message[2] = words[2];
}


static void host_ambient_assign(void *address, uint32_t mode)
{
    last_assign_address = address;
    last_assign_mode = mode;
}


static uint16_t host_ambient_sample(void *address)
{
    if (address == device + 0x33U) return 0x1234U;
    if (address == device + 0x36U) return 0x5678U;
    return 0U;
}


static uint32_t host_ambient_raw_read(uint32_t channel)
{
    assert(channel == 0U);
    return ambient_encoded;
}

static int host_ambient_bus_read(uint32_t bus, uint32_t device_address,
                                 const void *register_address,
                                 uint32_t register_length, void *output,
                                 uint32_t output_length)
{
    uint8_t address = *(const uint8_t *)register_address;
    uint8_t *bytes = output;
    assert(bus == 2U && device_address == 0x45U);
    assert(register_length == 1U && output_length == 2U);
    bytes[0] = (uint8_t)(ambient_registers[address] >> 8U);
    bytes[1] = (uint8_t)ambient_registers[address];
    return 0;
}

static int host_ambient_bus_write(uint32_t bus, uint32_t device_address,
                                  const void *register_address,
                                  uint32_t register_length,
                                  const void *input, uint32_t input_length)
{
    uint8_t address = *(const uint8_t *)register_address;
    const uint8_t *bytes = input;
    assert(bus == 2U && device_address == 0x45U);
    assert(register_length == 1U && input_length == 2U);
    ambient_registers[address] =
        (uint16_t)((uint16_t)bytes[0] << 8U) | bytes[1];
    ++ambient_bus_write_calls;
    return 0;
}


static uint8_t host_lens_side(void)
{
    return lens_side;
}


static void host_audio_codec_route(uint32_t code, uint32_t value)
{
    route_code = code;
    route_value = value;
    if (value == buzzer_pin_configuration) {
        buzzer_pin = code;
        ++buzzer_pin_configure_calls;
    }
}


static int host_delay_ticks(uint32_t ticks)
{
    delay_ticks = ticks;
    if (delay_call_count < 10U) delay_history[delay_call_count] = ticks;
    ++delay_call_count;
    return 0;
}


static int host_buzzer_timer_stop(void *timer)
{
    assert(timer == &buzzer_timer_storage);
    ++buzzer_prepare_calls;
    return 0;
}


static void host_buzzer_pwm_update(uint32_t frequency, uint8_t duty)
{
    buzzer_frequency = frequency;
    buzzer_duty = duty;
}


static void host_buzzer_pwm_start(void)
{
    ++buzzer_pwm_start_calls;
}


static void host_buzzer_pwm_stop(void)
{
    ++buzzer_pwm_stop_calls;
}


static void host_hardware_identifier_read(uint32_t selector, uint32_t *record)
{
    unsigned int index;
    identifier_selector = selector;
    for (index = 0U; index < 16U; ++index) record[index] = 0U;
    record[0] = 0xCAFEBABEU;
}


static void host_uart_data_memory_barrier(void) { ++uart_data_barriers; }
static void host_uart_cache_dsb(void)
{
    assert(uart_cache_barrier_calls < sizeof(uart_cache_barrier_sequence));
    uart_cache_barrier_sequence[uart_cache_barrier_calls++] = 1U;
}
static void host_uart_cache_isb(void)
{
    assert(uart_cache_barrier_calls < sizeof(uart_cache_barrier_sequence));
    uart_cache_barrier_sequence[uart_cache_barrier_calls++] = 2U;
}
static uint32_t host_uart_tick_get(void) { return 123U; }
static int host_uart_semaphore_acquire(void *semaphore, uint32_t timeout)
{
    assert(semaphore == &uart_semaphore_storage);
    uart_timeout = timeout;
    return timeout == 0U ? 0 : uart_result;
}
static void host_uart_delay_us(uint32_t microseconds)
{
    assert(microseconds == 10U);
    ++uart_delay_calls;
}


static int host_codec_route_set(uint32_t code, uint8_t enabled)
{
    codec_route_code = code;
    codec_route_enabled = enabled;
    return codec_route_result;
}


static void host_display_reinitialize(void)
{
    ++display_reinitialize_calls;
}


static void host_display_apply(uint32_t a, uint32_t b, uint32_t c,
                               uint32_t d, uint32_t width, uint32_t height)
{
    assert(a == 0U && b == 0U && c == 0U && d == 0U);
    assert(width == 0x240U && height == 0x120U);
    ++display_apply_calls;
}


static int32_t host_lens_sync_transport(uint16_t first, const void *second,
                                        uint32_t third, uint32_t fourth,
                                        uint8_t command, uint8_t route,
                                        uint32_t auxiliary)
{
    postprocess_transport_first = first;
    postprocess_transport_second = second;
    postprocess_transport_third = third;
    postprocess_transport_fourth = fourth;
    postprocess_transport_command = command;
    postprocess_transport_route = route;
    postprocess_transport_auxiliary = auxiliary;
    ++postprocess_send_calls;
    return -1;
}


static void host_audio_path_format_provider(uint8_t selector,
                                            uint16_t identifier,
                                            char *path,
                                            uint32_t capacity)
{
    audio_path_selector = selector;
    audio_path_identifier = identifier;
    audio_path_output = path;
    audio_path_capacity = capacity;
}


static void host_time_read(void *record)
{
    uint8_t *bytes = record;
    unsigned int index;
    for (index = 0U; index < 40U; ++index) bytes[index] = (uint8_t)index;
}


static int32_t host_time_to_seconds(const void *record)
{
    const uint8_t *bytes = record;
    assert(bytes[0] == 0U && bytes[39] == 39U);
    return 100000;
}


static void host_time_output(uint32_t seconds, void *record)
{
    time_output_seconds = seconds;
    time_output_record = record;
}


static int host_uled_read_chip_id(uint16_t *identifier)
{
    *identifier = uled_identifier;
    return 0;
}


static int host_uled_set_brightness(uint32_t delay, uint32_t period,
                                    uint32_t brightness)
{
    uled_brightness_arguments[0] = delay;
    uled_brightness_arguments[1] = period;
    uled_brightness_arguments[2] = brightness;
    return uled_brightness_result;
}


static int host_uled_set_offset(uint8_t first, uint8_t second)
{
    uled_offset_arguments[0] = first;
    uled_offset_arguments[1] = second;
    return uled_offset_result;
}


static int32_t host_hardware_identifier_2_read(const void *device,
                                               uint32_t command,
                                               uint8_t *value,
                                               uint32_t length)
{
    assert(device == &identifier_2_device);
    assert(command == 0x101U);
    assert(length == 1U);
    *value = identifier_2_value;
    return identifier_2_result;
}


static void *host_charger_open(const void *device, uint32_t index)
{
    assert(device == &charger_device_storage);
    assert(index == 0U);
    return charger_open_result;
}


static int32_t host_charger_disable(void *device, uint32_t argument)
{
    assert(device == &charger_device_storage);
    charger_disable_argument = argument;
    return (int32_t)0x2BAD0000U;
}


static int32_t host_charger_enable(void *device, uint32_t argument)
{
    assert(device == &charger_device_storage);
    charger_enable_argument = argument;
    return (int32_t)0x2BAD0000U;
}


static int host_audio_register(uint32_t listener, uint32_t mode,
                               const void *callback)
{
    audio_register_listener = listener;
    audio_register_mode = mode;
    audio_register_callback = callback;
    return 0;
}


static int host_audio_remove(uint32_t listener, uint32_t mode)
{
    audio_remove_listener = listener;
    audio_remove_mode = mode;
    return audio_remove_result;
}


static void host_codec_mic_enable(uint32_t enabled)
{
    codec_mic_enabled = enabled;
}


static void host_pdm_mic_enable(uint32_t enabled)
{
    pdm_mic_enabled = enabled;
}


static void host_pcm_route(uint32_t mode)
{
    pcm_route_mode = mode;
}


static void host_audio_unregister(uint32_t mode)
{
    audio_unregister_mode = mode;
}


static int host_identifier_1_initialize(void)
{
    assert(identifier_1_sequence == 0U);
    identifier_1_sequence = 1U;
    return identifier_1_initialize_result;
}


static void host_identifier_1_acquire(void)
{
    assert(identifier_1_sequence <= 1U);
    identifier_1_sequence = 2U;
}


static void host_identifier_1_prepare(void)
{
    assert(identifier_1_sequence == 2U);
    identifier_1_sequence = 3U;
}


static int host_identifier_1_read(uint32_t *value)
{
    assert(identifier_1_sequence == 3U);
    identifier_1_sequence = 4U;
    *value = identifier_1_read_value;
    return identifier_1_read_result;
}


static void host_identifier_1_finish(void)
{
    assert(identifier_1_sequence == 4U);
    identifier_1_sequence = 5U;
}


static void host_identifier_1_release(void)
{
    assert(identifier_1_sequence == 5U);
    identifier_1_sequence = 6U;
}


static void host_seconds_to_time(uint32_t seconds, void *record)
{
    uint8_t *bytes = record;
    unsigned int index;
    configured_seconds = seconds;
    for (index = 0U; index < 40U; ++index) bytes[index] = (uint8_t)(40U-index);
}


static void host_rtc_set_time(const void *record)
{
    const uint8_t *bytes = record;
    assert(bytes[0] == 40U && bytes[39] == 1U);
    ++rtc_set_calls;
}


static int host_mutex_acquire(void *mutex, uint32_t timeout)
{
    assert(mutex == &display_mutex_storage || mutex == &font_mutex_storage ||
           mutex == &uart_mutex_storage);
    assert(timeout == 0xFFFFFFFFU);
    return mutex == &font_mutex_storage ? font_mutex_acquire_result : 0;
}


static int host_mutex_release(void *mutex)
{
    assert(mutex == &display_mutex_storage || mutex == &font_mutex_storage ||
           mutex == &uart_mutex_storage);
    return mutex == &font_mutex_storage ? font_mutex_release_result : 0;
}

static int32_t host_mspi_control(void *device, uint32_t operation,
                                 uint32_t argument)
{
    assert(device == &font_device_storage);
    mspi_control_operation = operation;
    mspi_control_argument = argument;
    ++mspi_control_calls;
    return 0;
}

static void host_mram_delete_all(void) { ++mram_delete_all_calls; }
static void host_privacy_clear(void) { ++privacy_clear_calls; }

static const void *host_charger_slot_configuration(void *handle)
{
    assert(handle != NULL);
    return &direct_charger_configuration;
}

static const void *host_charger_configuration_interface(
    const void *configuration)
{
    assert(configuration == &direct_charger_configuration);
    return direct_charger_interface_link;
}

static int32_t host_direct_charger_write(const void *context,
                                         uint32_t register_address,
                                         const void *input, uint32_t length)
{
    assert(context == &direct_charger_configuration && length == 1U);
    assert(direct_charger_write_calls < 2U);
    direct_charger_registers[direct_charger_write_calls] = register_address;
    direct_charger_values[direct_charger_write_calls] = *(const uint8_t *)input;
    ++direct_charger_write_calls;
    return (int32_t)0x2BAD0000U;
}

static int32_t host_direct_identifier_read(const void *context,
                                           uint32_t register_address,
                                           uint8_t *output, uint32_t length)
{
    assert(context == &direct_identifier_value);
    assert(register_address == 0x101U && length == 1U && output != NULL);
    *output = direct_identifier_value;
    return (int32_t)0x2BAD0000U;
}


static void host_display_buffer_write(void *destination, uintptr_t source,
                                      uint32_t length)
{
    assert(destination == display_buffer);
    display_write_source = source;
    display_write_length = length;
}


static void host_system_reset_barrier(void)
{
    assert(system_reset_barrier_calls < 2U);
    system_reset_barrier_values[system_reset_barrier_calls++] =
        system_reset_control;
}


static void host_ring_acquire_barrier(void) { ++ring_acquire_barriers; }
static void host_ring_release_barrier(void) { ++ring_release_barriers; }


static void host_ring_callback(void *descriptor, uint32_t event,
                               uint32_t count)
{
    ++ring_callback_calls;
    ring_callback_descriptor = descriptor;
    ring_callback_event = event;
    ring_callback_count = count;
    ring_callback_observed_write_index = *ring_callback_write_index;
}


static unsigned int host_input_log_failure(const char *format, int result)
{
    assert(strcmp(format, "input queue failure %x") == 0);
    ++input_log_calls;
    input_log_result = result;
    return 0U;
}


static uint32_t host_audio_log_filter(void)
{
    ++audio_log_filter_calls;
    return audio_log_filter;
}


static unsigned int host_audio_log_argument_count(const char *message)
{
    if (strcmp(message, "Invalid parameters for app registration") == 0 ||
            strcmp(message, "[svc.audio]Invalid parameters for app registration") == 0 ||
            strcmp(message, "No PCM app registered") == 0 ||
            strcmp(message, "[svc.audio]No PCM app registered") == 0 ||
            strcmp(message, "font mutex acquire failed") == 0 ||
            strcmp(message, "[font]font mutex acquire failed") == 0 ||
            strcmp(message, "font mutex release failed") == 0 ||
            strcmp(message, "[font]font mutex release failed") == 0)
        return 0U;
    if (strcmp(message, "PCM app registered: ID=%d, Source=%d") == 0 ||
            strcmp(message, "[svc.audio]PCM app registered: ID=%d, Source=%d") == 0 ||
            strcmp(message, "App ID %d not found, current app ID is %d") == 0 ||
            strcmp(message, "[svc.audio]App ID %d not found, current app ID is %d") == 0)
        return 2U;
    return 1U;
}


static void host_audio_structured_log(uint32_t level, const char *tag,
                                      const char *file, const char *function,
                                      uint32_t line, const char *message, ...)
{
    va_list arguments;
    unsigned int index;
    assert(tag != NULL && file != NULL && function != NULL && message != NULL);
    audio_log_level = level;
    audio_log_line = line;
    audio_log_function = function;
    audio_log_message = message;
    audio_log_argument_count = host_audio_log_argument_count(message);
    va_start(arguments, message);
    if (strcmp(message, "audio queue failure %x") == 0) {
        audio_log_arguments[0] = (uint32_t)va_arg(arguments, int);
    } else {
        for (index = 0U; index < audio_log_argument_count; ++index)
            audio_log_arguments[index] = va_arg(arguments, uint32_t);
    }
    va_end(arguments);
    ++audio_structured_log_calls;
    if (audio_log_argument_count != 0U)
        audio_log_result = (int)audio_log_arguments[
            audio_log_argument_count - 1U];
}


static void host_audio_trace_log(uint32_t flags, const char *format, ...)
{
    va_list arguments;
    unsigned int index;
    const char *source;
    audio_trace_flags = flags;
    audio_log_message = format;
    audio_log_argument_count = host_audio_log_argument_count(format);
    va_start(arguments, format);
    source = va_arg(arguments, const char *);
    assert(format == source);
    if (strcmp(format, "[thread.audio]audio queue failure %x") == 0) {
        audio_log_arguments[0] = (uint32_t)va_arg(arguments, int);
    } else {
        for (index = 0U; index < audio_log_argument_count; ++index)
            audio_log_arguments[index] = va_arg(arguments, uint32_t);
    }
    va_end(arguments);
    ++audio_trace_log_calls;
    if (audio_log_argument_count != 0U)
        audio_log_result = (int)audio_log_arguments[
            audio_log_argument_count - 1U];
}


static int host_queue_send(void *queue, const void *message,
                           uint32_t priority, uint32_t timeout)
{
    assert(priority == 0U);
    if (timeout == 0U) {
        ++direct_queue_calls;
        if (direct_queue_result == 0) {
            if (queue == &input_queue_storage)
                memcpy(last_message, message, sizeof(last_message));
            else {
                assert(queue == &audio_queue_storage);
                memcpy(direct_audio_message, message,
                       sizeof(uint32_t) * 3U);
            }
        }
        return direct_queue_result;
    }
    if (timeout == 1000U) {
        assert(queue == &display_queue_storage);
        memcpy(submitted_display_message, message,
               sizeof(submitted_display_message));
        return display_queue_result;
    }
    assert(timeout == 2000U);
    assert(queue == &lens_queue_storage);
    submitted_lens_message = *(void *const *)message;
    return lens_queue_result;
}


static void host_fail_stop(void)
{
    ++fail_stop_calls;
}


static void *host_lens_allocate(uint32_t size)
{
    void *result;
    ++allocation_count;
    if (allocation_fail_always != 0U ||
            allocation_count <= allocation_fail_first ||
            allocation_fail_at == allocation_count)
        return NULL;
    if (allocation_count == 1U) {
        assert(size <= sizeof(allocation_0.bytes));
        result = allocation_0.bytes;
    } else {
        assert(size <= sizeof(allocation_1.bytes));
        result = allocation_1.bytes;
    }
    memset(result, 0, size);
    return result;
}


static void host_lens_release(void *allocation)
{
    assert(released_allocation_count < 2U);
    released_allocations[released_allocation_count++] = allocation;
}


static uint32_t host_event_flags_set(void *event, uint32_t flags)
{
    assert(event == &lens_event_storage);
    event_flags = flags;
    return flags;
}

static uint32_t host_thread_flags_set(void *thread, uint32_t flags)
{
    direct_thread = thread;
    direct_thread_flags = flags;
    return flags;
}

static int host_direct_file_close(void *file)
{
    assert(file == &direct_audio_file);
    ++direct_file_close_calls;
    return 0;
}

static void host_system_reset_inner(void) { ++system_reset_inner_calls; }
static uint8_t host_postprocess_state_0(void) { return postprocess_state_0; }
static uint8_t host_postprocess_state_1(void) { return postprocess_state_1; }
static uint8_t host_postprocess_state_2(void) { return postprocess_state_2; }
static void host_postprocess_refresh(void) { ++postprocess_refresh_calls; }
static int host_postprocess_onboarding(uint8_t index, const uint8_t *enabled)
{
    assert(index == 0U && enabled != NULL && *enabled == 1U);
    ++postprocess_onboarding_calls;
    return 0;
}
static int host_postprocess_remove(const void *path)
{
    assert(path == (const void *)0x1234U);
    ++postprocess_remove_calls;
    return 0;
}
static void host_postprocess_commit(void) { ++postprocess_commit_calls; }
static void host_font_xip_read(uint32_t address, uint8_t *destination,
                               uint32_t length)
{
    uint32_t offset = address - HOST_FONT_XIP_START;
    assert(address >= HOST_FONT_XIP_START);
    assert(length <= HOST_FONT_XIP_END - address);
    memcpy(destination, &font_xip[offset], length);
    ++font_xip_read_calls;
}


static uint16_t host_font_crc16(const uint8_t *data, uint32_t length)
{
    uint16_t crc = 0xFFFFU;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        uint32_t bit;
        crc ^= (uint16_t)((uint16_t)data[index] << 8U);
        for (bit = 0U; bit < 8U; ++bit)
            crc = (uint16_t)((crc & 0x8000U) != 0U
                ? (uint16_t)((uint16_t)(crc << 1U) ^ 0x1021U)
                : (uint16_t)(crc << 1U));
    }
    return crc;
}


static void host_font_prepare(uint32_t base, uint32_t length)
{
    uint32_t offset = base - HOST_FONT_XIP_START;
    uint32_t candidate;
    uint16_t crc = 0U;
    uint8_t *payload = &font_xip[offset + 0x45U];

    memset(&font_xip[offset], 0, 0x46U + length);
    font_xip[offset + 0x40U] = (uint8_t)length;
    font_xip[offset + 0x41U] = (uint8_t)(length >> 8U);
    font_xip[offset + 0x42U] = (uint8_t)(length >> 16U);
    font_xip[offset + 0x43U] = (uint8_t)(length >> 24U);
    for (candidate = 1U; candidate < length; ++candidate)
        payload[candidate] = (uint8_t)(candidate * 17U + 3U);
    for (candidate = 0U; candidate <= 0xFFU; ++candidate) {
        payload[0] = (uint8_t)candidate;
        crc = host_font_crc16(payload, length);
        if ((uint8_t)(crc >> 8U) == payload[0])
            break;
    }
    assert(candidate <= 0xFFU);
    font_xip[offset + 0x44U] = (uint8_t)crc;
}


#define OPEN_CFW_PT_DISPLAY_STATE display_state
#define OPEN_CFW_PT_CODEC_IDENTIFIER_WORD (&codec_identifier)
#define OPEN_CFW_PT_INPUT_MESSAGE_SEND host_input_message_send
#define OPEN_CFW_PT_INPUT_THREAD_LINK (&input_thread_link)
#define OPEN_CFW_PT_INPUT_QUEUE_LINK (&input_queue_link)
#define OPEN_CFW_PT_INPUT_LOG_FAILURE host_input_log_failure
#define OPEN_CFW_PT_INPUT_QUEUE_FAILURE_FORMAT "input queue failure %x"
#define OPEN_CFW_PT_BUZZER_ROUTE_WORD (&buzzer_route_word)
#define OPEN_CFW_PT_BUZZER_PWM_UPDATE host_buzzer_pwm_update
#define OPEN_CFW_PT_BUZZER_PWM_START host_buzzer_pwm_start
#define OPEN_CFW_PT_BUZZER_PWM_STOP host_buzzer_pwm_stop
#define OPEN_CFW_PT_BUZZER_PIN_CONFIGURATION (&buzzer_pin_configuration)
#define OPEN_CFW_PT_BUZZER_TIMER_LINK (&buzzer_timer_link)
#define OPEN_CFW_PT_BUZZER_TIMER_STOP host_buzzer_timer_stop
#define OPEN_CFW_PT_BUZZER_SCRIPT_STATE (&buzzer_script_state)
#define OPEN_CFW_PT_BUZZER_ACTIVE_FLAG (&buzzer_active_flag)
#define OPEN_CFW_PT_BUZZER_PENDING_FLAG (&buzzer_pending_flag)
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_READ host_hardware_identifier_read
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_STATE (&identifier_1_state)
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_INITIALIZE host_identifier_1_initialize
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_ACQUIRE host_identifier_1_acquire
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_PREPARE host_identifier_1_prepare
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_READ host_identifier_1_read
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_FINISH host_identifier_1_finish
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_RELEASE host_identifier_1_release
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_2_READ host_hardware_identifier_2_read
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_2_DEVICE (&identifier_2_device)
#define OPEN_CFW_PT_CHARGER_OPEN host_charger_open
#define OPEN_CFW_PT_CHARGER_DEVICE (&charger_device_storage)
#define OPEN_CFW_PT_CHARGER_DISABLE host_charger_disable
#define OPEN_CFW_PT_CHARGER_ENABLE host_charger_enable
#define OPEN_CFW_PT_CHARGER_SLOT_CONFIGURATION(handle) \
    host_charger_slot_configuration(handle)
#define OPEN_CFW_PT_CHARGER_CONFIGURATION_INTERFACE(configuration) \
    host_charger_configuration_interface(configuration)
#define OPEN_CFW_PT_UART_INITIALIZED (&uart_initialized)
#define OPEN_CFW_PT_UART_DEVICE_LINK (&uart_device_link)
#define OPEN_CFW_PT_UART_MUTEX_LINK (&uart_mutex_link)
#define OPEN_CFW_PT_UART_SEMAPHORE_LINK (&uart_semaphore_link)
#define OPEN_CFW_PT_UART_ERROR_FLAG (&uart_error_flag)
#define OPEN_CFW_PT_UART_TX_BUFFER uart_tx_buffer
#define OPEN_CFW_PT_UART_CACHE_CLEAN_REGISTER (&uart_cache_clean_register)
#define OPEN_CFW_PT_UART_REGISTER_BASE uart_registers
#define OPEN_CFW_PT_UART_DATA_MEMORY_BARRIER host_uart_data_memory_barrier
#define OPEN_CFW_PT_UART_TICK_GET host_uart_tick_get
#define OPEN_CFW_PT_UART_SEMAPHORE_ACQUIRE host_uart_semaphore_acquire
#define OPEN_CFW_PT_UART_DELAY_US host_uart_delay_us
#define OPEN_CFW_PT_UART_CACHE_DSB host_uart_cache_dsb
#define OPEN_CFW_PT_UART_CACHE_ISB host_uart_cache_isb
#define OPEN_CFW_PT_AUDIO_STATUS_BASE audio_status
#define OPEN_CFW_PT_CODEC_ROUTE_SET host_codec_route_set
#define OPEN_CFW_PT_AUDIO_CAPTURE_ACTIVE (&audio_capture_active)
#define OPEN_CFW_PT_AUDIO_REGISTER host_audio_register
#define OPEN_CFW_PT_AUDIO_REMOVE host_audio_remove
#define OPEN_CFW_PT_AUDIO_REGISTRATION_TABLE \
    ((volatile struct open_cfw_pt_audio_registration *) \
        audio_registration_storage.bytes)
#define OPEN_CFW_PT_AUDIO_SINGLE_CALLBACK (&audio_single_callback)
#define OPEN_CFW_PT_AUDIO_STEREO_CALLBACK (&audio_stereo_callback)
#define OPEN_CFW_PT_CODEC_MIC_ENABLE host_codec_mic_enable
#define OPEN_CFW_PT_PDM_MIC_ENABLE host_pdm_mic_enable
#define OPEN_CFW_PT_AUDIO_THREAD_LINK (&audio_thread_link)
#define OPEN_CFW_PT_AUDIO_QUEUE_LINK (&audio_queue_link)
#define OPEN_CFW_PT_PCM_ROUTE host_pcm_route
#define OPEN_CFW_PT_AUDIO_UNREGISTER host_audio_unregister
#define OPEN_CFW_PT_AUDIO_RECORDER_TABLE \
    ((volatile struct open_cfw_pt_audio_recorder *)audio_recorder_storage.bytes)
#define OPEN_CFW_PT_AUDIO_NAME_TABLE audio_name_table
#define OPEN_CFW_PT_FILE_CLOSE host_direct_file_close
#define OPEN_CFW_PT_AUDIO_CODEC_BUFFER_0 (audio_codec_buffer_0.bytes)
#define OPEN_CFW_PT_AUDIO_CODEC_BUFFER_1 (audio_codec_buffer_1.bytes)
#define OPEN_CFW_PT_AUDIO_PDM_BUFFER (audio_pdm_buffer.bytes)
#define OPEN_CFW_PT_DISPLAY_STAGE_1_WORD (&display_stage_1_word)
#define OPEN_CFW_PT_DISPLAY_STAGE_3_WORD (&display_stage_3_word)
#define OPEN_CFW_PT_DISPLAY_STAGE_2_FIRST_WORD (&display_stage_2_first_word)
#define OPEN_CFW_PT_DISPLAY_STAGE_2_SECOND_WORD (&display_stage_2_second_word)
#define OPEN_CFW_PT_DISPLAY_REINITIALIZE host_display_reinitialize
#define OPEN_CFW_PT_DISPLAY_APPLY host_display_apply
#define OPEN_CFW_PT_LENS_SYNC_TRANSPORT host_lens_sync_transport
#define OPEN_CFW_PT_ULED_OPERATIONS_LINK (&uled_operations_link)
#define OPEN_CFW_PT_DISPLAY_MUTEX_LINK (&display_mutex_link)
#define OPEN_CFW_PT_DISPLAY_QUEUE_LINK (&display_queue_link)
#define OPEN_CFW_PT_DISPLAY_BUFFER display_buffer
#define OPEN_CFW_PT_MUTEX_ACQUIRE host_mutex_acquire
#define OPEN_CFW_PT_MUTEX_RELEASE host_mutex_release
#define OPEN_CFW_PT_DISPLAY_BUFFER_WRITE host_display_buffer_write
#define OPEN_CFW_PT_QUEUE_SEND host_queue_send
#define OPEN_CFW_PT_RING_ACQUIRE_BARRIER() host_ring_acquire_barrier()
#define OPEN_CFW_PT_RING_RELEASE_BARRIER() host_ring_release_barrier()
#define OPEN_CFW_PT_AUDIO_LOG_FILTER_READ() host_audio_log_filter()
#define OPEN_CFW_PT_AUDIO_STRUCTURED_LOG host_audio_structured_log
#define OPEN_CFW_PT_AUDIO_TRACE_LOG host_audio_trace_log
#define OPEN_CFW_PT_AUDIO_LOG_TAG "thread.audio"
#define OPEN_CFW_PT_AUDIO_LOG_FILE "thread_audio.c"
#define OPEN_CFW_PT_AUDIO_LOG_FUNCTION "AUD_SendMessage"
#define OPEN_CFW_PT_AUDIO_LOG_MESSAGE "audio queue failure %x"
#define OPEN_CFW_PT_AUDIO_TRACE_MESSAGE \
    "[thread.audio]audio queue failure %x"
#define OPEN_CFW_PT_SERVICE_AUDIO_LOG_TAG "svc.audio"
#define OPEN_CFW_PT_SERVICE_AUDIO_LOG_FILE "service_audio.c"
#define OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_FUNCTION "SVC_PcmAppRegister"
#define OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_INVALID_MESSAGE \
    "Invalid parameters for app registration"
#define OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_INVALID_TRACE \
    "[svc.audio]Invalid parameters for app registration"
#define OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_OCCUPIED_MESSAGE \
    "PCM stream is already occupied by app ID %d, unregistering previous app"
#define OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_OCCUPIED_TRACE \
    "[svc.audio]PCM stream is already occupied by app ID %d, unregistering previous app"
#define OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_SUCCESS_MESSAGE \
    "PCM app registered: ID=%d, Source=%d"
#define OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_SUCCESS_TRACE \
    "[svc.audio]PCM app registered: ID=%d, Source=%d"
#define OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_FUNCTION "SVC_PcmAppUnregister"
#define OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_EMPTY_MESSAGE "No PCM app registered"
#define OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_EMPTY_TRACE \
    "[svc.audio]No PCM app registered"
#define OPEN_CFW_PT_FONT_LOG_TAG "font"
#define OPEN_CFW_PT_FONT_LOG_FILE "font_manager.c"
#define OPEN_CFW_PT_FONT_ACQUIRE_FUNCTION "font_xip_acquire"
#define OPEN_CFW_PT_FONT_ACQUIRE_MESSAGE "font mutex acquire failed"
#define OPEN_CFW_PT_FONT_ACQUIRE_TRACE "[font]font mutex acquire failed"
#define OPEN_CFW_PT_FONT_RELEASE_FUNCTION "font_xip_release"
#define OPEN_CFW_PT_FONT_RELEASE_MESSAGE "font mutex release failed"
#define OPEN_CFW_PT_FONT_RELEASE_TRACE "[font]font mutex release failed"
#define OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_MISMATCH_MESSAGE \
    "App ID %d not found, current app ID is %d"
#define OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_MISMATCH_TRACE \
    "[svc.audio]App ID %d not found, current app ID is %d"
#define OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_SUCCESS_MESSAGE \
    "PCM app unregistered: ID=%d"
#define OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_SUCCESS_TRACE \
    "[svc.audio]PCM app unregistered: ID=%d"
#define OPEN_CFW_PT_FAIL_STOP host_fail_stop
#define OPEN_CFW_PT_LENS_SYNC_QUEUE_LINK (&lens_queue_link)
#define OPEN_CFW_PT_LENS_SYNC_EVENT_LINK (&lens_event_link)
#define OPEN_CFW_PT_LENS_SYNC_ALLOCATE host_lens_allocate
#define OPEN_CFW_PT_FILE_HEAP_ALLOCATE host_lens_allocate
#define OPEN_CFW_PT_LENS_SYNC_RELEASE host_lens_release
#define OPEN_CFW_PT_EVENT_FLAGS_SET host_event_flags_set
#define OPEN_CFW_PT_THREAD_FLAGS_SET host_thread_flags_set
#define OPEN_CFW_PT_AUDIO_PATH_TABLE audio_path_table
#define OPEN_CFW_PT_AUDIO_PATH_FORMAT_PROVIDER host_audio_path_format_provider
#define OPEN_CFW_PT_TIME_READ host_time_read
#define OPEN_CFW_PT_SECONDS_TO_TIME host_seconds_to_time
#define OPEN_CFW_PT_RTC_SET_TIME host_rtc_set_time
#define OPEN_CFW_PT_TIME_TO_SECONDS host_time_to_seconds
#define OPEN_CFW_PT_TIME_OUTPUT host_time_output
#define OPEN_CFW_PT_TIME_CONFIGURATION_LINK (&time_configuration_link)
#define OPEN_CFW_PT_AMBIENT_ASSIGN host_ambient_assign
#define OPEN_CFW_PT_AMBIENT_SAMPLE host_ambient_sample
#define OPEN_CFW_PT_AMBIENT_RAW_READ host_ambient_raw_read
#define OPEN_CFW_PT_AMBIENT_BUS_READ host_ambient_bus_read
#define OPEN_CFW_PT_AMBIENT_BUS_WRITE host_ambient_bus_write
#define OPEN_CFW_PT_LENS_SIDE host_lens_side
#define OPEN_CFW_PT_AUDIO_CODEC_ROUTE host_audio_codec_route
#define OPEN_CFW_PT_DELAY_TICKS host_delay_ticks
#define OPEN_CFW_PT_AMBIENT_ROUTE_WORD (&ambient_route_word)
#define OPEN_CFW_PT_AMBIENT_INIT_REGISTER (&ambient_init_register)
#define OPEN_CFW_PT_AMBIENT_RESET_REGISTER (&ambient_reset_register)
#define OPEN_CFW_PT_SYSTEM_RESET_INNER host_system_reset_inner
#define OPEN_CFW_PT_SYSTEM_RESET_CONTROL (&system_reset_control)
#define OPEN_CFW_PT_SYSTEM_RESET_BARRIER() host_system_reset_barrier()
#define OPEN_CFW_PT_SYSTEM_RESET_WAIT() (++system_reset_wait_calls)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_0 host_postprocess_state_0
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_1 host_postprocess_state_1
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_2 host_postprocess_state_2
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_READY (&postprocess_ready)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_ACTIVE (&postprocess_active)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_PRIMARY (&postprocess_primary)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_MODE (&postprocess_mode)
#define OPEN_CFW_PT_TIME_FORMAT_WORD (&time_format_word)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_REFRESH host_postprocess_refresh
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_ONBOARDING host_postprocess_onboarding
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_REMOVE host_postprocess_remove
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_PATH ((const void *)0x1234U)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_COMMIT host_postprocess_commit
#define OPEN_CFW_PT_MRAM_DELETE_ALL_RECORDS host_mram_delete_all
#define OPEN_CFW_PT_PRIVACY_CLEAR host_privacy_clear
#define OPEN_CFW_PT_PAIRING_FLAG_0 (&pairing_flag_0)
#define OPEN_CFW_PT_PAIRING_WORD (&pairing_word)
#define OPEN_CFW_PT_PAIRING_FLAG_1 (&pairing_flag_1)
#define OPEN_CFW_PT_FONT_XIP_START HOST_FONT_XIP_START
#define OPEN_CFW_PT_FONT_XIP_END HOST_FONT_XIP_END
#define OPEN_CFW_PT_FONT_XIP_READ host_font_xip_read
#define OPEN_CFW_PT_FONT_XIP_CONFIGURATION_FLAG (&font_configuration_flag)
#define OPEN_CFW_PT_FONT_XIP_ACTIVE (&font_xip_active)
#define OPEN_CFW_PT_FONT_XIP_MUTEX_LINK (&font_mutex_link)
#define OPEN_CFW_PT_FONT_XIP_DEVICE_LINK (&font_device_link)
#define OPEN_CFW_PT_MSPI_CONTROL host_mspi_control
#define OPEN_CFW_PT_FONT_0_BASE HOST_FONT_0_BASE
#define OPEN_CFW_PT_FONT_1_BASE HOST_FONT_1_BASE
#include "../../components/apollo_main/core_overlay/pt_protocol_lc3_setup.c"
#include "../../components/apollo_main/core_overlay/pt_protocol_board_leaf_candidates.c"


static const struct open_cfw_pt_uled_operations uled_operations = {
    .read_chip_id = host_uled_read_chip_id,
    .set_brightness = host_uled_set_brightness,
    .set_display_offset = host_uled_set_offset,
};


int main(void)
{
    {
        open_cfw_pt_time_record record;
        postprocess_ready = 1U;
        postprocess_active = 2U;
        postprocess_primary = 1U;
        postprocess_mode = 1U;
        assert(open_cfw_pt_display_postprocess_state_0() == 1U);
        assert(open_cfw_pt_display_postprocess_state_1() == 1U);
        assert(open_cfw_pt_display_postprocess_state_2() == 1U);
        postprocess_ready = 0U;
        postprocess_active = 0U;
        postprocess_mode = 2U;
        assert(open_cfw_pt_display_postprocess_state_0() == 0U);
        assert(open_cfw_pt_display_postprocess_state_1() == 0U);
        assert(open_cfw_pt_display_postprocess_state_2() == 0U);
        postprocess_ready = 2U;
        postprocess_active = 1U;
        postprocess_primary = 0U;
        postprocess_mode = 1U;
        assert(open_cfw_pt_display_postprocess_state_0() == 0U);
        assert(open_cfw_pt_display_postprocess_state_1() == 1U);
        assert(open_cfw_pt_display_postprocess_state_2() == 0U);
        postprocess_primary = 1U;
        postprocess_mode = 2U;
        assert(open_cfw_pt_display_postprocess_state_2() == 0U);

        memset(&record, 0xA5, sizeof(record));
        open_cfw_pt_seconds_to_time(0U, &record);
        assert(record.read_error == 0U && record.century_bit == 0U);
        assert(record.year == 0U && record.month == 1U && record.day == 1U);
        open_cfw_pt_seconds_to_time(946684800U, &record);
        assert(record.weekday == 6U);
        assert(record.year == 0U && record.month == 1U && record.day == 1U);
        assert(record.hour == 0U && record.minute == 0U && record.second == 0U);
        assert(open_cfw_pt_time_to_seconds(&record) == 946684800);
        open_cfw_pt_seconds_to_time(951827696U, &record);
        assert(record.year == 0U && record.month == 2U && record.day == 29U);
        assert(record.hour == 12U && record.minute == 34U && record.second == 56U);
        assert(open_cfw_pt_time_to_seconds(&record) == 951827696);
        time_format_word = 1U;
        open_cfw_pt_time_output(951829200, &record);
        assert(record.hour == 1U);
        time_format_word = 0U;
        open_cfw_pt_time_output(951829200, &record);
        assert(record.hour == 13U);
        record.month = 13U;
        assert(open_cfw_pt_time_to_seconds(&record) == 980773200);
        memset(&record, 0, sizeof(record));
        record.month = 1U;
        record.day = 1U;
        assert(open_cfw_pt_time_to_seconds(&record) == 946684800);
        record.hundredths = 49U;
        assert(open_cfw_pt_time_to_seconds(&record) == 946684800);
        record.hundredths = 50U;
        assert(open_cfw_pt_time_to_seconds(&record) == 946684801);
        record.year = 100U;
        record.hundredths = 0U;
        assert(open_cfw_pt_time_to_seconds(&record) == 946684800);
        open_cfw_pt_seconds_to_time(4107542400U, &record);
        assert(record.year == 100U && record.month == 2U && record.day == 29U);
        open_cfw_pt_seconds_to_time(4107628800U, &record);
        assert(record.year == 100U && record.month == 3U && record.day == 1U);
        open_cfw_pt_seconds_to_time(UINT32_MAX, &record);
        assert(record.year == 106U && record.month == 2U && record.day == 6U);
        assert(record.hour == 6U && record.minute == 28U &&
               record.second == 15U);
        assert(open_cfw_pt_time_to_seconds(NULL) == -1);
        open_cfw_pt_seconds_to_time(946684800U, NULL);
        time_format_word = 1U;
        open_cfw_pt_time_output(946684800U, &record);
        assert(record.hour == 12U);
        open_cfw_pt_time_output(946728000U, &record);
        assert(record.hour == 12U);
        open_cfw_pt_time_output(946767600U, &record);
        assert(record.hour == 11U);

        system_reset_control = 0xFFFFFFFFU;
        system_reset_wait_calls = 0U;
        system_reset_barrier_calls = 0U;
        open_cfw_pt_system_reset_inner();
        assert(system_reset_control == 0x05FA0704U);
        assert(system_reset_wait_calls == 1U);
        assert(system_reset_barrier_calls == 2U);
        assert(system_reset_barrier_values[0] == 0xFFFFFFFFU);
        assert(system_reset_barrier_values[1] == 0x05FA0704U);

        {
            struct {
                uint32_t before;
                open_cfw_pt_display_buffer_descriptor descriptor;
                uint32_t after;
            } guarded;
            uint8_t ring[8] = {0xEEU, 0xEEU, 0xEEU, 0xEEU,
                               0xEEU, 0xEEU, 0xEEU, 0xEEU};
            const uint8_t bytes[6] = {0U, 1U, 2U, 3U, 4U, 5U};
            memset(&guarded, 0, sizeof(guarded));
            guarded.before = 0x11223344U;
            guarded.after = 0x55667788U;
            guarded.descriptor.base = ring;
            guarded.descriptor.capacity = sizeof(ring);
            guarded.descriptor.read_index = 2U;
            guarded.descriptor.write_index = 6U;
            guarded.descriptor.callback = host_ring_callback;
            ring_callback_calls = 0U;
            ring_acquire_barriers = 0U;
            ring_release_barriers = 0U;
            ring_callback_write_index = &guarded.descriptor.write_index;
            assert(open_cfw_pt_display_buffer_write(
                       &guarded.descriptor, (uintptr_t)bytes,
                       sizeof(bytes)) == 3U);
            assert(ring[6] == 0U && ring[7] == 1U && ring[0] == 2U);
            assert(ring[1] == 0xEEU && guarded.descriptor.write_index == 1U);
            assert(guarded.before == 0x11223344U &&
                   guarded.after == 0x55667788U);
            assert(ring_acquire_barriers == 1U && ring_release_barriers == 1U);
            assert(ring_callback_calls == 1U);
            assert(ring_callback_descriptor == &guarded.descriptor);
            assert(ring_callback_event == 1U && ring_callback_count == 3U);
            assert(ring_callback_observed_write_index == 1U);
            guarded.descriptor.read_index = 2U;
            guarded.descriptor.write_index = 1U;
            assert(open_cfw_pt_display_buffer_write(
                       &guarded.descriptor, (uintptr_t)bytes, 1U) == 0U);
            guarded.descriptor.read_index = 8U;
            guarded.descriptor.write_index = 0U;
            assert(open_cfw_pt_display_buffer_write(
                       &guarded.descriptor, (uintptr_t)bytes, 1U) == 0U);
            assert(open_cfw_pt_display_buffer_write(
                       NULL, (uintptr_t)bytes, 1U) == 0U);
            assert(open_cfw_pt_display_buffer_write(
                       &guarded.descriptor, 0U, 1U) == 0U);
        }
        allocation_fail_at = 0U;
        allocation_fail_first = 0U;
        allocation_fail_always = 0U;
        allocation_count = 0U;
        delay_call_count = 0U;
        assert(open_cfw_pt_lens_sync_allocate(8U) == allocation_0.bytes);
        assert(allocation_count == 1U && delay_call_count == 0U);
        allocation_count = 0U;
        allocation_fail_first = 3U;
        delay_call_count = 0U;
        delay_ticks = 0U;
        assert(open_cfw_pt_lens_sync_allocate(8U) == allocation_1.bytes);
        assert(allocation_count == 4U && delay_call_count == 3U);
        assert(delay_history[0] == 1U && delay_history[1] == 2U &&
               delay_history[2] == 4U && delay_ticks == 4U);
        allocation_count = 0U;
        allocation_fail_first = 0U;
        allocation_fail_always = 1U;
        delay_call_count = 0U;
        assert(open_cfw_pt_lens_sync_allocate(8U) == NULL);
        assert(allocation_count == 10U && delay_call_count == 10U);
        assert(delay_history[0] == 1U && delay_history[9] == 512U);
        allocation_fail_always = 0U;

        last_message[0] = 9U;
        {
            const uint32_t message[3] = {3U, 4U, 5U};
            input_queue_link = &input_queue_storage;
            input_thread_link = &input_thread_storage;
            direct_queue_result = 0;
            direct_queue_calls = 0U;
            direct_thread_flags = 0U;
            open_cfw_pt_input_message_send(message);
            assert(last_message[0] == 3U && last_message[2] == 5U);
            assert(direct_thread == &input_thread_storage);
            assert(direct_thread_flags == 0x00400000U);
            input_thread_link = NULL;
            direct_thread = &input_thread_storage;
            open_cfw_pt_input_message_send(message);
            assert(direct_thread == NULL &&
                   direct_thread_flags == 0x00400000U);
            input_queue_link = NULL;
            open_cfw_pt_input_message_send(message);
            assert(direct_queue_calls == 2U);
            input_queue_link = &input_queue_storage;
            direct_queue_result = -7;
            direct_thread_flags = 0U;
            input_log_calls = 0U;
            open_cfw_pt_input_message_send(message);
            assert(input_log_calls == 1U && input_log_result == -7);
            assert(direct_thread_flags == 0U);
            open_cfw_pt_input_message_send(NULL);
            assert(direct_queue_calls == 3U);
            input_thread_link = &input_thread_storage;
        }
        direct_queue_result = 0;
        direct_thread_flags = 0U;
        open_cfw_pt_codec_mic_enable(0x101U);
        assert(direct_audio_message[0] == 0U);
        assert(direct_audio_message[1] == 1U);
        assert(direct_audio_message[2] == 1U);
        assert(direct_thread == &audio_thread_storage);
        open_cfw_pt_pdm_mic_enable(0x102U);
        assert(direct_audio_message[0] == 1U);
        assert(direct_audio_message[2] == 2U);
        audio_thread_link = NULL;
        direct_thread = &audio_thread_storage;
        open_cfw_pt_codec_mic_enable(1U);
        assert(direct_thread == NULL && direct_thread_flags == 0x00400000U);
        audio_thread_link = &audio_thread_storage;
        direct_queue_result = -9;
        audio_log_filter = 7U;
        audio_log_filter_calls = 0U;
        audio_structured_log_calls = 0U;
        audio_trace_log_calls = 0U;
        direct_thread_flags = 0U;
        open_cfw_pt_codec_mic_enable(1U);
        assert(audio_structured_log_calls == 1U &&
               audio_trace_log_calls == 1U && audio_log_result == -9);
        assert(audio_log_filter_calls == 2U && direct_thread_flags == 0U);
        audio_queue_link = NULL;
        open_cfw_pt_codec_mic_enable(1U);
        assert(audio_log_filter_calls == 2U);
        audio_queue_link = &audio_queue_storage;
        direct_queue_result = 0;

        {
            char path[32];
            char short_path[5];
            char one_byte_path[1] = {'X'};
            volatile struct open_cfw_pt_audio_registration *registration;
            volatile struct open_cfw_pt_audio_recorder *recorder;
            open_cfw_pt_audio_path_format_provider(0U, 7U, path,
                                                   sizeof(path));
            assert(strcmp(path, "/audio/codec_07.pcm") == 0);
            memset(short_path, 'X', sizeof(short_path));
            open_cfw_pt_audio_path_format_provider(1U, 123U, short_path,
                                                   sizeof(short_path));
            assert(short_path[sizeof(short_path) - 1U] == '\0');
            open_cfw_pt_audio_path_format_provider(1U, UINT16_MAX, path,
                                                   sizeof(path));
            assert(strcmp(path, "/audio/pdm_65535.pcm") == 0);
            open_cfw_pt_audio_path_format_provider(0U, 0U, one_byte_path,
                                                   sizeof(one_byte_path));
            assert(one_byte_path[0] == '\0');
            strcpy(path, "unchanged");
            open_cfw_pt_audio_path_format_provider(2U, 7U, path,
                                                   sizeof(path));
            assert(strcmp(path, "unchanged") == 0);
            memset(audio_registration_storage.bytes, 0,
                   sizeof(audio_registration_storage.bytes));
            registration = OPEN_CFW_PT_AUDIO_REGISTRATION_TABLE;
            audio_log_filter = 7U;
            audio_log_filter_calls = 0U;
            audio_structured_log_calls = 0U;
            audio_trace_log_calls = 0U;
            assert(open_cfw_pt_audio_register(
                       0x10BU, 1U, &audio_single_callback) == 0);
            assert(registration[1].listener == 0x10BU);
            assert(registration[1].mode == 1U);
            assert(registration[1].callback == &audio_single_callback);
            assert(audio_structured_log_calls == 1U &&
                   audio_trace_log_calls == 1U &&
                   audio_log_filter_calls == 2U);
            assert(audio_log_level == 3U && audio_log_line == 0xD0U);
            assert(strcmp(audio_log_function, "SVC_PcmAppRegister") == 0);
            assert(strcmp(audio_log_message,
                          "[svc.audio]PCM app registered: ID=%d, Source=%d") == 0);
            assert(audio_log_argument_count == 2U &&
                   audio_log_arguments[0] == 0x10BU &&
                   audio_log_arguments[1] == 1U);
            assert(audio_trace_flags == 0x0C800000U);
            registration[1].reserved[0] = 0xAAU;
            assert(open_cfw_pt_audio_register(
                       0x20BU, 1U, &audio_stereo_callback) == 0);
            assert(registration[1].listener == 0x20BU);
            assert(registration[1].reserved[0] == 0U);
            assert(registration[1].callback == &audio_stereo_callback);
            assert(audio_structured_log_calls == 3U &&
                   audio_trace_log_calls == 3U &&
                   audio_log_filter_calls == 6U);
            assert(open_cfw_pt_audio_register(0U, 2U,
                       &audio_single_callback) == -1);
            assert(open_cfw_pt_audio_register(0U, 0U, NULL) == -1);
            assert(audio_structured_log_calls == 5U &&
                   audio_trace_log_calls == 5U &&
                   audio_log_filter_calls == 10U);
            assert(audio_log_level == 1U && audio_log_line == 0xBFU &&
                   audio_log_argument_count == 0U);
            assert(audio_trace_flags == 0x04000000U);
            assert(open_cfw_pt_audio_remove(7U, 1U) == -1);
            assert(audio_structured_log_calls == 6U &&
                   audio_trace_log_calls == 6U);
            assert(audio_log_level == 2U && audio_log_line == 0xDDU);
            assert(audio_log_arguments[0] == 7U &&
                   audio_log_arguments[1] == 0x20BU);
            assert(audio_trace_flags == 0x08800000U);
            assert(open_cfw_pt_audio_remove(0x20BU, 1U) == 0);
            assert(registration[1].callback == NULL);
            assert(audio_structured_log_calls == 7U &&
                   audio_trace_log_calls == 7U);
            assert(audio_log_level == 3U && audio_log_line == 0xE1U);
            assert(audio_log_argument_count == 1U &&
                   audio_log_arguments[0] == 0x20BU);
            assert(audio_trace_flags == 0x0C400000U);
            assert(open_cfw_pt_audio_remove(0x20BU, 1U) == 0);
            assert(audio_structured_log_calls == 8U &&
                   audio_trace_log_calls == 8U &&
                   audio_log_filter_calls == 16U);
            assert(audio_log_level == 2U && audio_log_line == 0xD8U &&
                   audio_log_argument_count == 0U);
            assert(audio_trace_flags == 0x08000000U);
            assert(open_cfw_pt_audio_remove(0U, 2U) == -1);
            memset(audio_recorder_storage.bytes, 0,
                   sizeof(audio_recorder_storage.bytes));
            recorder = OPEN_CFW_PT_AUDIO_RECORDER_TABLE;
            recorder[1].file = &direct_audio_file;
            recorder[1].byte_count = 0x11223344U;
            recorder[1].identifier = 0x5566U;
            recorder[1].active = 1U;
            recorder[1].initialized = 0x77U;
            direct_file_close_calls = 0U;
            open_cfw_pt_audio_unregister(1U);
            assert(direct_file_close_calls == 1U);
            assert(recorder[1].file == NULL && recorder[1].active == 0U);
            assert(recorder[1].byte_count == 0x11223344U);
            assert(recorder[1].identifier == 0x5566U &&
                   recorder[1].initialized == 0x77U);
            open_cfw_pt_audio_unregister(1U);
            assert(direct_file_close_calls == 1U);
            open_cfw_pt_audio_unregister(2U);
            assert(direct_file_close_calls == 1U);
        }
        {
            struct open_cfw_pt_ambient_field field = {7U, 4U, 1U};
            ambient_registers[1] = 0xA50FU;
            ambient_bus_write_calls = 0U;
            assert(open_cfw_pt_ambient_raw_read(1U) == 0xA50FU);
            assert(open_cfw_pt_ambient_sample(&field) == 0xA50FU);
            open_cfw_pt_ambient_assign(&field, 3U);
            assert(ambient_registers[1] == 0xA53FU);
            assert(ambient_bus_write_calls == 1U);
            open_cfw_pt_ambient_assign(&field, 3U);
            assert(ambient_bus_write_calls == 1U);
            field.most_significant_bit = 16U;
            open_cfw_pt_ambient_assign(&field, 0U);
            assert(ambient_bus_write_calls == 1U);
        }
        font_configuration_flag = 0U;
        font_xip_active = 1U;
        font_mutex_acquire_result = 0;
        font_mutex_release_result = 0;
        mspi_control_calls = 0U;
        open_cfw_pt_font_xip_acquire();
        assert(mspi_control_calls == 1U && mspi_control_operation == 0U);
        assert(mspi_control_argument == 1U && font_xip_active == 0U);
        open_cfw_pt_font_xip_release();
        assert(mspi_control_calls == 2U && mspi_control_operation == 2U);
        assert(font_xip_active == 1U);
        audio_log_filter = 7U;
        audio_structured_log_calls = 0U;
        audio_trace_log_calls = 0U;
        font_configuration_flag = 1U;
        font_mutex_acquire_result = -1;
        open_cfw_pt_font_xip_acquire();
        assert(audio_structured_log_calls == 1U &&
               audio_trace_log_calls == 1U && audio_log_level == 1U &&
               audio_log_line == 0xC3U &&
               strcmp(audio_log_function, "font_xip_acquire") == 0 &&
               strcmp(audio_log_message,
                      "[font]font mutex acquire failed") == 0 &&
               audio_trace_flags == 0x04000000U &&
               audio_log_argument_count == 0U);
        font_mutex_acquire_result = 0;
        font_mutex_release_result = -1;
        open_cfw_pt_font_xip_release();
        assert(audio_structured_log_calls == 2U &&
               audio_trace_log_calls == 2U && audio_log_level == 1U &&
               audio_log_line == 0xCCU &&
               strcmp(audio_log_function, "font_xip_release") == 0 &&
               strcmp(audio_log_message,
                      "[font]font mutex release failed") == 0 &&
               audio_trace_flags == 0x04000000U &&
               audio_log_argument_count == 0U);
        font_mutex_release_result = 0;
        open_cfw_pt_font_xip_acquire();
        open_cfw_pt_font_xip_release();
        assert(mspi_control_calls == 2U);
        pairing_flag_0 = 1U;
        pairing_word = 0xFFFFFFFFU;
        pairing_flag_1 = 1U;
        mram_delete_all_calls = 0U;
        privacy_clear_calls = 0U;
        open_cfw_pt_display_postprocess_commit();
        assert(mram_delete_all_calls == 1U && privacy_clear_calls == 1U);
        assert(pairing_flag_0 == 0U && pairing_word == 0U &&
               pairing_flag_1 == 0U);
        {
            uint8_t charger_device[0x100] = {0U};
            static const struct open_cfw_pt_device_write_interface writer = {
                .write = host_direct_charger_write,
                .reserved = NULL,
                .context = &direct_charger_configuration,
            };
            static const struct open_cfw_pt_device_read_interface reader = {
                .reserved = NULL,
                .read = host_direct_identifier_read,
                .context = &direct_identifier_value,
            };
            uint8_t identifier = 0U;
            void *handle = open_cfw_pt_charger_open(charger_device, 0U);
            assert(handle == charger_device + 0x8CU);
            assert(open_cfw_pt_charger_open(NULL, 0U) == NULL);
            assert(open_cfw_pt_charger_open(
                       (const void *)(uintptr_t)0x1000U,
                       (uint8_t)0x100U) ==
                   (void *)(uintptr_t)0x108CU);
            assert(open_cfw_pt_charger_open(
                       (const void *)(uintptr_t)0x1000U, 0xFFU) ==
                   (void *)(uintptr_t)0x1884U);
            direct_charger_interface_link = &writer;
            direct_charger_write_calls = 0U;
            assert(open_cfw_pt_charger_enable(handle, 0x0FU) ==
                   (int32_t)0x2BAD0000U);
            assert(direct_charger_write_calls == 2U);
            assert(direct_charger_registers[0] == 0x304U &&
                   direct_charger_registers[1] == 0x307U);
            assert(direct_charger_values[0] == 3U &&
                   direct_charger_values[1] == 3U);
            direct_charger_write_calls = 0U;
            assert(open_cfw_pt_charger_enable(handle, 0xF0U) ==
                   OPEN_CFW_PT_PLATFORM_SUCCESS);
            assert(direct_charger_write_calls == 0U);
            direct_charger_write_calls = 0U;
            assert(open_cfw_pt_charger_disable(handle, 0x0FU) ==
                   (int32_t)0x2BAD0000U);
            assert(direct_charger_registers[0] == 0x305U &&
                   direct_charger_registers[1] == 0x306U);
            assert(open_cfw_pt_hardware_identifier_2_read(
                       &reader, 0x101U, &identifier, 1U) ==
                   (int32_t)0x2BAD0000U);
            assert(identifier == 0x42U);
        }
    }
    assert(open_cfw_pt_board_display_state() == display_state);
    assert(open_cfw_pt_board_codec_platform_identifier() == 0xA1B2C3D4U);

    open_cfw_pt_board_buzzer_start(4000U, 30U);
    assert(buzzer_prepare_calls == 1U);
    assert(buzzer_pwm_stop_calls == 1U);
    assert(buzzer_pin_configure_calls == 1U && buzzer_pin == 0x91U);
    assert(buzzer_script_state == 0U);
    assert(buzzer_active_flag == 0U && buzzer_pending_flag == 0U);
    assert(route_code == 0x91U);
    assert(route_value == 0x55667788U);
    assert(buzzer_frequency == 4000U);
    assert(buzzer_duty == 30U);
    assert(buzzer_pwm_start_calls == 1U);
    open_cfw_pt_board_buzzer_stop();
    assert(buzzer_pwm_stop_calls == 2U);
    assert(buzzer_pin_configure_calls == 2U);

    {
        uint32_t identifier = 0U;
        assert(open_cfw_pt_board_hardware_identifier_0(NULL) == -1);
        assert(open_cfw_pt_board_hardware_identifier_0(&identifier) == 0);
        assert(identifier_selector == 1U);
        assert(identifier == 0xCAFEBABEU);
    }

    {
        uint32_t identifier = 0U;
        assert(open_cfw_pt_board_hardware_identifier_1(NULL) == -1);
        identifier_1_state = 0U;
        identifier_1_initialize_result = -1;
        identifier_1_sequence = 0U;
        assert(open_cfw_pt_board_hardware_identifier_1(&identifier) == -3);
        assert(identifier_1_sequence == 1U);
        identifier_1_initialize_result = 0;
        identifier_1_read_result = 0;
        identifier_1_read_value = 0xAB123456U;
        identifier_1_sequence = 0U;
        assert(open_cfw_pt_board_hardware_identifier_1(&identifier) == 0);
        assert(identifier_1_sequence == 6U);
        assert(identifier == 0x00123456U);
        identifier_1_state = 1U;
        identifier_1_read_result = -1;
        identifier_1_sequence = 0U;
        assert(open_cfw_pt_board_hardware_identifier_1(&identifier) == -2);
        assert(identifier_1_sequence == 6U);
    }

    {
        uint32_t identifier = 0U;
        assert(open_cfw_pt_board_hardware_identifier_2(NULL) == -1);
        identifier_2_result = -7;
        assert(open_cfw_pt_board_hardware_identifier_2(&identifier) == -2);
        identifier_2_result = (int32_t)0x2BAD0000U;
        identifier_2_value = 0U;
        assert(open_cfw_pt_board_hardware_identifier_2(&identifier) == 0);
        assert(identifier == 0x13U);
        identifier_2_value = 0xFFU;
        assert(open_cfw_pt_board_hardware_identifier_2(&identifier) == 0);
        assert(identifier == 0x13U);
        identifier_2_value = 0x42U;
        assert(open_cfw_pt_board_hardware_identifier_2(&identifier) == 0);
        assert(identifier == 0x42U);
    }

    charger_open_result = NULL;
    open_cfw_pt_board_charger_test_disable();
    open_cfw_pt_board_charger_test_enable();
    assert(charger_disable_argument == 0U);
    assert(charger_enable_argument == 0U);
    charger_open_result = &charger_device_storage;
    open_cfw_pt_board_charger_test_disable();
    open_cfw_pt_board_charger_test_enable();
    assert(charger_disable_argument == 0x0FU);
    assert(charger_enable_argument == 0x0FU);

    uart_initialized = 1U;
    memset(uart_device_storage, 0, sizeof(uart_device_storage));
    memset((void *)uart_registers, 0, sizeof(uart_registers));
    uart_device_storage[0] = 0x01EA9E06U;
    uart_device_storage[10] = 0U;
    uart_result = 0;
    uart_registers[0x18U / 4U] = 0U;
    uart_data_barriers = 0U;
    uart_cache_barrier_calls = 0U;
    assert(open_cfw_pt_board_uart_sync_write(display_state, 4U, 100U) == 0);
    assert(uart_registers[0x50U / 4U] == 4U);
    assert(uart_registers[0x4CU / 4U] ==
           (uint32_t)(uintptr_t)uart_tx_buffer);
    assert(uart_registers[0x48U / 4U] == 10U);
    assert(uart_registers[0x44U / 4U] == 0x1821U);
    assert(uart_timeout == 100U);
    assert(memcmp(uart_tx_buffer, display_state, 4U) == 0);
    assert(uart_data_barriers == 1U);
    assert(uart_cache_barrier_calls == 3U);
    assert(uart_cache_barrier_sequence[0] == 1U &&
           uart_cache_barrier_sequence[1] == 1U &&
           uart_cache_barrier_sequence[2] == 2U);
    uart_result = 7;
    assert(open_cfw_pt_board_uart_sync_write(display_state, 4U, 100U) == -1);
    assert(uart_registers[0x48U / 4U] == 0U);
    assert(uart_registers[0x44U / 4U] == 0x1800U);
    assert(uart_data_barriers == 2U);
    assert(uart_cache_barrier_calls == 6U);
    assert(uart_cache_barrier_sequence[3] == 1U &&
           uart_cache_barrier_sequence[4] == 1U &&
           uart_cache_barrier_sequence[5] == 2U);
    uart_result = 0;
    uart_registers[0x18U / 4U] = 8U;
    uart_delay_calls = 0U;
    assert(open_cfw_pt_board_uart_sync_write(display_state, 4U, 0U) == 0);
    assert(uart_delay_calls == 100U);
    assert(uart_data_barriers == 3U);
    assert(uart_cache_barrier_calls == 9U);
    assert(uart_cache_barrier_sequence[6] == 1U &&
           uart_cache_barrier_sequence[7] == 1U &&
           uart_cache_barrier_sequence[8] == 2U);
    assert(open_cfw_pt_uart_status_get(NULL, &uart_timeout) == 2);
    uart_device_storage[0] = 0U;
    assert(open_cfw_pt_uart_status_get(
               uart_device_storage, &uart_timeout) == 2);
    uart_device_storage[0] = 0x01EA9E06U;
    assert(open_cfw_pt_uart_status_get(uart_device_storage, NULL) == 6);
    uart_initialized = 0U;
    assert(open_cfw_pt_board_uart_sync_write(display_state, 4U, 0U) == -1);
    uart_initialized = 1U;

    assert(open_cfw_pt_board_audio_status_get(0U) == &audio_status[0]);
    assert(open_cfw_pt_board_audio_status_get(1U) == &audio_status[1]);
    assert(open_cfw_pt_board_audio_status_get(2U) == &audio_status[2]);
    assert(open_cfw_pt_board_audio_status_get(3U) == &audio_status[0]);

    codec_route_result = 0;
    open_cfw_pt_board_audio_codec_route(0x86U, 1U);
    assert(codec_route_code == 0x86U);
    assert(codec_route_enabled == 1U);
    codec_route_result = 4;
    open_cfw_pt_board_audio_codec_route(9U, 2U);
    assert(codec_route_code == 9U);
    assert(codec_route_enabled == 0U);

    audio_capture_active = 99U;
    open_cfw_pt_board_audio_channel_0_start(0U);
    assert(audio_capture_active == 0U);
    assert(audio_register_listener == 0x10BU);
    assert(audio_register_mode == 0U);
    assert(audio_register_callback == &audio_single_callback);
    assert(codec_mic_enabled == 1U);
    assert(pcm_route_mode == 0U);
    open_cfw_pt_board_audio_channel_0_start(1U);
    assert(audio_register_callback == &audio_stereo_callback);
    audio_register_callback = NULL;
    open_cfw_pt_board_audio_channel_0_start(2U);
    assert(audio_register_callback == NULL);

    open_cfw_pt_board_audio_channel_0_stop();
    assert(audio_register_listener == 0x10BU);
    assert(audio_register_mode == 1U);
    assert(audio_register_callback == &audio_single_callback);
    assert(pdm_mic_enabled == 1U);
    assert(pcm_route_mode == 1U);

    memset(audio_codec_buffer_0.bytes, 0, sizeof(audio_codec_buffer_0.bytes));
    memset(audio_codec_buffer_1.bytes, 0, sizeof(audio_codec_buffer_1.bytes));
    audio_codec_buffer_0.words[1] = 10000U;
    audio_codec_buffer_0.words[2] = 16000U;
    audio_codec_buffer_1.words[1] = 10000U;
    audio_codec_buffer_1.words[2] = 24000U;
    audio_remove_result = 0;
    open_cfw_pt_board_audio_channel_1_start();
    assert(codec_mic_enabled == 0U);
    assert(audio_remove_listener == 0x10BU);
    assert(audio_remove_mode == 0U);
    assert(audio_unregister_mode == 0U);
    assert(audio_codec_buffer_0.words[6] ==
           (uint32_t)(uintptr_t)(audio_codec_buffer_0.bytes + 0x1CU));
    assert(audio_codec_buffer_1.words[6] == 0U);
    audio_remove_result = -1;
    audio_codec_buffer_0.words[6] = 0U;
    open_cfw_pt_board_audio_channel_1_start();
    assert(audio_codec_buffer_0.words[6] == 0U);

    memset(audio_pdm_buffer.bytes, 0, sizeof(audio_pdm_buffer.bytes));
    audio_pdm_buffer.words[1] = 2500U;
    audio_pdm_buffer.words[2] = 48000U;
    audio_remove_result = 0;
    open_cfw_pt_board_audio_channel_1_stop();
    assert(pdm_mic_enabled == 0U);
    assert(audio_remove_mode == 1U);
    assert(audio_unregister_mode == 1U);
    assert(audio_pdm_buffer.words[6] ==
           (uint32_t)(uintptr_t)(audio_pdm_buffer.bytes + 0x1CU));
    open_cfw_pt_audio_encoder_setup(NULL);

    memset(lc3_encoder_storage.bytes, 0xA5,
           sizeof(lc3_encoder_storage.bytes));
    assert(open_cfw_pt_lc3_setup_encoder(
               10000U, 16000U, 0U, lc3_encoder_storage.bytes) ==
           (void *)lc3_encoder_storage.bytes);
    {
        const uint32_t *lc3_words =
            (const uint32_t *)lc3_encoder_storage.bytes;
        unsigned int index;
        assert(lc3_encoder_storage.bytes[0] == 3U);
        assert(lc3_encoder_storage.bytes[1] == 1U);
        assert(lc3_encoder_storage.bytes[2] == 1U);
        for (index = 3U; index < 0x4A0U; ++index)
            assert(lc3_encoder_storage.bytes[index] == 0U);
        assert(lc3_words[0x4A0U / 4U] == 20U);
        assert(lc3_words[0x4A4U / 4U] == 90U);
        assert(lc3_words[0x4A8U / 4U] == 250U);
        for (index = 0x4ACU; index < 0x4ACU + 350U * 4U; ++index)
            assert(lc3_encoder_storage.bytes[index] == 0U);
        assert(lc3_encoder_storage.bytes[0x4ACU + 350U * 4U] == 0xA5U);
    }

    memset(lc3_encoder_storage.bytes, 0xA5,
           sizeof(lc3_encoder_storage.bytes));
    assert(open_cfw_pt_lc3_setup_encoder(
               7500U, 24000U, 48000U, lc3_encoder_storage.bytes) ==
           (void *)lc3_encoder_storage.bytes);
    {
        const uint32_t *lc3_words =
            (const uint32_t *)lc3_encoder_storage.bytes;
        unsigned int index;
        assert(lc3_encoder_storage.bytes[0] == 2U);
        assert(lc3_encoder_storage.bytes[1] == 2U);
        assert(lc3_encoder_storage.bytes[2] == 4U);
        assert(lc3_words[0x4A0U / 4U] == 60U);
        assert(lc3_words[0x4A4U / 4U] == 210U);
        assert(lc3_words[0x4A8U / 4U] == 570U);
        for (index = 0x4ACU; index < 0x4ACU + 846U * 4U; ++index)
            assert(lc3_encoder_storage.bytes[index] == 0U);
        assert(lc3_encoder_storage.bytes[0x4ACU + 846U * 4U] == 0xA5U);
    }
    {
        static const int durations[] = {2500, 5000, 7500, 10000};
        static const int rates[] = {8000, 16000, 24000, 32000, 48000};
        static const size_t expected_sizes[4][5] = {
            {1416U, 1636U, 1856U, 2076U, 2516U},
            {1576U, 1956U, 2336U, 2716U, 3476U},
            {1760U, 2324U, 2888U, 3452U, 4580U},
            {1896U, 2596U, 3296U, 3996U, 5396U},
        };
        unsigned int duration_index;
        unsigned int codec_rate_index;
        int pcm_rate_index;

        for (duration_index = 0U; duration_index < 4U; ++duration_index) {
            for (codec_rate_index = 0U; codec_rate_index < 5U;
                 ++codec_rate_index) {
                for (pcm_rate_index = -1; pcm_rate_index < 5;
                     ++pcm_rate_index) {
                    unsigned int effective_rate_index =
                        pcm_rate_index < 0 ? codec_rate_index :
                        (unsigned int)pcm_rate_index;
                    int pcm_rate = pcm_rate_index < 0 ? 0 :
                        rates[pcm_rate_index];
                    size_t expected =
                        expected_sizes[duration_index][effective_rate_index];
                    void *result;

                    assert(open_cfw_pt_lc3_encoder_size(
                               durations[duration_index],
                               rates[effective_rate_index]) == expected);
                    memset(lc3_encoder_storage.bytes, 0xA5,
                           sizeof(lc3_encoder_storage.bytes));
                    result = open_cfw_pt_lc3_setup_encoder(
                        durations[duration_index], rates[codec_rate_index],
                        pcm_rate, lc3_encoder_storage.bytes);
                    if (codec_rate_index <= effective_rate_index) {
                        assert(result == (void *)lc3_encoder_storage.bytes);
                        assert(lc3_encoder_storage.bytes[0] == duration_index);
                        assert(lc3_encoder_storage.bytes[1] == codec_rate_index);
                        assert(lc3_encoder_storage.bytes[2] ==
                               effective_rate_index);
                        assert(lc3_encoder_storage.bytes[expected] == 0xA5U);

                        memset(lc3_encoder_storage.bytes, 0xA5,
                               sizeof(lc3_encoder_storage.bytes));
                        assert(open_cfw_pt_lc3_setup_encoder_bounded(
                                   durations[duration_index],
                                   rates[codec_rate_index], pcm_rate,
                                   lc3_encoder_storage.bytes, expected) ==
                               (void *)lc3_encoder_storage.bytes);
                        memset(lc3_encoder_storage.bytes, 0xA5,
                               sizeof(lc3_encoder_storage.bytes));
                        assert(open_cfw_pt_lc3_setup_encoder_bounded(
                                   durations[duration_index],
                                   rates[codec_rate_index], pcm_rate,
                                   lc3_encoder_storage.bytes, expected - 1U) ==
                               NULL);
                        assert(lc3_encoder_storage.bytes[0] == 0xA5U);
                    } else {
                        assert(result == NULL);
                        assert(lc3_encoder_storage.bytes[0] == 0xA5U);
                    }
                }
            }
        }
        assert(expected_sizes[3][4] == 5396U);
        assert(open_cfw_pt_lc3_encoder_size(2500, 48000) == 2516U);
        assert(open_cfw_pt_lc3_encoder_size(5000, 24000) == 2336U);
        assert(open_cfw_pt_lc3_encoder_size(10000, 44100) == 0U);
        assert(open_cfw_pt_lc3_encoder_size(10000, 96000) == 0U);
    }
    memset(lc3_encoder_storage.bytes, 0xA5,
           sizeof(lc3_encoder_storage.bytes));
    assert(open_cfw_pt_lc3_setup_encoder(
               10000, 16000, -1, lc3_encoder_storage.bytes) ==
           (void *)lc3_encoder_storage.bytes);
    assert(lc3_encoder_storage.bytes[0] == 3U);
    assert(lc3_encoder_storage.bytes[1] == 1U);
    assert(lc3_encoder_storage.bytes[2] == 1U);
    memset(lc3_encoder_storage.bytes, 0xA5,
           sizeof(lc3_encoder_storage.bytes));
    assert(open_cfw_pt_lc3_setup_encoder(
               9000U, 16000U, 0U, lc3_encoder_storage.bytes) == 0U);
    assert(lc3_encoder_storage.bytes[0] == 0xA5U);
    assert(open_cfw_pt_lc3_setup_encoder(
               -1, 16000, 0, lc3_encoder_storage.bytes) == NULL);
    assert(open_cfw_pt_lc3_setup_encoder(
               10000, -1, 0, lc3_encoder_storage.bytes) == NULL);
    assert(open_cfw_pt_lc3_setup_encoder(
               10000U, 48000U, 16000U, lc3_encoder_storage.bytes) == 0U);
    assert(open_cfw_pt_lc3_setup_encoder(
               10000U, 16000U, 0U, NULL) == 0U);
    assert(open_cfw_pt_lc3_setup_encoder(
               10000, 16000, 0, lc3_encoder_storage.bytes + 1U) == NULL);
    assert(lc3_encoder_storage.bytes[0] == 0xA5U);

    open_cfw_pt_board_display_stage_1(0x11U);
    assert(display_stage_1_word == 0x11U);
    open_cfw_pt_board_display_stage_3(0x22U);
    assert(display_stage_3_word == 0x22U);
    open_cfw_pt_board_display_stage_2(0x30U, 0x40U);
    assert(display_stage_2_first_word == 0x30U);
    assert(display_stage_2_second_word == 0x40U);
    open_cfw_pt_board_display_stage_2(0x31U, 0U);
    open_cfw_pt_board_display_stage_2(0U, 0x41U);
    assert(display_reinitialize_calls == 3U);
    assert(display_apply_calls == 3U);

    uled_operations_link = NULL;
    assert(open_cfw_pt_board_display_hardware_identifier() == 0xFFFFU);
    open_cfw_pt_board_display_brightness(1U, 2U, 3U);
    open_cfw_pt_board_display_offset(4U, 5U);
    uled_operations_link = &uled_operations;
    assert(open_cfw_pt_board_display_hardware_identifier() == 0x4567U);
    uled_brightness_result = 17;
    open_cfw_pt_board_display_brightness(1U, 2U, 3U);
    assert(uled_brightness_arguments[0] == 1U);
    assert(uled_brightness_arguments[1] == 2U);
    assert(uled_brightness_arguments[2] == 3U);
    uled_offset_result = 19;
    open_cfw_pt_board_display_offset(4U, 5U);
    assert(uled_offset_arguments[0] == 4U);
    assert(uled_offset_arguments[1] == 5U);

    display_queue_result = 0;
    open_cfw_pt_board_screen_show(0x1234U, 0x55667788U, 17U);
    assert(display_write_source == (uintptr_t)0x55667788U);
    assert(display_write_length == 17U);
    assert(submitted_display_message[0] == 2U);
    assert(*(uint32_t *)&submitted_display_message[4] == 0x1234U);
    assert(*(uint32_t *)&submitted_display_message[8] == 17U);
    open_cfw_pt_board_screen_hide(7U, 0x11223344U, 0x2800U);
    assert(submitted_display_message[0] == 5U);
    open_cfw_pt_board_screen_show(1U, 2U, 0x2801U);
    display_queue_result = -1;
    open_cfw_pt_board_screen_hide(1U, 2U, 3U);
    assert(fail_stop_calls == 1U);

    {
        static const uint8_t payload[3] = {0xAAU, 0xBBU, 0xCCU};
        struct open_cfw_pt_lens_sync_message *message;
        allocation_count = 0U;
        allocation_fail_at = 0U;
        released_allocation_count = 0U;
        lens_queue_result = 0;
        event_flags = 0U;
        assert(open_cfw_pt_board_lens_sync_send(
                   0x103U, payload, sizeof(payload), 0xAABBCCDDU) == 0);
        message = submitted_lens_message;
        assert(message == (void *)allocation_0.bytes);
        assert(message->user_data == 0xAABBCCDDU);
        assert(message->type == 4U);
        assert(message->payload_length == 11U);
        assert(message->payload[0] == 4U);
        assert(message->payload[1] == 0x0CU);
        assert(message->payload[2] == 0x03U);
        assert(message->payload[3] == 0x01U);
        assert(message->payload[6] == 3U);
        assert(memcmp(message->payload + 8U, payload, sizeof(payload)) == 0);
        assert(event_flags == 2U);

        allocation_count = 0U;
        allocation_fail_at = 2U;
        released_allocation_count = 0U;
        assert(open_cfw_pt_board_lens_sync_send(
                   1U, payload, sizeof(payload), 0U) == -1);
        assert(released_allocation_count == 1U);
        assert(released_allocations[0] == (void *)allocation_0.bytes);

        allocation_count = 0U;
        allocation_fail_at = 0U;
        released_allocation_count = 0U;
        lens_queue_result = -1;
        assert(open_cfw_pt_board_lens_sync_send(
                   1U, payload, sizeof(payload), 0U) == -1);
        assert(released_allocation_count == 2U);
        assert(released_allocations[0] == (void *)allocation_1.bytes);
        assert(released_allocations[1] == (void *)allocation_0.bytes);
        assert(open_cfw_pt_board_lens_sync_send(1U, NULL, 1U, 0U) == -1);

        allocation_count = 0U;
        lens_queue_result = 0;
        assert(open_cfw_pt_board_lens_sync_send(
                   0xFFFFU, font_xip, 0xFFF7U, 0U) == 0);
        message = submitted_lens_message;
        assert(message->payload_length == 0xFFFFU);
        assert(message->payload[2] == 0xFFU);
        assert(message->payload[3] == 0xFFU);
        assert(allocation_count == 2U);

        allocation_count = 0U;
        assert(open_cfw_pt_board_lens_sync_send(
                   1U, font_xip, 0xFFF8U, 0U) == -1);
        assert(open_cfw_pt_board_lens_sync_send(
                   1U, font_xip, 0xFFFFU, 0U) == -1);
        assert(open_cfw_pt_board_lens_sync_send(
                   1U, font_xip, 0x10000U, 0U) == -1);
        assert(open_cfw_pt_board_lens_sync_send(
                   1U, font_xip, UINT32_MAX, 0U) == -1);
        assert(open_cfw_pt_board_lens_sync_send(
                   0x10000U, NULL, 0U, 0U) == -1);
        assert(open_cfw_pt_board_lens_sync_send(
                   UINT32_MAX, NULL, 0U, 0U) == -1);
        assert(allocation_count == 0U);
    }

    audio_path_table[8] = 0x34U;
    audio_path_table[9] = 0x12U;
    audio_path_table[20] = 0x78U;
    audio_path_table[21] = 0x56U;
    open_cfw_pt_board_audio_path_format(1U, (char *)display_state, 4U);
    assert(audio_path_selector == 1U);
    assert(audio_path_identifier == 0x5678U);
    assert(audio_path_output == (char *)display_state);
    assert(audio_path_capacity == 4U);
    audio_path_selector = 0xFFU;
    open_cfw_pt_board_audio_path_format(2U, (char *)display_state, 4U);
    assert(audio_path_selector == 0xFFU);

    time_configuration[8] = (uint8_t)(int8_t)-4;
    open_cfw_pt_board_time_capture(display_state);
    assert(time_output_seconds == 96400);
    assert(time_output_record == display_state);
    time_configuration[8] = 0U;
    open_cfw_pt_board_time_configure(123456U, -7);
    assert(configured_seconds == 123456U);
    assert(rtc_set_calls == 1U);
    assert(time_output_seconds == 100000);

    open_cfw_pt_board_post_input_message_id3();
    assert(last_message[0] == 3U);
    assert(last_message[1] == 0U);
    assert(last_message[2] == 0U);

    open_cfw_pt_board_ambient_identifier_step_1(device);
    assert(last_assign_address == device + 12U);
    assert(last_assign_mode == 3U);
    open_cfw_pt_board_ambient_identifier_step_2(device);
    assert(last_assign_address == device + 9U);
    assert(last_assign_mode == 0U);
    assert(open_cfw_pt_board_ambient_identifier_low(device) == 0x1234U);
    assert(open_cfw_pt_board_ambient_identifier_high(device) == 0x5678U);

    lens_side = 0U;
    assert(open_cfw_pt_board_ambient_read() == -1.0);
    lens_side = 1U;
    ambient_encoded = 0x3002U;
    assert(open_cfw_pt_board_ambient_read() == 16.0);
    ambient_encoded = 0xF001U;
    assert(open_cfw_pt_board_ambient_read() == 32768.0);

    open_cfw_pt_board_ambient_identifier_initialize();
    assert(route_code == 0x86U);
    assert(route_value == 0x11223344U);
    assert(ambient_init_register == 0x40U);
    assert(delay_ticks == 10U);

    route_code = 0U;
    route_value = 0U;
    open_cfw_pt_board_production_reset();
    assert(route_code == 0x86U);
    assert(route_value == 0x11223344U);
    assert(ambient_reset_register == 0x40U);
    open_cfw_pt_board_system_reset();
    assert(system_reset_inner_calls == 1U);
    lens_side = 1U;
    postprocess_state_0 = 1U;
    postprocess_state_1 = 1U;
    postprocess_state_2 = 1U;
    postprocess_send_calls = 0U;
    open_cfw_pt_display_postprocess_send(
        0x12345U, 0x12345678U, 0x23456U, 0xABCDEF01U);
    assert(postprocess_send_calls == 1U);
    assert(postprocess_transport_first == 0x2345U);
    assert(postprocess_transport_second ==
           (const void *)(uintptr_t)0x12345678U);
    assert(postprocess_transport_third == 0x3456U);
    assert(postprocess_transport_fourth == 0xABCDEF01U);
    assert(postprocess_transport_command == 5U);
    assert(postprocess_transport_route == 2U);
    assert(postprocess_transport_auxiliary == 0U);
    postprocess_send_calls = 0U;
    open_cfw_pt_board_display_postprocess();
    assert(postprocess_send_calls == 2U);
    assert(postprocess_refresh_calls == 1U);
    assert(postprocess_onboarding_calls == 1U);
    assert(postprocess_remove_calls == 1U);
    assert(postprocess_commit_calls == 1U);
    assert(delay_ticks == 500U);
    host_font_prepare(HOST_FONT_0_BASE, 1U);
    host_font_prepare(HOST_FONT_1_BASE, 1025U);
    font_xip_read_calls = 0U;
    assert(open_cfw_pt_board_font_crc_check_0() == 0U);
    assert(font_xip_read_calls == 2U);
    font_xip_read_calls = 0U;
    assert(open_cfw_pt_board_font_crc_check_1() == 0U);
    assert(font_xip_read_calls == 3U);
    assert(open_cfw_pt_font_crc_validate(HOST_FONT_XIP_START - 1U) == 1U);
    assert(open_cfw_pt_font_crc_validate(HOST_FONT_XIP_END - 0x45U) == 1U);
    memset(&font_xip[0x200U], 0, 0x46U);
    assert(open_cfw_pt_font_crc_validate(HOST_FONT_XIP_START + 0x200U) == 1U);
    memset(&font_xip[0x300U], 0, 0x46U);
    font_xip[0x340U] = 0xFFU;
    font_xip[0x341U] = 0xFFU;
    font_xip[0x342U] = 0x01U;
    assert(open_cfw_pt_font_crc_validate(HOST_FONT_XIP_START + 0x300U) == 1U);
    font_xip[0x44U] ^= 1U;
    assert(open_cfw_pt_board_font_crc_check_0() == 1U);
    return 0;
}
