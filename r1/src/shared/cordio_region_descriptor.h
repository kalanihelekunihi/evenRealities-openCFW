#ifndef R1_CORDIO_REGION_DESCRIPTOR_H
#define R1_CORDIO_REGION_DESCRIPTOR_H

#include <stdint.h>

#define R1_CORDIO_DESCRIPTOR_MAGIC 0x52314344u
#define R1_CORDIO_DESCRIPTOR_VERSION 22u
#define R1_CORDIO_FLASH_BASE 0x00001000u
#define R1_CORDIO_FLASH_LIMIT 0x00027000u
#define R1_CORDIO_RAM_BASE 0x20000000u
#define R1_CORDIO_RAM_LIMIT 0x200064a8u

typedef struct {
    uint32_t magic;
    uint32_t version;
    uint32_t bytes;
    uint32_t flash_base;
    uint32_t flash_limit;
    uint32_t ram_base;
    uint32_t ram_limit;
    uint32_t bss_begin;
    uint32_t bss_end;
    uint32_t data_load;
    uint32_t data_begin;
    uint32_t data_end;
    uint32_t code_end;
    uint32_t controller_bootstrap;
    uint32_t timer_update;
    uint32_t dispatch_once;
    uint32_t ll_set_bd_addr;
    uint32_t clock_irq;
    uint32_t radio_irq;
    uint32_t timer0_irq;
    uint32_t timer1_irq;
    uint32_t ccm_aar_irq;
    uint32_t rtc1_irq;
    uint32_t dfu_cfg_set;
    uint32_t dfu_cfg_ready;
    uint32_t dfu_manager_enable;
    uint32_t gap_device_name_set;
    uint32_t gap_device_name_get;
    uint32_t gap_ppcp_set;
    uint32_t gap_adv_configure;
    uint32_t gap_adv_start;
    uint32_t gap_adv_stop;
    uint32_t soc_evt_get;
    uint32_t dfu_flash_register;
    uint32_t dfu_flash_service;
    uint32_t dfu_flash_erase;
    uint32_t dfu_flash_write;
    uint32_t dfu_host_start;
    uint32_t dfu_host_ready;
    uint32_t dfu_host_shutdown;
    uint32_t dfu_ble_enable;
    uint32_t dfu_gap_disconnect;
    uint32_t dfu_gap_conn_param_update;
    uint32_t dfu_gap_data_length_update;
    uint32_t dfu_gap_phy_update;
    uint32_t dfu_gatts_exchange_mtu_reply;
    uint32_t gatts_service_add;
    uint32_t gatts_characteristic_add;
    uint32_t gatts_hvx;
    uint32_t gatts_sys_attr_set;
    uint32_t gatts_authorize_reply;
    uint32_t dfu_gatts_value_get;
    uint32_t dfu_sec_params_reply;
    uint32_t dfu_sec_info_reply;
    uint32_t dfu_manager_disable;
} r1_cordio_region_descriptor_t;

_Static_assert(sizeof(r1_cordio_region_descriptor_t) == 220u,
               "Cordio cross-image descriptor layout changed");

#endif
