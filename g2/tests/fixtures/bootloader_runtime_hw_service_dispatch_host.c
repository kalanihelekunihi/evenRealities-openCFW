#include <stdint.h>

struct open_cfw_hwsd_instance;
uint32_t open_cfw_hwsd_host_bank50_value;
uint32_t open_cfw_hwsd_host_status_value;
uint32_t open_cfw_hwsd_host_shutdown_count;
uint32_t open_cfw_hwsd_host_clear_secondary_count;
uint32_t open_cfw_hwsd_host_clear_primary_count;
uint32_t open_cfw_hwsd_host_secondary_progress_count;
uint32_t open_cfw_hwsd_host_primary_progress_count;
uint32_t open_cfw_hwsd_host_callback_count;
uint32_t open_cfw_hwsd_host_callback_status;
uint32_t open_cfw_hwsd_host_callback_context;
uint32_t open_cfw_hwsd_host_status_index;
uint32_t open_cfw_hwsd_host_status_flags;

uint32_t open_cfw_hwsd_host_bank50(uint32_t index) { (void)index; return open_cfw_hwsd_host_bank50_value; }
void open_cfw_hwsd_host_shutdown(struct open_cfw_hwsd_instance *p) { (void)p; ++open_cfw_hwsd_host_shutdown_count; }
void open_cfw_hwsd_host_clear_secondary(struct open_cfw_hwsd_instance *p) { (void)p; ++open_cfw_hwsd_host_clear_secondary_count; }
uint32_t open_cfw_hwsd_host_status_map(uint32_t index, uint32_t flags) { open_cfw_hwsd_host_status_index=index;open_cfw_hwsd_host_status_flags=flags;return open_cfw_hwsd_host_status_value; }
void open_cfw_hwsd_host_callback(uint32_t status, uint32_t context) { ++open_cfw_hwsd_host_callback_count;open_cfw_hwsd_host_callback_status=status;open_cfw_hwsd_host_callback_context=context; }
void open_cfw_hwsd_host_clear_primary(struct open_cfw_hwsd_instance *p) { (void)p; ++open_cfw_hwsd_host_clear_primary_count; }
void open_cfw_hwsd_host_secondary_progress(struct open_cfw_hwsd_instance *p) { (void)p; ++open_cfw_hwsd_host_secondary_progress_count; }
void open_cfw_hwsd_host_primary_progress(struct open_cfw_hwsd_instance *p) { (void)p; ++open_cfw_hwsd_host_primary_progress_count; }

#include "../../components/bootloader/core_overlay/runtime_hw_service_dispatch_42377c.c"
