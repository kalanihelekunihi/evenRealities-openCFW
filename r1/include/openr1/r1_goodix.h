#ifndef OPENR1_R1_GOODIX_H
#define OPENR1_R1_GOODIX_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

/*
 * Clean-room product adapter for the proprietary Goodix GH3X2X boundary.
 *
 * The numeric masks are recovered R1 interface values.  Their vendor-private
 * algorithm meaning is intentionally not guessed here.  A licensed provider
 * must implement the operations below; openR1 never synthesizes biometric
 * results when that provider is absent.
 */
#define R1_GOODIX_MASK_STOCK_2000 UINT32_C(0x00002000)
#define R1_GOODIX_MASK_STOCK_4000 UINT32_C(0x00004000)
#define R1_GOODIX_MASK_SWITCH_CLEAR UINT32_C(0x00000042)
#define R1_GOODIX_MASK_SWITCH_2 UINT32_C(0x00000002)
#define R1_GOODIX_MASK_SWITCH_40 UINT32_C(0x00000040)
#define R1_GOODIX_DIAGNOSTIC_SNAPSHOT_BYTES 240u
#define R1_GOODIX_DIAGNOSTIC_REFRESH_TICKS UINT32_C(500)
#define R1_GOODIX_DIAGNOSTIC_OUTPUT_MAX 124u
#define R1_SENSOR_STREAM_REGISTRATION_COUNT 8u
#define R1_SENSOR_STREAM_CALLBACK_COUNT 8u
#define R1_SENSOR_STREAM_STATE_BYTES 240u
#define R1_GOODIX_RAW_HR_RECORD_BYTES 124u
#define R1_GOODIX_RAW_HR_VALUE_CAPACITY 30u
#define R1_GOODIX_ADT_RECORD_BYTES 24u
#define R1_GOODIX_ADT_VALUE_CAPACITY 5u
#define R1_GOODIX_WEAR_RECORD_BYTES 2u

typedef enum {
    R1_GOODIX_STOCK_PROFILE_2000 = 0,
    R1_GOODIX_STOCK_PROFILE_4000 = 1
} r1_goodix_stock_profile;

typedef enum {
    R1_GOODIX_SWITCH_PROFILE_2 = 0,
    R1_GOODIX_SWITCH_PROFILE_40 = 1
} r1_goodix_switch_selection;

typedef struct {
    int32_t (*initialize)(void *context);
    int32_t (*switch_configuration)(void *context, uint8_t configuration);
    int32_t (*start_sampling)(void *context, uint32_t mask);
    int32_t (*stop_sampling)(void *context, uint32_t mask);
} r1_goodix_provider_ops;

typedef struct {
    bool (*prepare)(void *context);
    void (*shutdown)(void *context);
    void (*delay_ms)(void *context, uint32_t milliseconds);
} r1_goodix_board_ops;

typedef struct {
    const r1_goodix_provider_ops *provider;
    void *provider_context;
    const r1_goodix_board_ops *board;
    void *board_context;
    uint32_t active_mask;
    bool initialized;
    bool prepared;
} r1_goodix_adapter;

/* Product-owned registration metadata recovered at 0x00089eec. Callback
 * implementations and the generic stream registry remain provider-owned. */
typedef struct {
    const char *name;
    uint16_t payload_bytes;
    uint8_t type;
    bool enabled;
} r1_sensor_stream_registration;

typedef struct {
    bool initialize_goodix;
    bool clear_state;
    size_t clear_bytes;
    size_t callback_count;
    r1_sensor_stream_registration
        registrations[R1_SENSOR_STREAM_REGISTRATION_COUNT];
} r1_sensor_stream_registration_plan_result;

void r1_goodix_adapter_initialize(r1_goodix_adapter *adapter);
r1_error r1_goodix_adapter_bind(r1_goodix_adapter *adapter,
                                const r1_goodix_provider_ops *provider,
                                void *provider_context,
                                const r1_goodix_board_ops *board,
                                void *board_context);
r1_error r1_goodix_start_stock_profile(r1_goodix_adapter *adapter,
                                       r1_goodix_stock_profile profile);
r1_error r1_goodix_switch_profile(r1_goodix_adapter *adapter,
                                  r1_goodix_switch_selection profile);
r1_error r1_goodix_stop_stock_profiles(r1_goodix_adapter *adapter);
bool r1_goodix_provider_available(const r1_goodix_adapter *adapter);
bool r1_goodix_diagnostic_refresh_due(uint32_t now_tick,
                                      uint32_t previous_refresh_tick);
r1_error r1_goodix_diagnostic_select(
    uint8_t snapshot[R1_GOODIX_DIAGNOSTIC_SNAPSHOT_BYTES], uint8_t selector,
    uint8_t *output, size_t output_capacity, size_t *written);
r1_error r1_sensor_stream_registration_plan(
    r1_sensor_stream_registration_plan_result *plan);
/* Exact internal raw_hr producer at 0x0008A01C. The 124-byte record is a
 * count byte, three preserved reserved bytes, and up to thirty UInt32LE
 * values. Values intentionally remain unlabeled pending hardware capture. */
bool r1_goodix_raw_hr_append(
    uint8_t record[R1_GOODIX_RAW_HR_RECORD_BYTES], uint32_t value);
/* Exact internal adt producer at 0x00089E30. Its record uses the same
 * count/reserved/UInt32LE shape as raw_hr with a five-value capacity. */
bool r1_goodix_adt_append(
    uint8_t record[R1_GOODIX_ADT_RECORD_BYTES], uint32_t value);
/* Exact internal wear producer at 0x0008A054. Byte 0 is the pending flag and
 * byte 1 is the Goodix living-object value; this is not the fused wear state. */
void r1_goodix_wear_living_object_update(
    uint8_t record[R1_GOODIX_WEAR_RECORD_BYTES], uint8_t value);

/*
 * Integrator glue around the Goodix goodix_mem/GdMem pool manager.
 *
 * The GH3X2X SDK declares Gh3x2xPoolIsNotEnough() as an integrator-supplied
 * callback.  The recovered stock body at 0x0002E952 logs
 * "sensor_algo_mem_fatal, info1: %u", flushes the log, and never returns.
 * The clean-room seam records the redacted diagnostic first and defers the
 * terminal action to the platform halt hook, which is not expected to return
 * on target; the portable implementation itself contains no busy loop.
 */
typedef struct {
    void (*record)(void *context, uint32_t info1);
    void (*halt)(void *context);
    void *context;
} r1_goodix_pool_fatal_ops;

/*
 * Zero-fill used when clearing the provider pool region.  The recovered
 * 12-byte body at 0x00092B60 is the product byte-fill that the Goodix
 * goodix_mem_init path thunks into; the clean-room equivalent is an explicit
 * zero loop (the freestanding target has no C library headers) behind a
 * NULL-safe wrapper.
 */
void r1_goodix_pool_fill(void *destination, size_t length);
void r1_goodix_pool_not_enough(const r1_goodix_pool_fatal_ops *ops,
                               uint32_t info1);

#endif
