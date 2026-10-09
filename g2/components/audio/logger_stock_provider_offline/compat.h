#ifndef LOGGER_STOCK_COMPAT_H
#define LOGGER_STOCK_COMPAT_H
#include <stdint.h>
#include <stdbool.h>
#define AM_HAL_STATUS_SUCCESS 0u
#define AM_HAL_STATUS_IN_USE 3u
#define AM_HAL_STATUS_TIMEOUT 4u
#define AM_HAL_PWRCTRL_PERIPH_DEBUG 28u
#define AM_REGVAL(x) (*(volatile uint32_t *)(x))
#define AM_CRITICAL_BEGIN uint32_t saved; __asm volatile("mrs %0, primask\ncpsid i":"=r"(saved)::"memory");
#define AM_CRITICAL_END __asm volatile("msr primask, %0"::"r"(saved):"memory");
#define g_ui8DebugEnableCount (*(volatile uint8_t *)0x20074F5C)
#define g_ui8PowerCount (*(volatile uint8_t *)0x20074F5D)
#define g_ui8TRCENAcount (*(volatile uint8_t *)0x20074F5E)
#define g_ui8PwrStDbgOnEntry (*(volatile uint8_t *)0x20074F5F)
#define g_bTpiu_DebugEnabled (*(volatile uint8_t *)0x20074F7D)
#define g_ui8TpiuEnCnt (*(volatile uint8_t *)0x20074F7E)
typedef struct { union {uint32_t DBGCTRL; struct {uint32_t DBGTPIUTRACEENABLE:1,DBGTPIUCLKSEL:3,other:28;} DBGCTRL_b;}; } DebugRegs;
#define MCUCTRL ((volatile DebugRegs *)0x40020250)
#define MCUCTRL_DBGCTRL_DBGTPIUTRACEENABLE_DIS 0u
#define MCUCTRL_DBGCTRL_DBGTPIUCLKSEL_OFF 0u
typedef struct {uint32_t DEMCR;} DCBRegs;
#define DCB ((volatile DCBRegs *)0xE000EDFC)
#define DCB_DEMCR_TRCENA_Msk 0x1000000u
typedef struct {uint32_t PORT[32];uint8_t reserved[0xE00];uint32_t TCR;} ITMRegs;
#define ITM ((volatile ITMRegs *)0xE0000000)
#define ITM_TCR_SWOENA_Msk 0x10u
#define ITM_TCR_ITMENA_Msk 1u
#define ITM_TCR_BUSY_Msk 0x800000u
#define ITM_STIM_DISABLED_Msk 2u
#define ITM_STIM_FIFOREADY_Msk 1u
uint32_t am_hal_delay_us_status_change(uint32_t,uint32_t,uint32_t,uint32_t);
void am_hal_delay_us(uint32_t);
uint32_t am_hal_debug_disable(void);
uint32_t am_hal_debug_trace_disable(void);
uint32_t am_hal_debug_power(bool);
uint32_t am_hal_itm_tpiu_pipeline_flush(void);
bool am_hal_itm_not_busy(void);
bool am_hal_itm_stimulus_not_busy(uint32_t);
bool am_hal_itm_print_not_busy(void);
uint32_t am_hal_itm_disable(void);
uint32_t am_hal_tpiu_disable(void);
uint32_t am_hal_pwrctrl_periph_disable(uint32_t);
uint32_t am_hal_pwrctrl_periph_enable(uint32_t);
uint32_t am_hal_pwrctrl_periph_enabled(uint32_t,bool *);
#endif
