/* SPDX-License-Identifier: MIT */
/* Reconstructed flash-only LvpLoadKwsNpuModle path, package 0x1023c.
 * Explicitly initialize fields that stock copied from uninitialized stack.
 * The decoded task consumer ignores these fields; full loader testing pending. */
#include <stdint.h>
struct kws_task {
    uint32_t module_id, ops, data, input, output, cmd, temporary, weight;
};
extern uint32_t LvpModelGetCmdSize(void), LvpModelGetWeightSize(void);
extern int32_t LvpModelGetOpsSize(void), LvpModelGetDataSize(void), LvpModelGetTmpSize(void);
extern uint32_t gx_get_time_ms(void);
extern void *gx_spi_flash_probe(unsigned, unsigned, unsigned, unsigned);
extern int gx_spi_flash_readdata(void *, unsigned, void *, unsigned);
extern int printf_(const char *, ...);
extern void LvpSetSnpuTask(const struct kws_task *);
extern const char open_cfw_kws_flash_init_error[], open_cfw_kws_flash_elapsed[], open_cfw_kws_flash_read_error[];
/* Stock rounds signed model sizes with truncation toward zero. */
static uint32_t aligned_signed(int32_t value)
{
    int32_t sum = (int32_t)((uint32_t)value + 3u);
    return (uint32_t)(sum / 4) * 4u;
}
void open_cfw_gx8002_kws_flash_load(void)
{
    struct kws_task task;
    uint32_t commands = LvpModelGetCmdSize();
    uint32_t weights = LvpModelGetWeightSize();
    task.ops = 0x20000000u;
    task.data = task.ops + aligned_signed(LvpModelGetOpsSize());
    task.temporary = task.data + aligned_signed(LvpModelGetDataSize());
    task.cmd = task.temporary + aligned_signed(LvpModelGetTmpSize());
    commands = (commands + 3u) & ~3u;
    task.weight = task.cmd + commands;
    uint32_t start = gx_get_time_ms();
    void *flash = gx_spi_flash_probe(0, 0, 6144000, 2048);
    weights = (weights + 3u) & ~3u;
    if (!flash) {
        printf_(open_cfw_kws_flash_init_error);
        return;
    }
    int status = gx_spi_flash_readdata(flash, 0xf804, (void *)(uintptr_t)task.cmd, commands);
    status |= gx_spi_flash_readdata(flash, 0xf804 + commands, (void *)(uintptr_t)task.weight, weights);
    printf_(open_cfw_kws_flash_elapsed, gx_get_time_ms() - start);
    if (status) printf_(open_cfw_kws_flash_read_error);
    else {
        task.module_id = 0;
        task.input = 0;
        task.output = 0;
        LvpSetSnpuTask(&task);
    }
}
