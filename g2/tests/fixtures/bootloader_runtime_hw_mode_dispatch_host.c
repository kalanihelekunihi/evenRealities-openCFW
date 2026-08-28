#include <stdint.h>

struct open_cfw_hwmd_instance;
struct open_cfw_hwmd_request;

uint32_t open_cfw_hwmd_host_mode_zero_result, open_cfw_hwmd_host_mode_one_result;
uint32_t open_cfw_hwmd_host_primary_latch_result, open_cfw_hwmd_host_secondary_latch_result;
uint32_t open_cfw_hwmd_host_mode_zero_count, open_cfw_hwmd_host_mode_one_count;
uint32_t open_cfw_hwmd_host_primary_latch_count, open_cfw_hwmd_host_secondary_latch_count;
uint32_t open_cfw_hwmd_host_primary_progress_count, open_cfw_hwmd_host_secondary_progress_count;
uint32_t open_cfw_hwmd_host_clear_status_count;

uint32_t open_cfw_hwmd_host_mode_zero(struct open_cfw_hwmd_instance *instance, struct open_cfw_hwmd_request *request) { (void)instance; (void)request; open_cfw_hwmd_host_mode_zero_count++; return open_cfw_hwmd_host_mode_zero_result; }
uint32_t open_cfw_hwmd_host_mode_one(struct open_cfw_hwmd_instance *instance, struct open_cfw_hwmd_request *request) { (void)instance; (void)request; open_cfw_hwmd_host_mode_one_count++; return open_cfw_hwmd_host_mode_one_result; }
uint32_t open_cfw_hwmd_host_primary_latch(struct open_cfw_hwmd_instance *instance) { (void)instance; open_cfw_hwmd_host_primary_latch_count++; return open_cfw_hwmd_host_primary_latch_result; }
uint32_t open_cfw_hwmd_host_secondary_latch(struct open_cfw_hwmd_instance *instance) { (void)instance; open_cfw_hwmd_host_secondary_latch_count++; return open_cfw_hwmd_host_secondary_latch_result; }
void open_cfw_hwmd_host_primary_progress(struct open_cfw_hwmd_instance *instance) { (void)instance; open_cfw_hwmd_host_primary_progress_count++; }
void open_cfw_hwmd_host_secondary_progress(struct open_cfw_hwmd_instance *instance) { (void)instance; open_cfw_hwmd_host_secondary_progress_count++; }
void open_cfw_hwmd_host_clear_status(struct open_cfw_hwmd_request *request) { (void)request; open_cfw_hwmd_host_clear_status_count++; }

#include "../../components/bootloader/core_overlay/runtime_hw_mode_dispatch_4233e8.c"
