#include <stdint.h>

extern uint32_t host_at_codec_acquire_calls;
extern uint32_t host_at_codec_release_calls;
extern uint32_t host_at_codec_output_calls;
extern uint32_t host_at_codec_last_application;
extern const char *host_at_codec_last_output;

int32_t host_at_codec_acquire(uint32_t application);
int32_t host_at_codec_release(uint32_t application);
void host_at_codec_output(const char *text);

#define OPEN_CFW_AT_CODEC_ACQUIRE(application) host_at_codec_acquire(application)
#define OPEN_CFW_AT_CODEC_RELEASE(application) host_at_codec_release(application)
#define OPEN_CFW_AT_CODEC_OUTPUT(text) host_at_codec_output(text)
#define OPEN_CFW_AT_CODEC_OK "AUD_AUDIO+OK\r\n"
