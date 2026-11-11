/* Stock 0x6ccc0: HBA input diagnostics after every calculation. */
#include <stddef.h>
#include <stdint.h>
#include "goodix_hba.h"
#include "goodix_log.h"
#include "goodix_mem.h"
#include "../../vendor/goodix_primitives/goodix_primitives.h"
#include "native_processing_teardown.h"

typedef int (*r1_hba_format_fn)(char *, size_t, const char *, ...);
typedef int (*r1_hba_print_fn)(const char *, ...);
typedef void (*r1_hba_write_fn)(char *);

/* The stock binary uses three adjacent RAM cells. The rebuilt image places
 * unrelated state there, so the C registration owns relocatable cells. */
static r1_hba_format_fn volatile hba_formatter;
static r1_hba_print_fn volatile hba_printer;
static r1_hba_write_fn volatile hba_writer;

void goodix_set_sprintFunc(CallbackPrintfUser printer,
                           CallbackSnprintfUser formatter,
                           Callback_GH3X2X_Log writer)
{
    hba_printer = printer;
    hba_formatter = formatter;
    hba_writer = writer;
}

static uint8_t byte_at(const void *base, size_t offset)
{ return *(const volatile uint8_t *)((uintptr_t)base + offset); }
static uint16_t half_at(const void *base, size_t offset)
{ return *(const volatile uint16_t *)((uintptr_t)base + offset); }
static int32_t word_at(const void *base, size_t offset)
{ return *(const volatile int32_t *)((uintptr_t)base + offset); }

static void hba_emit_formatted(void *unused, const char *format,
                               const int32_t *values, size_t count)
{
    (void)unused;
    r1_hba_format_fn formatter = hba_formatter;
    if (formatter != NULL) {
        char message[128] = {0};
        switch (count) {
        case 1: formatter(message, sizeof message, format, values[0]); break;
        case 2: formatter(message, sizeof message, format, values[0], values[1]); break;
        case 3: formatter(message, sizeof message, format,
                          values[0], values[1], values[2]); break;
        default: break;
        }
        hba_writer(message);
    }
}

static void hba_emit_direct(void *unused, const char *format,
                            const int32_t *values, size_t count)
{
    (void)unused;
    r1_hba_print_fn printer = hba_printer;
    if (printer != NULL) {
        switch (count) {
        case 1: printer(format, values[0]); break;
        case 2: printer(format, values[0], values[1]); break;
        case 3: printer(format, values[0], values[1], values[2]); break;
        default: break;
        }
    }
}

static uint32_t hba_memory_available(void *unused)
{ (void)unused; return goodix_mem_get_free_size(); }

void goodix_hba_essential_info_print(goodix_hba_input_rawdata *raw)
{
    const void *context = r1_goodix_native_processing_context;
    goodix_primitives_spo2_diagnostic_configuration configuration = {
        .sample_frequency = half_at(context, 0),
        .timestamp = (uint32_t)word_at(context, 4),
        .mode = byte_at(context, 19),
        .latest_output_time = word_at(context, 20),
        .earliest_output_time = word_at(context, 24),
        .valid_channel_count = byte_at(context, 28),
        .sigma = word_at(context, 32),
        .raw_ppg_scale = word_at(context, 0x148),
        .delay_time = word_at(context, 36),
        .valid_score_scale = word_at(context, 40),
        .last_heart_rate = word_at(context, 0x90),
    };
    goodix_primitives_spo2_diagnostic_input input = {0};
    if (raw != NULL) {
        input.total_channel_count = raw->total_ch_num;
        input.enable_flags = raw->enable_flg;
        input.enable_flag_count = ((size_t)raw->total_ch_num * 3u + 7u) / 8u;
        input.ppg = raw->ppg_rawdata;
        input.ppg_count = raw->total_ch_num;
        input.accelerometer[0] = raw->acc_x;
        input.accelerometer[1] = raw->acc_y;
        input.accelerometer[2] = raw->acc_z;
        input.gyroscope[0] = raw->groy_x;
        input.gyroscope[1] = raw->groy_y;
        input.gyroscope[2] = raw->groy_z;
    }
    goodix_primitives_spo2_diagnostic_plan plan = {
        .formatted_emit = hba_formatter != NULL ? hba_emit_formatted : NULL,
        .direct_emit = hba_printer != NULL ? hba_emit_direct : NULL,
        .memory_available = hba_memory_available,
    };
    (void)goodix_primitives_spo2_input_diagnostics_emit(
        &configuration, raw != NULL ? &input : NULL, &plan);
}
