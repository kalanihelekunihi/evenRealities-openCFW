#include <stdint.h>

/* Stock codec.host wrapper contracts, with driver and log providers explicit. */
extern uint32_t audio_log_flags(void);
extern int32_t audio_dmic_request(uint32_t enable, uint16_t *response, uint32_t timeout);
extern int32_t audio_i2s_output_request(uint32_t enable, uint8_t *response, uint32_t timeout);
extern void audio_log_extended(uint32_t level, const char *module, const char *file,
                               const char *function, uint32_t line,
                               const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format, const char *copy, ...);

static const char module[] = "codec.host";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c";

static int32_t dmic_control(uint32_t enable, uint32_t failure_line,
                            uint32_t success_line, const char *function,
                            const char *failure, const char *success,
                            const char *simple_failure, const char *simple_success) {
    uint16_t response = 0;
    int32_t status = audio_dmic_request(enable, &response, 200);
    if (status != 0 || response != 1) {
        if (audio_log_flags() & 2)
            audio_log_extended(1, module, file, function, failure_line,
                               failure, status, (uint32_t)response);
        if ((audio_log_flags() & 1) || (audio_log_flags() & 4))
            audio_log_simple(0x04800000, simple_failure, simple_failure,
                             status, (uint32_t)response);
        return status ? status : -1;
    }
    if (audio_log_flags() & 2)
        audio_log_extended(3, module, file, function, success_line, success);
    if ((audio_log_flags() & 1) || (audio_log_flags() & 4))
        audio_log_simple(0x0c000000, simple_success, simple_success);
    return 0;
}

/* Stock 0x57D6B4 (SVC_CodecDMICOpen) */
int32_t audio_dsp_enable(void) {
    return dmic_control(1, 811, 814, "SVC_CodecDMICOpen",
                        "DMICOpen failed: %d, rsp=0x%04X", "DMICOpen success",
                        "[codec.host]DMICOpen failed: %d, rsp=0x%04X",
                        "[codec.host]DMICOpen success");
}

/* Stock 0x57D794 (SVC_CodecDMICClose) */
int32_t audio_dsp_disable(void) {
    return dmic_control(0, 823, 826, "SVC_CodecDMICClose",
                        "DMICClose failed: %d, rsp=0x%04X", "DMICClose success",
                        "[codec.host]DMICClose failed: %d, rsp=0x%04X",
                        "[codec.host]DMICClose success");
}

/* Stock 0x57D93C (SVC_I2SOutputCtrl) */
int32_t audio_dsp_gate(uint32_t enable) {
    uint8_t response = 0;
    uint8_t selected = (uint8_t)enable;
    int32_t status = audio_i2s_output_request(selected, &response, 200);
    if (status != 0 || response != 1) {
        if (audio_log_flags() & 2)
            audio_log_extended(1, module, file, "SVC_I2SOutputCtrl", 856,
                               "I2SOutputCtrl failed: %d, rsp=0x%02X",
                               status, (uint32_t)response);
        if ((audio_log_flags() & 1) || (audio_log_flags() & 4))
            audio_log_simple(0x04800000,
                             "[codec.host]I2SOutputCtrl failed: %d, rsp=0x%02X",
                             "[codec.host]I2SOutputCtrl failed: %d, rsp=0x%02X",
                             status, (uint32_t)response);
        return status ? status : -1;
    }
    const char *state = selected ? "ON" : "OFF";
    if (audio_log_flags() & 2)
        audio_log_extended(3, module, file, "SVC_I2SOutputCtrl", 859,
                           "I2SOutputCtrl success: %s", state);
    if ((audio_log_flags() & 1) || (audio_log_flags() & 4))
        audio_log_simple(0x0c400000, "[codec.host]I2SOutputCtrl success: %s",
                         "[codec.host]I2SOutputCtrl success: %s", state);
    return 0;
}
