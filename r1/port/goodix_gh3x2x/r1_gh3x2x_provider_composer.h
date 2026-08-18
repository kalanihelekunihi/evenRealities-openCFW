#ifndef R1_GH3X2X_PROVIDER_COMPOSER_H
#define R1_GH3X2X_PROVIDER_COMPOSER_H

/*
 * Transparent composition of the three recovered R1 biometric wrappers.
 *
 * The democode ABI consumes one generic provider, while the recovered retail
 * wrappers have distinct input construction and result-publication rules.
 * This layer owns those proven wrapper rules.  Stateful HBA, HRV, and SpO2
 * roots remain explicit bindings; a target must not advertise a function
 * until its complete root binding is present.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "r1_gh3x2x_algo_bridge.h"

#define R1_GH3X2X_PUBLIC_RESULT_WORDS 6u
#define R1_GH3X2X_HR_RESULT_MASK UINT16_C(0x003f)
#define R1_GH3X2X_HRV_RESULT_MASK UINT16_C(0x007f)
#define R1_GH3X2X_SPO2_RESULT_MASK UINT16_C(0x00ff)

typedef enum {
    R1_GH3X2X_ROOT_ERROR = -1,
    R1_GH3X2X_ROOT_NO_UPDATE = 0,
    R1_GH3X2X_ROOT_UPDATE = 1,
} r1_gh3x2x_root_status;

typedef bool (*r1_gh3x2x_root_initialize_fn)(
    void *context, const r1_gh3x2x_algo_frame *frame);
typedef r1_gh3x2x_root_status (*r1_gh3x2x_root_process_fn)(
    void *context, const r1_gh3x2x_algo_input *input,
    int32_t output[R1_GH3X2X_PUBLIC_RESULT_WORDS]);
typedef bool (*r1_gh3x2x_root_deinitialize_fn)(void *context);
typedef bool (*r1_gh3x2x_root_version_fn)(
    void *context, char *destination, size_t destination_size);

typedef struct {
    void *context;
    r1_gh3x2x_root_initialize_fn initialize;
    r1_gh3x2x_root_process_fn process;
    r1_gh3x2x_root_deinitialize_fn deinitialize;
    r1_gh3x2x_root_version_fn version;
} r1_gh3x2x_root_binding;

typedef struct {
    void *context;
    void (*sensor_enable)(void *context, bool accelerometer,
                          bool capacitive, bool temperature);
    bool (*write_virtual_register)(void *context, uint16_t address,
                                   uint16_t value);
} r1_gh3x2x_provider_control;

typedef struct {
    r1_gh3x2x_root_binding hr;
    r1_gh3x2x_root_binding hrv;
    r1_gh3x2x_root_binding spo2;
    r1_gh3x2x_provider_control control;
    uint32_t supported_functions;
    uint32_t initialized_functions;
    uint8_t last_hr;
    uint8_t scene;
    uint8_t sleep_flag;
} r1_gh3x2x_provider_composer;

void r1_gh3x2x_provider_composer_initialize(
    r1_gh3x2x_provider_composer *composer);

/* Only HR, HRV, and SpO2 offsets are admitted. A binding is complete only
 * when all four lifecycle callbacks are present. Replacing a binding while
 * that function is initialized is rejected. */
bool r1_gh3x2x_provider_composer_bind_root(
    r1_gh3x2x_provider_composer *composer, uint8_t function_offset,
    const r1_gh3x2x_root_binding *binding);
void r1_gh3x2x_provider_composer_bind_control(
    r1_gh3x2x_provider_composer *composer,
    const r1_gh3x2x_provider_control *control);
void r1_gh3x2x_provider_composer_set_mode(
    r1_gh3x2x_provider_composer *composer, uint8_t scene,
    uint8_t sleep_flag);

/* Builds the copy-bind table consumed by r1_gh3x2x_algo_bind_provider().
 * Returns false when no complete root is configured. */
bool r1_gh3x2x_provider_composer_build(
    r1_gh3x2x_provider_composer *composer,
    r1_gh3x2x_algo_provider *provider);

#endif
