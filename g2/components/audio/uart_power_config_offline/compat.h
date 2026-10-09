#ifndef UART_POWER_CONFIG_COMPAT
#define UART_POWER_CONFIG_COMPAT
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#define AM_HAL_UART_CHK_HANDLE(h) ((h)&&((*(uint32_t *)(h)&0x1ffffffu)==0x1ea9e06u))
#define AM_HAL_STATUS_SUCCESS 0u
#define AM_HAL_STATUS_INVALID_HANDLE 2u
#define AM_HAL_STATUS_INVALID_ARG 6u
#define AM_HAL_STATUS_INVALID_OPERATION 7u
#define AM_HAL_SYSCTRL_WAKE 0u
#define AM_HAL_SYSCTRL_NORMALSLEEP 1u
#define AM_HAL_SYSCTRL_DEEPSLEEP 2u
#define AM_HAL_PWRCTRL_PERIPH_UART0 11u
#define AM_HAL_CLKMGR_USER_ID_UART0 11u
#define AM_HAL_CLKMGR_CLK_ID_HFRC 4u
#define AM_HAL_CLKMGR_CLK_ID_SYSPLL 6u
#define AM_HAL_UART_CLOCK_SRC_HFRC 0u
#define AM_HAL_UART_CLOCK_SRC_SYSPLL 1u
#define APOLLO5_B0 ((*(volatile uint32_t *)0x4002000c&255u)==0x21u)
#define APOLLO5_GE_B1 ((*(volatile uint32_t *)0x4002000c&255u)>0x21u)
#define MCUCTRL_D2ASPARE_UART0PLL_Msk 0x400000u
#define AM_HAL_UART_STATUS_CLOCK_NOT_CONFIGURED 0x8000002u
#define AM_HAL_UART_STATUS_BAUDRATE_NOT_POSSIBLE 0x8000003u
#define BAUDCLK 16u
#define AM_HAL_UART_PARITY_ODD 0u
#define AM_HAL_UART_PARITY_EVEN 1u
#define AM_HAL_UART_PARITY_NONE 2u
#define UART0_CR_CLKSEL_HFRC_24MHZ 1u
#define UART0_CR_CLKSEL_HFRC_12MHZ 2u
#define UART0_CR_CLKSEL_HFRC_6MHZ 3u
#define UART0_CR_CLKSEL_HFRC_3MHZ 4u
#define UART0_CR_CLKSEL_HFRC_48MHZ 5u
#define UART0_CR_CLKSEL_PLL_CLK 6u
typedef uint32_t am_hal_pwrctrl_periph_e;
typedef uint32_t am_hal_clkmgr_user_id_e;
typedef struct {uint32_t prefix;struct {bool bValid;uint8_t pad[3];uint32_t regILPR,regIBRD,regFBRD,regLCRH,regCR,regIFLS,regIER,regDMACFG;}sRegState;uint32_t ui32Module,psDmaQueue,ui32BaudRate;uint8_t pad52[228];uint8_t eClkSrc;} am_hal_uart_state_t;
typedef struct {uint32_t ui32BaudRate;uint8_t eDataBits,eParity,eStopBits,pad7;uint16_t eFlowControl;uint8_t eTXFifoLevel,eRXFifoLevel,eClockSrc,pad13[3];} am_hal_uart_config_t;
typedef struct {uint32_t D2ASPARE;} McuRegs;
#define MCUCTRL ((volatile McuRegs *)0x400201b0)
typedef struct {uint32_t DR,RSR,other8[4],FR,other28,ILPR,IBRD,FBRD;union {uint32_t LCRH;struct {uint32_t BRK:1,PEN:1,EPS:1,STP2:1,FEN:1,WLEN:2,SPS:1,other:24;}LCRH_b;};union {uint32_t CR;struct {uint32_t UARTEN:1,other1:2,CLKEN:1,CLKSEL:3,other7:1,TXE:1,RXE:1,other10:4,RTSEN:1,CTSEN:1,other16:16;}CR_b;};union {uint32_t IFLS;struct {uint32_t TXIFLSEL:3,RXIFLSEL:3,other:26;}IFLS_b;};uint32_t IER,RIS,MIS,IEC,DCR;} UartRegs;
#define UARTn(n) ((volatile UartRegs *)(0x40039000u+0x1000u*(n)))
_Static_assert(offsetof(UartRegs,CR)==0x30,"stock CR");
_Static_assert(offsetof(UartRegs,DCR)==0x48,"stock DMA config");
_Static_assert(offsetof(am_hal_uart_state_t,eClkSrc)==0x118,"stock clock source");
_Static_assert(sizeof(am_hal_uart_config_t)==16,"stock packed enums config");
uint32_t am_hal_pwrctrl_periph_enable(am_hal_pwrctrl_periph_e);
uint32_t am_hal_pwrctrl_periph_disable(am_hal_pwrctrl_periph_e);
uint32_t am_hal_clkmgr_clock_request(uint32_t,am_hal_clkmgr_user_id_e);
uint32_t am_hal_clkmgr_clock_release(uint32_t,am_hal_clkmgr_user_id_e);
uint32_t am_hal_uart_interrupt_clear(void *,uint32_t);
static uint32_t config_baudrate(uint32_t,uint32_t,uint32_t *);
#endif
