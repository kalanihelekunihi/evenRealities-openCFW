#include "at_codec_host.h"

uint32_t host_at_codec_acquire_calls;
uint32_t host_at_codec_release_calls;
uint32_t host_at_codec_output_calls;
uint32_t host_at_codec_last_application;
const char *host_at_codec_last_output;

int32_t host_at_codec_acquire(uint32_t application)
{
    ++host_at_codec_acquire_calls;
    host_at_codec_last_application = application;
    return -1;
}

int32_t host_at_codec_release(uint32_t application)
{
    ++host_at_codec_release_calls;
    host_at_codec_last_application = application;
    return -1;
}

void host_at_codec_output(const char *text)
{
    ++host_at_codec_output_calls;
    host_at_codec_last_output = text;
}

void host_at_codec_reset(void)
{
    host_at_codec_acquire_calls = 0u;
    host_at_codec_release_calls = 0u;
    host_at_codec_output_calls = 0u;
    host_at_codec_last_application = 0u;
    host_at_codec_last_output = (const char *)0;
}
