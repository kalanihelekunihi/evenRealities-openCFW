#include <stdint.h>
struct open_cfw_hwp_instance;
uint32_t open_cfw_hwp_host_token, open_cfw_hwp_host_enter_count, open_cfw_hwp_host_restore_count, open_cfw_hwp_host_restored_token;
uint32_t open_cfw_hwp_host_primary_result, open_cfw_hwp_host_primary_count, open_cfw_hwp_host_primary_requested;
uint32_t open_cfw_hwp_host_secondary_result, open_cfw_hwp_host_secondary_count, open_cfw_hwp_host_secondary_requested;
uint32_t open_cfw_hwp_host_primary_callback_count, open_cfw_hwp_host_primary_callback_event;
uint32_t open_cfw_hwp_host_secondary_callback_count, open_cfw_hwp_host_secondary_callback_event;
uint32_t open_cfw_hwp_host_pump_count, open_cfw_hwp_host_snapshot_count;
uint32_t open_cfw_hwp_host_critical_enter(void);
void open_cfw_hwp_host_critical_restore(uint32_t);
uint32_t open_cfw_hwp_host_primary_transfer(struct open_cfw_hwp_instance *, uint32_t, uint32_t *);
uint32_t open_cfw_hwp_host_secondary_transfer(struct open_cfw_hwp_instance *, uint32_t, uint32_t *);
void open_cfw_hwp_host_primary_callback(uint32_t);
void open_cfw_hwp_host_secondary_callback(uint32_t);
void open_cfw_hwp_host_pump(struct open_cfw_hwp_instance *);
void open_cfw_hwp_host_snapshot(struct open_cfw_hwp_instance *);
#include "../../components/bootloader/core_overlay/runtime_hw_progress_423524.c"
uint32_t open_cfw_hwp_host_critical_enter(void){open_cfw_hwp_host_enter_count++;return open_cfw_hwp_host_token;}
void open_cfw_hwp_host_critical_restore(uint32_t t){open_cfw_hwp_host_restore_count++;open_cfw_hwp_host_restored_token=t;}
uint32_t open_cfw_hwp_host_primary_transfer(struct open_cfw_hwp_instance *i,uint32_t n,uint32_t *c){(void)i;open_cfw_hwp_host_primary_requested=n;*c=open_cfw_hwp_host_primary_count;return open_cfw_hwp_host_primary_result;}
uint32_t open_cfw_hwp_host_secondary_transfer(struct open_cfw_hwp_instance *i,uint32_t n,uint32_t *c){(void)i;open_cfw_hwp_host_secondary_requested=n;*c=open_cfw_hwp_host_secondary_count;return open_cfw_hwp_host_secondary_result;}
void open_cfw_hwp_host_primary_callback(uint32_t e){open_cfw_hwp_host_primary_callback_count++;open_cfw_hwp_host_primary_callback_event=e;}
void open_cfw_hwp_host_secondary_callback(uint32_t e){open_cfw_hwp_host_secondary_callback_count++;open_cfw_hwp_host_secondary_callback_event=e;}
void open_cfw_hwp_host_pump(struct open_cfw_hwp_instance *i){(void)i;open_cfw_hwp_host_pump_count++;}
void open_cfw_hwp_host_snapshot(struct open_cfw_hwp_instance *i){(void)i;open_cfw_hwp_host_snapshot_count++;}
