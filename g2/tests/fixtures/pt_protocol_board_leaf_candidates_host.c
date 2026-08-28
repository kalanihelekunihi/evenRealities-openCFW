/* SPDX-License-Identifier: MIT */
#include <assert.h>
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
static unsigned int buzzer_prepare_calls;
static volatile uint32_t buzzer_route_word = 0x55667788U;
static uint32_t buzzer_frequency;
static uint8_t buzzer_duty;
static uint32_t buzzer_disable_argument;
static uint32_t identifier_selector;
static uint32_t uart_length;
static uint32_t uart_timeout;
static int uart_result;
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
static int32_t time_output_seconds;
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
static void *released_buffers[2];
static unsigned int released_buffer_count;
static const uint8_t audio_single_callback;
static const uint8_t audio_stereo_callback;
static uint8_t audio_codec_buffer_0;
static uint8_t audio_codec_buffer_1;
static uint8_t audio_pdm_buffer;
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
static void *released_allocations[2];
static unsigned int released_allocation_count;
static union { uint64_t align; uint8_t bytes[32]; } allocation_0;
static union { uint64_t align; uint8_t bytes[0x10000]; } allocation_1;
static unsigned int system_reset_inner_calls;
static volatile uint32_t system_reset_control;
static unsigned int system_reset_wait_calls;
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
static unsigned int mram_delete_all_calls;
static unsigned int privacy_clear_calls;
static volatile uint8_t pairing_flag_0;
static volatile uint32_t pairing_word;
static volatile uint8_t pairing_flag_1;
static uint8_t postprocess_state_0;
static uint8_t postprocess_state_1;
static uint8_t postprocess_state_2;
static uint8_t postprocess_ready;
static volatile uint32_t postprocess_active;
static volatile uint32_t postprocess_primary;
static volatile uint32_t postprocess_mode;
static volatile uint32_t time_format_word;
static unsigned int postprocess_send_calls;
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
}


static int host_delay_ticks(uint32_t ticks)
{
    delay_ticks = ticks;
    return 0;
}


static void host_buzzer_prepare(void)
{
    ++buzzer_prepare_calls;
}


static void host_buzzer_apply(uint32_t frequency, uint8_t duty)
{
    buzzer_frequency = frequency;
    buzzer_duty = duty;
}


static void host_buzzer_disable(uint32_t argument)
{
    buzzer_disable_argument = argument;
}


static void host_hardware_identifier_read(uint32_t selector, uint32_t *record)
{
    unsigned int index;
    identifier_selector = selector;
    for (index = 0U; index < 16U; ++index) record[index] = 0U;
    record[0] = 0xCAFEBABEU;
}


