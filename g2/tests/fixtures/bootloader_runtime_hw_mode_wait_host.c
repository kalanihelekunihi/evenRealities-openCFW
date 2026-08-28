#include <stdint.h>

struct open_cfw_hwmw_instance;
struct open_cfw_hwmw_request;
uint32_t open_cfw_hwmw_host_mode_two_result, open_cfw_hwmw_host_mode_three_result;
uint32_t open_cfw_hwmw_host_mode_two_count, open_cfw_hwmw_host_mode_three_count;
uint32_t open_cfw_hwmw_host_primary_progress_count, open_cfw_hwmw_host_secondary_progress_count;
uint32_t open_cfw_hwmw_host_primary_clear_after, open_cfw_hwmw_host_secondary_clear_after;
uint32_t open_cfw_hwmw_host_delay_count, open_cfw_hwmw_host_delay_value;
uint32_t open_cfw_hwmw_host_mode_two_start(struct open_cfw_hwmw_instance *, struct open_cfw_hwmw_request *);
uint32_t open_cfw_hwmw_host_mode_three_start(struct open_cfw_hwmw_instance *, struct open_cfw_hwmw_request *);
void open_cfw_hwmw_host_primary_progress(struct open_cfw_hwmw_instance *);
void open_cfw_hwmw_host_secondary_progress(struct open_cfw_hwmw_instance *);
void open_cfw_hwmw_host_delay(uint32_t);

#include "../../components/bootloader/core_overlay/runtime_hw_mode_wait_423444.c"

uint32_t open_cfw_hwmw_host_mode_two_start(struct open_cfw_hwmw_instance *instance, struct open_cfw_hwmw_request *request) { (void)instance; (void)request; open_cfw_hwmw_host_mode_two_count++; return open_cfw_hwmw_host_mode_two_result; }
uint32_t open_cfw_hwmw_host_mode_three_start(struct open_cfw_hwmw_instance *instance, struct open_cfw_hwmw_request *request) { (void)instance; (void)request; open_cfw_hwmw_host_mode_three_count++; return open_cfw_hwmw_host_mode_three_result; }
void open_cfw_hwmw_host_primary_progress(struct open_cfw_hwmw_instance *instance) { open_cfw_hwmw_host_primary_progress_count++; if (open_cfw_hwmw_host_primary_clear_after != 0 && open_cfw_hwmw_host_primary_progress_count == open_cfw_hwmw_host_primary_clear_after) instance->bytes[0x119] = 0; }
void open_cfw_hwmw_host_secondary_progress(struct open_cfw_hwmw_instance *instance) { open_cfw_hwmw_host_secondary_progress_count++; if (open_cfw_hwmw_host_secondary_clear_after != 0 && open_cfw_hwmw_host_secondary_progress_count == open_cfw_hwmw_host_secondary_clear_after) instance->bytes[0x11a] = 0; }
void open_cfw_hwmw_host_delay(uint32_t value) { open_cfw_hwmw_host_delay_count++; open_cfw_hwmw_host_delay_value = value; }
