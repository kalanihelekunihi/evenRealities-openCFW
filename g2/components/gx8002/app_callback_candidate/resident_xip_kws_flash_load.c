/* SPDX-License-Identifier: MIT
 * Native XIP KWS flash loader 0x10206cb0 and 32-byte task-copy child
 * 0x10208c14. Model sizes and flash device remain true runtime inputs.
 */
#include <stdint.h>

extern int32_t gx8002_xip_model_cmd_size_10208bf4(void);
extern int32_t gx8002_xip_model_weight_size_10208bfc(void);
extern int32_t gx8002_xip_model_ops_size_10208c04(void);
extern int32_t gx8002_xip_model_data_size_10208c08(void);
extern int32_t gx8002_xip_model_tmp_size_10208c10(void);
extern uint32_t g2_codec_timestamp(void);
extern int32_t gx8002_resident_flash_probe_2475c(
    uint32_t, uint32_t, uint32_t, uint32_t);
extern int32_t gx8002_resident_flash_dispatch_read_247b8(
    const volatile uint8_t *, uint32_t, uint32_t, uint32_t);
extern void gx8002_resident_memcpy_25738(void *, const void *, uint32_t);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
/* Stock copies these three ambient stack words without assigning them. */
extern void gx8002_xip_kws_ambient_task_words(
    uint32_t *word0, uint32_t *word3, uint32_t *word4);

static uint32_t native_signed_align4(int32_t size)
{
    uint32_t plus_three = (uint32_t)size + 3u;
    if ((int32_t)plus_three < 0) plus_three = (uint32_t)size + 6u;
    return plus_three & ~UINT32_C(3);
}

void gx8002_xip_set_snpu_task_10208c14(const uint32_t task[8])
{
    gx8002_resident_memcpy_25738(
        (void *)(uintptr_t)UINT32_C(0x2002e85c), task, 32u);
}

void gx8002_xip_kws_flash_load_10206cb0(void)
{
    int32_t command_size = gx8002_xip_model_cmd_size_10208bf4();
    int32_t weight_size = gx8002_xip_model_weight_size_10208bfc();
    uint32_t task[8];
    gx8002_xip_kws_ambient_task_words(&task[0], &task[3], &task[4]);
    task[1] = UINT32_C(0x20000000);
    task[2] = task[1] + native_signed_align4(
        gx8002_xip_model_ops_size_10208c04());
    task[6] = task[2] + native_signed_align4(
        gx8002_xip_model_data_size_10208c08());
    task[5] = task[6] + native_signed_align4(
        gx8002_xip_model_tmp_size_10208c10());
    uint32_t aligned_command = ((uint32_t)command_size + 3u) & ~UINT32_C(3);
    task[7] = task[5] + aligned_command;
    uint32_t start = g2_codec_timestamp();
    int32_t descriptor = gx8002_resident_flash_probe_2475c(
        0u, 0u, UINT32_C(0x5dc000), UINT32_C(0x800));
    if (descriptor == 0) {
        gx8002_xip_tws_publish_10206c24("[LVP_KWS ]Init Flash Failed\n");
        return;
    }
    int32_t first = gx8002_resident_flash_dispatch_read_247b8(
        (const volatile uint8_t *)(uintptr_t)(uint32_t)descriptor,
        UINT32_C(0xf804), task[5], aligned_command);
    int32_t second = gx8002_resident_flash_dispatch_read_247b8(
        (const volatile uint8_t *)(uintptr_t)(uint32_t)descriptor,
        UINT32_C(0xf804) + aligned_command, task[7],
        ((uint32_t)weight_size + 3u) & ~UINT32_C(3));
    uint32_t elapsed = g2_codec_timestamp() - start;
    gx8002_xip_tws_publish_10206c24("[LVP_KWS ]Kws Use:%d ms\n", elapsed);
    if ((first | second) != 0) {
        gx8002_xip_tws_publish_10206c24("[LVP_KWS ]Read Flash Failed\n");
        return;
    }
    gx8002_xip_set_snpu_task_10208c14(task);
}
