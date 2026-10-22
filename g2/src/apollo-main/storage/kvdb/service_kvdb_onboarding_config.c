/* KV record "kvOnboardingConfig" (one byte, no version or CRC), stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_onboarding_config.c.
 * Native 0x4a777c..0x4a7899 except kvdbOnboardingConfigGet 0x4a7832
 * (audio_onboarding_flag_get_4a7832 in app/onboarding-check); pool 0x4a789c..0x4a78cf.
 * Only data index 0 exists; its value lives at RAM 0x20000040 (default 0). */
#include "kvdb_private.h"

extern volatile uint8_t g2_onboarding_flag; /* RAM 0x20000040 */

static const char key[] = "kvOnboardingConfig"; /* ROM 0x783370 */
static const char module_tag[] = "kv.onboarding_config"; /* ROM 0x77b95c */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_onboarding_config.c"; /* ROM 0x6db934 */
static const char set_fn[] = "SVC_SetKvdbOnboardingConfig"; /* ROM 0x771348 */
static const char set_msg[] = "Unknown kv dataIdx\n"; /* ROM 0x78335c */
static const char set_msg_short[] = "[kv.onboarding_config]Unknown kv dataIdx\n"; /* ROM 0x743360 */
static const char write_fn[] = "SVC_KvdbBlobWriteOnboardingConfig"; /* ROM 0x759b64 */
static const char write_msg[] = "SVC_KvdbBlobWriteOnboardingConfig: write fail!!"; /* ROM 0x738534 */
static const char write_msg_short[] =
    "[kv.onboarding_config]SVC_KvdbBlobWriteOnboardingConfig: write fail!!"; /* ROM 0x6fcfec */
static const char read_fn[] = "SVC_KvdbReadOnboardingConfig"; /* ROM 0x765010 */
static const char read_msg[] = "SVC_KvdbReadOnboardingConfig: read fail!!"; /* ROM 0x74338c */
static const char read_msg_short[] =
    "[kv.onboarding_config]SVC_KvdbReadOnboardingConfig: read fail!!"; /* ROM 0x70ee24 */

int32_t SVC_SetKvdbOnboardingConfig(uint8_t index, const uint8_t *value) {
    if (index != 0u) {
        G2_KV_LOG(2u, module_tag, source_file, set_fn, 45u, set_msg, set_msg_short, 0x08000000u);
        return -1;
    }
    if (value != NULL)
        g2_onboarding_flag = *value;
    return 0;
}

int32_t SVC_KvdbBlobWriteOnboardingConfig(void) {
    int32_t status = audio_settings_kvdb_blob_write(key, (const void *)(uintptr_t)&g2_onboarding_flag, 1u);
    if (status != 0)
        G2_KV_LOG(1u, module_tag, source_file, write_fn, 57u, write_msg, write_msg_short, 0x04000000u);
    return status;
}

void kvdbOnboardingConfigUpdateAndPersist(uint8_t index, const uint8_t *value) {
    if (SVC_SetKvdbOnboardingConfig(index, value) == 0)
        (void)SVC_KvdbBlobWriteOnboardingConfig();
}

/* Both arms of the stock index switch return the same cell. */
volatile uint8_t *kvdbOnboardingConfigPointer(uint8_t index) {
    if (index == 0u)
        return &g2_onboarding_flag;
    return &g2_onboarding_flag;
}

volatile uint8_t *SVC_KvdbReadOnboardingConfig(uint8_t index) {
    if (SVC_KvdbBlobRead(key, (void *)(uintptr_t)&g2_onboarding_flag, 1u) == 0)
        G2_KV_LOG(1u, module_tag, source_file, read_fn, 93u, read_msg, read_msg_short, 0x04000000u);
    return kvdbOnboardingConfigPointer(index);
}
