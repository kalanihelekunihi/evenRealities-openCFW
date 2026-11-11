#include "nrf_log_types.h"
_Static_assert(sizeof(nrf_log_module_const_data_t)==8,"native module record");
const char r1_log_module_name_0[] __attribute__((section(".r1.log.module_name.0")))="peer_manager_gcm";
const char r1_log_module_name_1[] __attribute__((section(".r1.log.module_name.1")))="peer_manager_gscm";
const char r1_log_module_name_2[] __attribute__((section(".r1.log.module_name.2")))="peer_manager_im";
const char r1_log_module_name_3[] __attribute__((section(".r1.log.module_name.3")))="nrf_ble_gatt";
const char r1_log_module_name_4[] __attribute__((section(".r1.log.module_name.4")))="peer_manager_pds";
const char r1_log_module_name_5[] __attribute__((section(".r1.log.module_name.5")))="peer_manager_pdb";
const char r1_log_module_name_6[] __attribute__((section(".r1.log.module_name.6")))="peer_manager";
const char r1_log_module_name_7[] __attribute__((section(".r1.log.module_name.7")))="peer_manager_handler";
const char r1_log_module_name_8[] __attribute__((section(".r1.log.module_name.8")))="peer_manager_smd";
const char r1_log_module_name_9[] __attribute__((section(".r1.log.module_name.9")))="peer_manager_sm";
const char r1_log_module_name_10[] __attribute__((section(".r1.log.module_name.10")))="clock";
const char r1_log_module_name_11[] __attribute__((section(".r1.log.module_name.11")))="CLOCK";
const char r1_log_module_name_12[] __attribute__((section(".r1.log.module_name.12")))="GPIOTE";
const char r1_log_module_name_13[] __attribute__((section(".r1.log.module_name.13")))="PRS";
const char r1_log_module_name_14[] __attribute__((section(".r1.log.module_name.14")))="UART";
const char r1_log_module_name_15[] __attribute__((section(".r1.log.module_name.15")))="UARTE";
const char r1_log_module_name_16[] __attribute__((section(".r1.log.module_name.16")))="TWIM";
const char r1_log_module_name_17[] __attribute__((section(".r1.log.module_name.17")))="WDT";
const char r1_log_module_name_18[] __attribute__((section(".r1.log.module_name.18")))="RTC";
const char r1_log_module_name_19[] __attribute__((section(".r1.log.module_name.19")))="SAADC";
const char r1_log_module_name_20[] __attribute__((section(".r1.log.module_name.20")))="SPIM";
const char r1_log_module_name_21[] __attribute__((section(".r1.log.module_name.21")))="TIMER";
const char r1_log_module_name_22[] __attribute__((section(".r1.log.module_name.22")))="NFCT";
const char r1_log_module_name_23[] __attribute__((section(".r1.log.module_name.23")))="PDM";
const char r1_log_module_name_24[] __attribute__((section(".r1.log.module_name.24")))="PWM";
const char r1_log_module_name_25[] __attribute__((section(".r1.log.module_name.25")))="app_button";
const char r1_log_module_name_26[] __attribute__((section(".r1.log.module_name.26")))="nrf_fstorage";
const char r1_log_module_name_27[] __attribute__((section(".r1.log.module_name.27")))="pwr_mgmt";
const char r1_log_module_name_28[] __attribute__((section(".r1.log.module_name.28")))="app";
const char r1_log_module_name_29[] __attribute__((section(".r1.log.module_name.29")))="nrf_sdh";
const char r1_log_module_name_30[] __attribute__((section(".r1.log.module_name.30")))="nrf_sdh_ble";
const char r1_log_module_name_31[] __attribute__((section(".r1.log.module_name.31")))="nrf_sdh_soc";
const nrf_log_module_const_data_t r1_log_module_records[32] __attribute__((section(".r1.log.modules")))={
    {r1_log_module_name_0,0,0,3,3},
    {r1_log_module_name_1,0,0,3,3},
    {r1_log_module_name_2,0,0,3,3},
    {r1_log_module_name_3,0,0,4,4},
    {r1_log_module_name_4,0,0,3,3},
    {r1_log_module_name_5,0,0,3,3},
    {r1_log_module_name_6,0,0,3,3},
    {r1_log_module_name_7,0,0,3,3},
    {r1_log_module_name_8,0,0,3,3},
    {r1_log_module_name_9,0,0,3,3},
    {r1_log_module_name_10,0,0,0,0},
    {r1_log_module_name_11,0,0,0,0},
    {r1_log_module_name_12,0,0,0,0},
    {r1_log_module_name_13,0,0,0,0},
    {r1_log_module_name_14,0,0,0,0},
    {r1_log_module_name_15,0,0,0,0},
    {r1_log_module_name_16,0,0,0,0},
    {r1_log_module_name_17,0,0,0,0},
    {r1_log_module_name_18,0,0,0,0},
    {r1_log_module_name_19,0,0,0,0},
    {r1_log_module_name_20,0,0,0,0},
    {r1_log_module_name_21,0,0,0,0},
    {r1_log_module_name_22,0,0,0,0},
    {r1_log_module_name_23,0,0,0,0},
    {r1_log_module_name_24,0,0,0,0},
    {r1_log_module_name_25,0,0,0,0},
    {r1_log_module_name_26,0,0,4,4},
    {r1_log_module_name_27,0,0,0,0},
    {r1_log_module_name_28,0,0,4,4},
    {r1_log_module_name_29,0,0,3,3},
    {r1_log_module_name_30,0,0,3,3},
    {r1_log_module_name_31,0,0,3,3},
};

