#ifndef OPEN_CFW_AT_BUZZER_HOST_H
#define OPEN_CFW_AT_BUZZER_HOST_H

#include <stdint.h>

extern char open_cfw_test_at_buzzer_output[2048];
extern unsigned int open_cfw_test_at_buzzer_output_count;
extern unsigned int open_cfw_test_at_buzzer_note_count;
extern unsigned int open_cfw_test_at_buzzer_play_count;
extern unsigned int open_cfw_test_at_buzzer_start_count;
extern unsigned int open_cfw_test_at_buzzer_stop_count;
extern uint32_t open_cfw_test_at_buzzer_arguments[3];
void open_cfw_test_at_buzzer_reset(void);
void open_cfw_test_at_buzzer_emit(const char *format, ...);
void open_cfw_test_at_buzzer_note(uint8_t note, uint8_t tone, uint8_t beat);
void open_cfw_test_at_buzzer_play(uint32_t type);
void open_cfw_test_at_buzzer_start(uint32_t frequency, uint8_t duty);
void open_cfw_test_at_buzzer_stop(void);

#define OPEN_CFW_AT_BUZZER_MISSING "AT^BUZZER: Missing parameters\r\n"
#define OPEN_CFW_AT_BUZZER_COMMAND_NOTE "note"
#define OPEN_CFW_AT_BUZZER_COMMAND_PLAY "play"
#define OPEN_CFW_AT_BUZZER_COMMAND_START "start"
#define OPEN_CFW_AT_BUZZER_COMMAND_STOP "stop"
#define OPEN_CFW_AT_BUZZER_USAGE "Usage:\r\n"
#define OPEN_CFW_AT_BUZZER_USAGE_NOTE "  AT^BUZZER=note,<note>,<tone>,<beat>\r\n"
#define OPEN_CFW_AT_BUZZER_USAGE_PLAY "  AT^BUZZER=play,<type>\r\n"
#define OPEN_CFW_AT_BUZZER_USAGE_START "  AT^BUZZER=start,<freq>,<duty>\r\n"
#define OPEN_CFW_AT_BUZZER_USAGE_STOP "  AT^BUZZER=stop\r\n"
#define OPEN_CFW_AT_BUZZER_NOTE_MISSING "AT^BUZZER=note: Missing parameters\r\n"
#define OPEN_CFW_AT_BUZZER_NOTE_USAGE "Usage: AT^BUZZER=note,<note>,<tone>,<beat>\r\n"
#define OPEN_CFW_AT_BUZZER_NOTE_INVALID "AT^BUZZER=note: Invalid parameters (parsed %d)\r\n"
#define OPEN_CFW_AT_BUZZER_NOTE_RANGE "AT^BUZZER=note: Parameters out of range\r\n"
#define OPEN_CFW_AT_BUZZER_NOTE_RANGE_HELP "note: 0-7, tone: 0-3, beat: 1-100\r\n"
#define OPEN_CFW_AT_BUZZER_NOTE_STATUS "Buzzer note: %d, tone: %d, beat: %d\r\n"
#define OPEN_CFW_AT_BUZZER_PLAY_MISSING "AT^BUZZER=play: Missing parameter\r\n"
#define OPEN_CFW_AT_BUZZER_PLAY_USAGE "Usage: AT^BUZZER=play,<type>\r\n"
#define OPEN_CFW_AT_BUZZER_PLAY_RANGE "AT^BUZZER=play: Type out of range (0-10)\r\n"
#define OPEN_CFW_AT_BUZZER_PLAY_STATUS "Buzzer play type: %d\r\n"
#define OPEN_CFW_AT_BUZZER_START_MISSING "AT^BUZZER=start: Missing parameters\r\n"
#define OPEN_CFW_AT_BUZZER_START_USAGE "Usage: AT^BUZZER=start,<freq>,<duty>\r\n"
#define OPEN_CFW_AT_BUZZER_START_INVALID "AT^BUZZER=start: Invalid parameters (parsed %d)\r\n"
#define OPEN_CFW_AT_BUZZER_START_RANGE "AT^BUZZER=start: Parameters out of range\r\n"
#define OPEN_CFW_AT_BUZZER_START_RANGE_HELP "freq: 1-20000, duty: 0-100\r\n"
#define OPEN_CFW_AT_BUZZER_START_STATUS "Buzzer start: freq=%d, duty=%d\r\n"
#define OPEN_CFW_AT_BUZZER_STOP_STATUS "Buzzer stop\r\n"
#define OPEN_CFW_AT_BUZZER_UNKNOWN "AT^BUZZER: Unknown subcommand '%s'\r\n"
#define OPEN_CFW_AT_BUZZER_UNKNOWN_HELP "Use: note, play, start, stop\r\n"
#define OPEN_CFW_AT_BUZZER_OK "AT^BUZZER+OK\r\n"
#define OPEN_CFW_AT_BUZZER_OUTPUT(...) open_cfw_test_at_buzzer_emit(__VA_ARGS__)
#define OPEN_CFW_AT_BUZZER_PLAY_NOTE(note,tone,beat) open_cfw_test_at_buzzer_note((note),(tone),(beat))
#define OPEN_CFW_AT_BUZZER_PLAY(type) open_cfw_test_at_buzzer_play((type))
#define OPEN_CFW_AT_BUZZER_START(frequency,duty) open_cfw_test_at_buzzer_start((frequency),(duty))
#define OPEN_CFW_AT_BUZZER_STOP() open_cfw_test_at_buzzer_stop()

#endif
