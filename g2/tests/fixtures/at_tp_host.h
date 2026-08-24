#ifndef OPEN_CFW_AT_TP_HOST_H
#define OPEN_CFW_AT_TP_HOST_H

#include <stdint.h>

extern volatile uint8_t open_cfw_test_at_tp_debug_flag;
extern char open_cfw_test_at_tp_output_log[2048];
extern unsigned int open_cfw_test_at_tp_output_count;
extern unsigned int open_cfw_test_at_tp_stop_count;
extern unsigned int open_cfw_test_at_tp_read_diff_count;
extern unsigned int open_cfw_test_at_tp_prepare_count;
extern unsigned int open_cfw_test_at_tp_save_count;
extern unsigned int open_cfw_test_at_tp_write_count;
extern unsigned int open_cfw_test_at_tp_read_count;
extern unsigned int open_cfw_test_at_tp_delay_count;
extern uint32_t open_cfw_test_at_tp_delay_ticks;
extern uint16_t open_cfw_test_at_tp_diff[5];
extern uint16_t open_cfw_test_at_tp_baseline;
extern uint16_t open_cfw_test_at_tp_written;
extern uint16_t open_cfw_test_at_tp_readback;
extern int open_cfw_test_at_tp_write_status;
extern int open_cfw_test_at_tp_read_status;

void open_cfw_test_at_tp_reset(void);
void open_cfw_test_at_tp_output(const char *format, ...);
void open_cfw_test_at_tp_stop(void);
void open_cfw_test_at_tp_read_diff(uint16_t values[5]);
uint16_t open_cfw_test_at_tp_read_baseline(void);
void open_cfw_test_at_tp_prepare(uint32_t *state);
void open_cfw_test_at_tp_save(void);
int open_cfw_test_at_tp_write(const uint16_t *configuration);
int open_cfw_test_at_tp_read(uint16_t *configuration);
int open_cfw_test_at_tp_delay(uint32_t ticks);

#define OPEN_CFW_AT_TP_GESTURE_FORMAT "Gesture cfg: long_press_threshold_ms=%u\r\n"
#define OPEN_CFW_AT_TP_DIFF_FORMAT "diff: %u, %u, %u, %u, %u\r\n"
#define OPEN_CFW_AT_TP_BASELINE_FORMAT "Proximity baseline: %u\r\n"
#define OPEN_CFW_AT_TP_BASELINE_SAVED "Proximity baseline save command sent successfully.\r\n"
#define OPEN_CFW_AT_TP_GESTURE_READ_FAILED "Gesture cfg read failed.\r\n"
#define OPEN_CFW_AT_TP_GESTURE_USAGE "Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n"
#define OPEN_CFW_AT_TP_GESTURE_INVALID "Invalid gesture cfg. Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n"
#define OPEN_CFW_AT_TP_GESTURE_WRITE_FAILED "Gesture cfg write failed.\r\n"
#define OPEN_CFW_AT_TP_GESTURE_READBACK_FAILED "Gesture cfg write success, but readback failed.\r\n"
#define OPEN_CFW_AT_TP_GESTURE_MISMATCH "Gesture cfg write mismatch: wrote threshold=%u, read back threshold=%u\r\n"
#define OPEN_CFW_AT_TP_GESTURE_UPDATED "Gesture cfg updated and verified successfully.\r\n"
#define OPEN_CFW_AT_TP_OK "AT^TP+OK\r\n"
#define OPEN_CFW_AT_TP_COMMAND_DIFF "1"
#define OPEN_CFW_AT_TP_COMMAND_STOP "0"
#define OPEN_CFW_AT_TP_COMMAND_DEBUG_ON "debug1"
#define OPEN_CFW_AT_TP_COMMAND_DEBUG_OFF "debug0"
#define OPEN_CFW_AT_TP_COMMAND_BASELINE_READ "bsln_read"
#define OPEN_CFW_AT_TP_COMMAND_BASELINE_SET "bsln_set"
#define OPEN_CFW_AT_TP_COMMAND_GESTURE_READ "gesture_cfg_read"
#define OPEN_CFW_AT_TP_COMMAND_GESTURE_SET "gesture_cfg_set"
#define OPEN_CFW_AT_TP_DEBUG_FLAG open_cfw_test_at_tp_debug_flag
#define OPEN_CFW_AT_TP_OUTPUT(...) open_cfw_test_at_tp_output(__VA_ARGS__)
#define OPEN_CFW_AT_TP_STOP() open_cfw_test_at_tp_stop()
#define OPEN_CFW_AT_TP_READ_DIFF(values) open_cfw_test_at_tp_read_diff((values))
#define OPEN_CFW_AT_TP_READ_BASELINE() open_cfw_test_at_tp_read_baseline()
#define OPEN_CFW_AT_TP_PREPARE_BASELINE_SAVE(state) open_cfw_test_at_tp_prepare((state))
#define OPEN_CFW_AT_TP_SAVE_BASELINE() open_cfw_test_at_tp_save()
#define OPEN_CFW_AT_TP_WRITE_GESTURE(configuration) open_cfw_test_at_tp_write((configuration))
#define OPEN_CFW_AT_TP_READ_GESTURE(configuration) open_cfw_test_at_tp_read((configuration))
#define OPEN_CFW_AT_TP_DELAY(ticks) open_cfw_test_at_tp_delay((ticks))

#endif
