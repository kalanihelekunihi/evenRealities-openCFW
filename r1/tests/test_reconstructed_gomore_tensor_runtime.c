#include <assert.h>
#include <stddef.h>
#include <stdint.h>

#include "gomore_tensor_runtime/gomore_tensor_runtime.h"

static float plus_one(float value) {
    return value + 1.0f;
}

static float positive_exp_fixture(float value) {
    return value + 2.0f;
}

static float dequantize_half(int16_t value) {
    return (float)value * 0.5f;
}

void test_reconstructed_gomore_tensor_runtime(void) {
    const float source[3] = {-2.0f, 0.0f, 3.0f};
    float output[3] = {0.0f, 0.0f, 0.0f};
    assert(gomore_tensor_map(source, output, 3u, plus_one));
    assert(output[0] == -1.0f && output[1] == 1.0f && output[2] == 4.0f);

    const float right[3] = {2.0f, 4.0f, -1.0f};
    assert(gomore_tensor_multiply(source, right, output, 3u));
    assert(output[0] == -4.0f && output[1] == 0.0f && output[2] == -3.0f);
    assert(gomore_tensor_leaky_relu(source, output, 3u, 0.25f));
    assert(output[0] == -0.5f && output[1] == 0.0f && output[2] == 3.0f);

    const float logits[2] = {0.0f, 2.0f};
    float probabilities[2] = {0.0f, 0.0f};
    assert(gomore_tensor_softmax(logits, probabilities, 2u,
                                 positive_exp_fixture));
    assert(probabilities[0] == (2.0f / 6.0f));
    assert(probabilities[1] == (4.0f / 6.0f));

    const int16_t bias[3] = {2, -4, 6};
    assert(gomore_tensor_dequant_bias_add(source, bias, output, 3u,
                                          dequantize_half));
    assert(output[0] == -1.0f && output[1] == -2.0f && output[2] == 6.0f);

    const int8_t weights[6] = {1, 2, -1, 3, 0, 2};
    const float input[3] = {2.0f, 1.0f, 4.0f};
    float dot[2] = {0.0f, 0.0f};
    assert(gomore_tensor_int8_float_dot(weights, 2u, 3u, 0.5f,
                                        input, dot));
    assert(dot[0] == 0.0f && dot[1] == 7.0f);

    assert(gomore_tensor_map(NULL, NULL, 0u, plus_one));
    assert(!gomore_tensor_map(NULL, output, 1u, plus_one));
    assert(!gomore_tensor_softmax(source, output, 3u, NULL));
}