/* Stable name order for SDK ordered queries while runtime filters are off.
 * Constant IDs 0..31 remain native; the two extra SDK modules occupy 32/33. */
_Static_assert(sizeof(nrf_log_module_dynamic_data_t)==4,"SDK dynamic module record");
nrf_log_module_dynamic_data_t r1_log_module_dynamic_records[34]
 __attribute__((section(".r1.log.dynamic"),aligned(4)))={
    {.order_idx=24,.filter=0}, /* peer_manager_gcm */
    {.order_idx=25,.filter=0}, /* peer_manager_gscm */
    {.order_idx=27,.filter=0}, /* peer_manager_im */
    {.order_idx=17,.filter=0}, /* nrf_ble_gatt */
    {.order_idx=29,.filter=0}, /* peer_manager_pds */
    {.order_idx=28,.filter=0}, /* peer_manager_pdb */
    {.order_idx=22,.filter=0}, /* peer_manager */
    {.order_idx=26,.filter=0}, /* peer_manager_handler */
    {.order_idx=31,.filter=0}, /* peer_manager_smd */
    {.order_idx=30,.filter=0}, /* peer_manager_sm */
    {.order_idx=16,.filter=0}, /* clock */
    {.order_idx=0,.filter=0}, /* CLOCK */
    {.order_idx=1,.filter=0}, /* GPIOTE */
    {.order_idx=4,.filter=0}, /* PRS */
    {.order_idx=11,.filter=0}, /* UART */
    {.order_idx=12,.filter=0}, /* UARTE */
    {.order_idx=10,.filter=0}, /* TWIM */
    {.order_idx=13,.filter=0}, /* WDT */
    {.order_idx=6,.filter=0}, /* RTC */
    {.order_idx=7,.filter=0}, /* SAADC */
    {.order_idx=8,.filter=0}, /* SPIM */
    {.order_idx=9,.filter=0}, /* TIMER */
    {.order_idx=2,.filter=0}, /* NFCT */
    {.order_idx=3,.filter=0}, /* PDM */
    {.order_idx=5,.filter=0}, /* PWM */
    {.order_idx=15,.filter=0}, /* app_button */
    {.order_idx=18,.filter=0}, /* nrf_fstorage */
    {.order_idx=32,.filter=0}, /* pwr_mgmt */
    {.order_idx=14,.filter=0}, /* app */
    {.order_idx=19,.filter=0}, /* nrf_sdh */
    {.order_idx=20,.filter=0}, /* nrf_sdh_ble */
    {.order_idx=21,.filter=0}, /* nrf_sdh_soc */
    {.order_idx=23,.filter=0}, /* peer_manager_ast */
    {.order_idx=33,.filter=0}, /* sortlist */
};
