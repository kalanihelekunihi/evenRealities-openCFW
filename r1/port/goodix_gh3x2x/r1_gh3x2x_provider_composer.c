#include "r1_gh3x2x_provider_composer.h"

static uint32_t function_mask(uint8_t offset) {
    return (uint32_t)1u << offset;
}

static bool supported_offset(uint8_t offset) {
    return offset == R1_GH3X2X_ALGO_FUNCTION_HR ||
        offset == R1_GH3X2X_ALGO_FUNCTION_HRV ||
        offset == R1_GH3X2X_ALGO_FUNCTION_SPO2;
}

static bool root_complete(const r1_gh3x2x_root_binding *root) {
    return root != NULL && root->initialize != NULL &&
        root->process != NULL && root->deinitialize != NULL &&
        root->version != NULL;
}

static r1_gh3x2x_root_binding *root_for_offset(
    r1_gh3x2x_provider_composer *composer, uint8_t offset) {
    if (composer == NULL) {
        return NULL;
    }
    if (offset == R1_GH3X2X_ALGO_FUNCTION_HR) {
        return &composer->hr;
    }
    if (offset == R1_GH3X2X_ALGO_FUNCTION_HRV) {
        return &composer->hrv;
    }
    if (offset == R1_GH3X2X_ALGO_FUNCTION_SPO2) {
        return &composer->spo2;
    }
    return NULL;
}

static const r1_gh3x2x_root_binding *const_root_for_offset(
    const r1_gh3x2x_provider_composer *composer, uint8_t offset) {
    if (composer == NULL) {
        return NULL;
    }
    if (offset == R1_GH3X2X_ALGO_FUNCTION_HR) {
        return &composer->hr;
    }
    if (offset == R1_GH3X2X_ALGO_FUNCTION_HRV) {
        return &composer->hrv;
    }
    if (offset == R1_GH3X2X_ALGO_FUNCTION_SPO2) {
        return &composer->spo2;
    }
    return NULL;
}

static uint32_t complete_root_mask(
    const r1_gh3x2x_provider_composer *composer) {
    uint32_t mask = 0u;
    if (composer != NULL && root_complete(&composer->hr)) {
        mask |= function_mask(R1_GH3X2X_ALGO_FUNCTION_HR);
    }
    if (composer != NULL && root_complete(&composer->hrv)) {
        mask |= function_mask(R1_GH3X2X_ALGO_FUNCTION_HRV);
    }
    if (composer != NULL && root_complete(&composer->spo2)) {
        mask |= function_mask(R1_GH3X2X_ALGO_FUNCTION_SPO2);
    }
    return mask;
}

void r1_gh3x2x_provider_composer_initialize(
    r1_gh3x2x_provider_composer *composer) {
    if (composer != NULL) {
        *composer = (r1_gh3x2x_provider_composer){0};
    }
}

bool r1_gh3x2x_provider_composer_bind_root(
    r1_gh3x2x_provider_composer *composer, uint8_t function_offset,
    const r1_gh3x2x_root_binding *binding) {
    if (composer == NULL || !supported_offset(function_offset) ||
        !root_complete(binding) ||
        (composer->initialized_functions & function_mask(function_offset)) !=
            0u) {
        return false;
    }
    r1_gh3x2x_root_binding *destination =
        root_for_offset(composer, function_offset);
    if (destination == NULL) {
        return false;
    }
    *destination = *binding;
    composer->supported_functions |= function_mask(function_offset);
    return true;
}

void r1_gh3x2x_provider_composer_bind_control(
    r1_gh3x2x_provider_composer *composer,
    const r1_gh3x2x_provider_control *control) {
    if (composer == NULL) {
        return;
    }
    composer->control = control != NULL
        ? *control : (r1_gh3x2x_provider_control){0};
}

void r1_gh3x2x_provider_composer_set_mode(
    r1_gh3x2x_provider_composer *composer, uint8_t scene,
    uint8_t sleep_flag) {
    if (composer == NULL) {
        return;
    }
    composer->scene = scene;
    composer->sleep_flag = sleep_flag;
}

static bool composer_initialize_root(
    void *context, const r1_gh3x2x_algo_frame *frame) {
    r1_gh3x2x_provider_composer *composer = context;
    if (composer == NULL || frame == NULL ||
        !supported_offset(frame->function_offset) ||
        frame->function_mask != function_mask(frame->function_offset) ||
        (composer->initialized_functions & frame->function_mask) != 0u) {
        return false;
    }
    r1_gh3x2x_root_binding *root =
        root_for_offset(composer, frame->function_offset);
    if (!root_complete(root) || !root->initialize(root->context, frame)) {
        return false;
    }
    composer->initialized_functions |= frame->function_mask;
    if (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_HRV) {
        composer->last_hr = 0u;
    }
    return true;
}

static bool prepare_input(r1_gh3x2x_provider_composer *composer,
                          const r1_gh3x2x_algo_frame *frame,
                          r1_gh3x2x_algo_input *input) {
    if (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_HR) {
        uint8_t channel_map[R1_GH3X2X_ALGO_INPUT_CHANNELS];
        return r1_gh3x2x_algo_hr_default_channel_map(channel_map) &&
            r1_gh3x2x_algo_prepare_hr_mapped_input(
                frame, channel_map, composer->scene,
                composer->sleep_flag, input);
    }
    if (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_HRV) {
        return r1_gh3x2x_algo_prepare_hrv_input(
            frame, composer->last_hr, composer->sleep_flag, input);
    }
    if (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_SPO2) {
        uint8_t channel_map[R1_GH3X2X_ALGO_INPUT_CHANNELS];
        return r1_gh3x2x_algo_spo2_default_channel_map(channel_map) &&
            r1_gh3x2x_algo_prepare_spo2_input(
                frame, channel_map, composer->sleep_flag, input);
    }
    return false;
}

