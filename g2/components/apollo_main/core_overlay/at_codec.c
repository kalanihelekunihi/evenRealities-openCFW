/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of platform/service/eAT/at_codec.c. */
#include <stdint.h>

#ifndef OPEN_CFW_AT_CODEC_ACQUIRE
int32_t open_cfw_audio_app_acquire(uint32_t application);
#define OPEN_CFW_AT_CODEC_ACQUIRE(application) \
    open_cfw_audio_app_acquire((application))
#endif

#ifndef OPEN_CFW_AT_CODEC_RELEASE
int32_t open_cfw_audio_app_release(uint32_t application);
#define OPEN_CFW_AT_CODEC_RELEASE(application) \
    open_cfw_audio_app_release((application))
#endif

#ifndef OPEN_CFW_AT_CODEC_OUTPUT
void open_cfw_at_codec_output(const char *text);
#define OPEN_CFW_AT_CODEC_OUTPUT(text) open_cfw_at_codec_output((text))
#endif

#ifndef OPEN_CFW_AT_CODEC_OK
#define OPEN_CFW_AT_CODEC_OK ((const char *)(uintptr_t)0x00785140u)
#endif

__attribute__((used, noinline))
int32_t open_cfw_at_codec_audio_control(const char *parameter)
{
    if (parameter != (const char *)0) {
        if (parameter[0] == '1') {
            (void)OPEN_CFW_AT_CODEC_ACQUIRE(7u);
        } else if (parameter[0] == '0') {
            (void)OPEN_CFW_AT_CODEC_RELEASE(7u);
        }
    }
    OPEN_CFW_AT_CODEC_OUTPUT(OPEN_CFW_AT_CODEC_OK);
    return 1;
}