static int host_uart_write(const uint8_t *data, uint32_t length,
                           uint32_t timeout)
{
    assert(data != 0);
    uart_length = length;
    uart_timeout = timeout;
    return uart_result;
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


static void host_time_output(int32_t seconds, void *record)
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


static void host_audio_register(uint32_t listener, uint32_t mode,
                                const void *callback)
{
    audio_register_listener = listener;
    audio_register_mode = mode;
    audio_register_callback = callback;
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


static void host_audio_release(void *buffer)
{
    assert(released_buffer_count < 2U);
    released_buffers[released_buffer_count++] = buffer;
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
    assert(mutex == &display_mutex_storage || mutex == &font_mutex_storage);
    assert(timeout == 0xFFFFFFFFU);
    return 0;
}


static int host_mutex_release(void *mutex)
{
    assert(mutex == &display_mutex_storage || mutex == &font_mutex_storage);
    return 0;
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


static void host_display_buffer_write(void *destination, uintptr_t source,
                                      uint32_t length)
{
    assert(destination == display_buffer);
    display_write_source = source;
    display_write_length = length;
}


static int host_queue_send(void *queue, const void *message,
                           uint32_t priority, uint32_t timeout)
{
    assert(priority == 0U);
    if (timeout == 0U) {
        if (queue == &input_queue_storage)
            memcpy(last_message, message, sizeof(last_message));
        else {
            assert(queue == &audio_queue_storage);
            memcpy(direct_audio_message, message, sizeof(direct_audio_message));
        }
        return 0;
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
    if (allocation_fail_at == allocation_count) return NULL;
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
static void host_postprocess_send(uint32_t a, uint32_t b, uint32_t c,
                                  uint32_t d)
{
    assert(a == 0U && b == 0U && c == 0U && d == 0U);
    ++postprocess_send_calls;
}
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
#define OPEN_CFW_PT_BUZZER_PREPARE host_buzzer_prepare
#define OPEN_CFW_PT_BUZZER_ROUTE_WORD (&buzzer_route_word)
#define OPEN_CFW_PT_BUZZER_APPLY host_buzzer_apply
#define OPEN_CFW_PT_BUZZER_DISABLE host_buzzer_disable
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
#define OPEN_CFW_PT_UART_WRITE host_uart_write
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
#define OPEN_CFW_PT_AUDIO_RELEASE host_audio_release
#define OPEN_CFW_PT_AUDIO_CODEC_BUFFER_0 (&audio_codec_buffer_0)
#define OPEN_CFW_PT_AUDIO_CODEC_BUFFER_1 (&audio_codec_buffer_1)
#define OPEN_CFW_PT_AUDIO_PDM_BUFFER (&audio_pdm_buffer)
#define OPEN_CFW_PT_DISPLAY_STAGE_1_WORD (&display_stage_1_word)
#define OPEN_CFW_PT_DISPLAY_STAGE_3_WORD (&display_stage_3_word)
#define OPEN_CFW_PT_DISPLAY_STAGE_2_FIRST_WORD (&display_stage_2_first_word)
#define OPEN_CFW_PT_DISPLAY_STAGE_2_SECOND_WORD (&display_stage_2_second_word)
#define OPEN_CFW_PT_DISPLAY_REINITIALIZE host_display_reinitialize
#define OPEN_CFW_PT_DISPLAY_APPLY host_display_apply
#define OPEN_CFW_PT_ULED_OPERATIONS_LINK (&uled_operations_link)
#define OPEN_CFW_PT_DISPLAY_MUTEX_LINK (&display_mutex_link)
#define OPEN_CFW_PT_DISPLAY_QUEUE_LINK (&display_queue_link)
#define OPEN_CFW_PT_DISPLAY_BUFFER display_buffer
#define OPEN_CFW_PT_MUTEX_ACQUIRE host_mutex_acquire
#define OPEN_CFW_PT_MUTEX_RELEASE host_mutex_release
#define OPEN_CFW_PT_DISPLAY_BUFFER_WRITE host_display_buffer_write
#define OPEN_CFW_PT_QUEUE_SEND host_queue_send
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
#define OPEN_CFW_PT_SYSTEM_RESET_WAIT() (++system_reset_wait_calls)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_0 host_postprocess_state_0
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_1 host_postprocess_state_1
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_2 host_postprocess_state_2
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_READY (&postprocess_ready)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_ACTIVE (&postprocess_active)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_PRIMARY (&postprocess_primary)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_MODE (&postprocess_mode)
#define OPEN_CFW_PT_TIME_FORMAT_WORD (&time_format_word)
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_SEND host_postprocess_send
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
        assert(open_cfw_pt_time_to_seconds(&record) == -1);

        system_reset_control = 0xFFFFFFFFU;
        system_reset_wait_calls = 0U;
        open_cfw_pt_system_reset_inner();
        assert(system_reset_control == 0x05FA0704U);
        assert(system_reset_wait_calls == 1U);

        {
            uint8_t bytes[8] = {0U, 1U, 2U, 3U, 4U, 5U, 6U, 7U};
            open_cfw_pt_display_buffer_write(bytes + 2U,
                                             (uintptr_t)bytes, 6U);
            assert(bytes[2] == 0U && bytes[7] == 5U);
        }
        allocation_count = 0U;
        allocation_fail_at = 1U;
        delay_ticks = 0U;
        assert(open_cfw_pt_lens_sync_allocate(8U) == allocation_1.bytes);
        assert(allocation_count == 2U && delay_ticks == 1U);

        last_message[0] = 9U;
        {
            const uint32_t message[3] = {3U, 4U, 5U};
            direct_thread_flags = 0U;
            open_cfw_pt_input_message_send(message);
            assert(last_message[0] == 3U && last_message[2] == 5U);
            assert(direct_thread == &input_thread_storage);
            assert(direct_thread_flags == 0x00400000U);
        }
        direct_thread_flags = 0U;
        open_cfw_pt_codec_mic_enable(0x101U);
        assert(direct_audio_message[0] == 0U);
        assert(direct_audio_message[1] == 1U);
        assert(direct_audio_message[2] == 1U);
        assert(direct_thread == &audio_thread_storage);
        open_cfw_pt_pdm_mic_enable(0x102U);
        assert(direct_audio_message[0] == 1U);
        assert(direct_audio_message[2] == 2U);

        {
            char path[32];
            char short_path[5];
            volatile struct open_cfw_pt_audio_registration *registration;
            volatile struct open_cfw_pt_audio_recorder *recorder;
            open_cfw_pt_audio_path_format_provider(0U, 7U, path,
                                                   sizeof(path));
            assert(strcmp(path, "/audio/codec_07.pcm") == 0);
            memset(short_path, 'X', sizeof(short_path));
            open_cfw_pt_audio_path_format_provider(1U, 123U, short_path,
                                                   sizeof(short_path));
            assert(short_path[sizeof(short_path) - 1U] == '\0');
            memset(audio_registration_storage.bytes, 0,
                   sizeof(audio_registration_storage.bytes));
            registration = OPEN_CFW_PT_AUDIO_REGISTRATION_TABLE;
            open_cfw_pt_audio_register(0x10BU, 1U, &audio_single_callback);
            assert(registration[1].listener == 0x10BU);
            assert(registration[1].mode == 1U);
            assert(registration[1].callback == &audio_single_callback);
            assert(open_cfw_pt_audio_remove(7U, 1U) == -1);
            assert(open_cfw_pt_audio_remove(0x10BU, 1U) == 0);
            assert(registration[1].callback == NULL);
            memset(audio_recorder_storage.bytes, 0,
                   sizeof(audio_recorder_storage.bytes));
            recorder = OPEN_CFW_PT_AUDIO_RECORDER_TABLE;
            recorder[1].file = &direct_audio_file;
            recorder[1].active = 1U;
            direct_file_close_calls = 0U;
            open_cfw_pt_audio_unregister(1U);
            assert(direct_file_close_calls == 1U);
            assert(recorder[1].file == NULL && recorder[1].active == 0U);
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
        mspi_control_calls = 0U;
        open_cfw_pt_font_xip_acquire();
        assert(mspi_control_calls == 1U && mspi_control_operation == 0U);
        assert(mspi_control_argument == 1U && font_xip_active == 0U);
        open_cfw_pt_font_xip_release();
        assert(mspi_control_calls == 2U && mspi_control_operation == 2U);
        assert(font_xip_active == 1U);
        font_configuration_flag = 1U;
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
    }
    assert(open_cfw_pt_board_display_state() == display_state);
    assert(open_cfw_pt_board_codec_platform_identifier() == 0xA1B2C3D4U);

    open_cfw_pt_board_buzzer_start(4000U, 30U);
    assert(buzzer_prepare_calls == 1U);
    assert(route_code == 0x91U);
    assert(route_value == 0x55667788U);
    assert(buzzer_frequency == 4000U);
    assert(buzzer_duty == 30U);
    open_cfw_pt_board_buzzer_stop();
    assert(buzzer_disable_argument == 1U);

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

    uart_result = 0;
    assert(open_cfw_pt_board_uart_sync_write(display_state, 4U, 100U) == 0);
    assert(uart_length == 4U);
    assert(uart_timeout == 100U);
    uart_result = 7;
    assert(open_cfw_pt_board_uart_sync_write(display_state, 4U, 100U) == -1);

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

    released_buffer_count = 0U;
    audio_remove_result = 0;
    open_cfw_pt_board_audio_channel_1_start();
    assert(codec_mic_enabled == 0U);
    assert(audio_remove_listener == 0x10BU);
    assert(audio_remove_mode == 0U);
    assert(audio_unregister_mode == 0U);
    assert(released_buffer_count == 2U);
    assert(released_buffers[0] == &audio_codec_buffer_0);
    assert(released_buffers[1] == &audio_codec_buffer_1);
    released_buffer_count = 0U;
    audio_remove_result = -1;
    open_cfw_pt_board_audio_channel_1_start();
    assert(released_buffer_count == 0U);

    released_buffer_count = 0U;
    audio_remove_result = 0;
    open_cfw_pt_board_audio_channel_1_stop();
    assert(pdm_mic_enabled == 0U);
    assert(audio_remove_mode == 1U);
    assert(audio_unregister_mode == 1U);
    assert(released_buffer_count == 1U);
    assert(released_buffers[0] == &audio_pdm_buffer);

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