static uint16_t result_mask(uint8_t offset) {
    if (offset == R1_GH3X2X_ALGO_FUNCTION_HR) {
        return R1_GH3X2X_HR_RESULT_MASK;
    }
    if (offset == R1_GH3X2X_ALGO_FUNCTION_HRV) {
        return R1_GH3X2X_HRV_RESULT_MASK;
    }
    if (offset == R1_GH3X2X_ALGO_FUNCTION_SPO2) {
        return R1_GH3X2X_SPO2_RESULT_MASK;
    }
    return 0u;
}

static bool composer_process_root(void *context,
                                  const r1_gh3x2x_algo_frame *frame,
                                  r1_gh3x2x_algo_result *result) {
    r1_gh3x2x_provider_composer *composer = context;
    if (composer == NULL || frame == NULL || result == NULL ||
        !supported_offset(frame->function_offset) ||
        frame->function_mask != function_mask(frame->function_offset) ||
        (composer->initialized_functions & frame->function_mask) == 0u) {
        return false;
    }
    const r1_gh3x2x_root_binding *root =
        const_root_for_offset(composer, frame->function_offset);
    if (!root_complete(root)) {
        return false;
    }

    r1_gh3x2x_algo_input input;
    if (!prepare_input(composer, frame, &input)) {
        return false;
    }
    int32_t public_output[R1_GH3X2X_PUBLIC_RESULT_WORDS] = {0};
    const r1_gh3x2x_root_status status = root->process(
        root->context, &input, public_output);
    if (status == R1_GH3X2X_ROOT_ERROR) {
        return false;
    }
    *result = (r1_gh3x2x_algo_result){0};
    if (status == R1_GH3X2X_ROOT_NO_UPDATE) {
        return true;
    }
    if (status != R1_GH3X2X_ROOT_UPDATE) {
        return false;
    }
    result->updated = true;
    result->value_mask = result_mask(frame->function_offset);
    result->value_count = frame->function_offset ==
            R1_GH3X2X_ALGO_FUNCTION_HR ? 6u :
        (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_HRV ? 7u : 8u);
    for (size_t index = 0u; index < R1_GH3X2X_PUBLIC_RESULT_WORDS;
         ++index) {
        result->values[index] = public_output[index];
    }
    /* Retail HRV sets bit 6 but writes only words 0..5. Retail R1 SpO2
     * differs from the public democode: it sets bits 0..7, mirrors word 0
     * into word 6, and leaves word 7 zero in the cleared result record. */
    if (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_HRV) {
        result->values[6] = 0;
    } else if (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_SPO2) {
        result->values[6] = result->values[0];
        result->values[7] = 0;
    }
    if (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_HR) {
        composer->last_hr = (uint8_t)public_output[0];
    }
    return true;
}

static bool composer_deinitialize_root(void *context,
                                       uint32_t requested_function_mask,
                                       uint8_t function_offset) {
    r1_gh3x2x_provider_composer *composer = context;
    if (composer == NULL || !supported_offset(function_offset)) {
        return false;
    }
    const uint32_t expected_mask = function_mask(function_offset);
    if (requested_function_mask != expected_mask ||
        (composer->initialized_functions & expected_mask) == 0u) {
        return false;
    }
    r1_gh3x2x_root_binding *root =
        root_for_offset(composer, function_offset);
    if (!root_complete(root) || !root->deinitialize(root->context)) {
        return false;
    }
    composer->initialized_functions &= ~expected_mask;
    return true;
}

static bool composer_version(void *context, uint8_t function_offset,
                             char *destination, size_t destination_size) {
    r1_gh3x2x_provider_composer *composer = context;
    const r1_gh3x2x_root_binding *root =
        const_root_for_offset(composer, function_offset);
    return root_complete(root) && destination != NULL &&
        destination_size != 0u &&
        root->version(root->context, destination, destination_size);
}

static void composer_sensor_enable(void *context, bool accelerometer,
                                   bool capacitive, bool temperature) {
    r1_gh3x2x_provider_composer *composer = context;
    if (composer != NULL && composer->control.sensor_enable != NULL) {
        composer->control.sensor_enable(
            composer->control.context, accelerometer, capacitive,
            temperature);
    }
}

static bool composer_write_virtual_register(void *context,
                                            uint16_t address,
                                            uint16_t value) {
    r1_gh3x2x_provider_composer *composer = context;
    return composer != NULL &&
        composer->control.write_virtual_register != NULL &&
        composer->control.write_virtual_register(
            composer->control.context, address, value);
}

bool r1_gh3x2x_provider_composer_build(
    r1_gh3x2x_provider_composer *composer,
    r1_gh3x2x_algo_provider *provider) {
    if (composer == NULL || provider == NULL) {
        return false;
    }
    const uint32_t complete_mask = complete_root_mask(composer);
    if (complete_mask == 0u ||
        composer->supported_functions != complete_mask ||
        composer->initialized_functions != 0u) {
        return false;
    }
    *provider = (r1_gh3x2x_algo_provider){
        .context = composer,
        .supported_functions = composer->supported_functions,
        .initialize = composer_initialize_root,
        .process = composer_process_root,
        .deinitialize = composer_deinitialize_root,
        .version = composer_version,
        .sensor_enable = composer_sensor_enable,
        .write_virtual_register = composer_write_virtual_register,
    };
    return true;
}
