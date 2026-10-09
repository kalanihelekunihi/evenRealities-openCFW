# 0 "/pdl/drivers/source/cy_syspm.c"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/pdl/drivers/source/cy_syspm.c"
# 26 "/pdl/drivers/source/cy_syspm.c"
# 1 "/pdl/drivers/include/cy_syspm.h" 1
# 502 "/pdl/drivers/include/cy_syspm.h"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stdbool.h" 1 3 4
# 503 "/pdl/drivers/include/cy_syspm.h" 2
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 145 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4

# 145 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
typedef int ptrdiff_t;
# 214 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
typedef unsigned int size_t;
# 329 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
typedef unsigned int wchar_t;
# 425 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
typedef struct {
  long long __max_align_ll __attribute__((__aligned__(__alignof__(long long))));
  long double __max_align_ld __attribute__((__aligned__(__alignof__(long double))));
# 436 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 3 4
} max_align_t;
# 504 "/pdl/drivers/include/cy_syspm.h" 2

# 1 "/pdl/drivers/include/cy_device.h" 1
# 32 "/pdl/drivers/include/cy_device.h"
# 1 "/pdl/devices/include/cy_device_headers.h" 1
# 1419 "/pdl/devices/include/cy_device_headers.h"
# 1 "/pdl/devices/include/cy8c4046fni_t412.h" 1
# 40 "/pdl/devices/include/cy8c4046fni_t412.h"

# 40 "/pdl/devices/include/cy8c4046fni_t412.h"
typedef enum {

  Reset_IRQn = -15,
  NonMaskableInt_IRQn = -14,
  HardFault_IRQn = -13,
  SVCall_IRQn = -5,
  PendSV_IRQn = -2,
  SysTick_IRQn = -1,

  ioss_interrupts_gpio_0_IRQn = 0,
  ioss_interrupts_gpio_1_IRQn = 1,
  ioss_interrupts_gpio_2_IRQn = 2,
  ioss_interrupts_gpio_3_IRQn = 3,
  ioss_interrupt_gpio_IRQn = 4,
  srss_interrupt_wdt_IRQn = 5,
  scb_0_interrupt_IRQn = 6,
  scb_1_interrupt_IRQn = 7,
  msclp_interrupt_lp_IRQn = 8,
  cpuss_interrupt_spcif_IRQn = 9,
  msclp_interrupt_IRQn = 10,
  tcpwm_interrupts_0_IRQn = 11,
  tcpwm_interrupts_1_IRQn = 12,
  unconnected_IRQn = 240
} IRQn_Type;
# 79 "/pdl/devices/include/cy8c4046fni_t412.h"
# 1 "/headers/cmsis/core_cm0plus.h" 1
# 34 "/headers/cmsis/core_cm0plus.h"
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stdint.h" 1 3 4
# 11 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stdint.h" 3 4
# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stdint-gcc.h" 1 3 4
# 34 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stdint-gcc.h" 3 4

# 34 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stdint-gcc.h" 3 4
typedef signed char int8_t;


typedef short int int16_t;


typedef long int int32_t;


typedef long long int int64_t;


typedef unsigned char uint8_t;


typedef short unsigned int uint16_t;


typedef long unsigned int uint32_t;


typedef long long unsigned int uint64_t;




typedef signed char int_least8_t;
typedef short int int_least16_t;
typedef long int int_least32_t;
typedef long long int int_least64_t;
typedef unsigned char uint_least8_t;
typedef short unsigned int uint_least16_t;
typedef long unsigned int uint_least32_t;
typedef long long unsigned int uint_least64_t;



typedef int int_fast8_t;
typedef int int_fast16_t;
typedef int int_fast32_t;
typedef long long int int_fast64_t;
typedef unsigned int uint_fast8_t;
typedef unsigned int uint_fast16_t;
typedef unsigned int uint_fast32_t;
typedef long long unsigned int uint_fast64_t;




typedef int intptr_t;


typedef unsigned int uintptr_t;




typedef long long int intmax_t;
typedef long long unsigned int uintmax_t;
# 12 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stdint.h" 2 3 4
# 35 "/headers/cmsis/core_cm0plus.h" 2
# 63 "/headers/cmsis/core_cm0plus.h"
# 1 "/headers/cmsis/cmsis_version.h" 1
# 64 "/headers/cmsis/core_cm0plus.h" 2
# 115 "/headers/cmsis/core_cm0plus.h"
# 1 "/headers/cmsis/cmsis_compiler.h" 1
# 54 "/headers/cmsis/cmsis_compiler.h"
# 1 "/headers/cmsis/cmsis_gcc.h" 1
# 29 "/headers/cmsis/cmsis_gcc.h"
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsign-conversion"
#pragma GCC diagnostic ignored "-Wconversion"
#pragma GCC diagnostic ignored "-Wunused-parameter"
# 71 "/headers/cmsis/cmsis_gcc.h"
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpacked"
#pragma GCC diagnostic ignored "-Wattributes"
  struct __attribute__((packed)) T_UINT32 { uint32_t v; };
#pragma GCC diagnostic pop



#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpacked"
#pragma GCC diagnostic ignored "-Wattributes"
  struct __attribute__((packed, aligned(1))) T_UINT16_WRITE { uint16_t v; };
#pragma GCC diagnostic pop



#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpacked"
#pragma GCC diagnostic ignored "-Wattributes"
  struct __attribute__((packed, aligned(1))) T_UINT16_READ { uint16_t v; };
#pragma GCC diagnostic pop



#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpacked"
#pragma GCC diagnostic ignored "-Wattributes"
  struct __attribute__((packed, aligned(1))) T_UINT32_WRITE { uint32_t v; };
#pragma GCC diagnostic pop



#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpacked"
#pragma GCC diagnostic ignored "-Wattributes"
  struct __attribute__((packed, aligned(1))) T_UINT32_READ { uint32_t v; };
#pragma GCC diagnostic pop
# 131 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline __attribute__((__noreturn__)) void __cmsis_start(void)
{
  extern void _start(void) __attribute__((__noreturn__));

  typedef struct {
    uint32_t const* src;
    uint32_t* dest;
    uint32_t wlen;
  } __copy_table_t;

  typedef struct {
    uint32_t* dest;
    uint32_t wlen;
  } __zero_table_t;

  extern const __copy_table_t __copy_table_start__;
  extern const __copy_table_t __copy_table_end__;
  extern const __zero_table_t __zero_table_start__;
  extern const __zero_table_t __zero_table_end__;

  for (__copy_table_t const* pTable = &__copy_table_start__; pTable < &__copy_table_end__; ++pTable) {
    for(uint32_t i=0u; i<pTable->wlen; ++i) {
      pTable->dest[i] = pTable->src[i];
    }
  }

  for (__zero_table_t const* pTable = &__zero_table_start__; pTable < &__zero_table_end__; ++pTable) {
    for(uint32_t i=0u; i<pTable->wlen; ++i) {
      pTable->dest[i] = 0u;
    }
  }

  _start();
}
# 258 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline void __ISB(void)
{
  __asm volatile ("isb 0xF":::"memory");
}







__attribute__((always_inline)) static inline void __DSB(void)
{
  __asm volatile ("dsb 0xF":::"memory");
}







__attribute__((always_inline)) static inline void __DMB(void)
{
  __asm volatile ("dmb 0xF":::"memory");
}
# 292 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline uint32_t __REV(uint32_t value)
{

  return __builtin_bswap32(value);






}
# 311 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline uint32_t __REV16(uint32_t value)
{
  uint32_t result;

  __asm ("rev16 %0, %1" : "=l" (result) : "l" (value) );
  return result;
}
# 326 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline int16_t __REVSH(int16_t value)
{

  return (int16_t)__builtin_bswap16(value);






}
# 346 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline uint32_t __ROR(uint32_t op1, uint32_t op2)
{
  op2 %= 32U;
  if (op2 == 0U)
  {
    return op1;
  }
  return (op1 >> op2) | (op1 << (32U - op2));
}
# 373 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline uint32_t __RBIT(uint32_t value)
{
  uint32_t result;






  uint32_t s = (4U * 8U) - 1U;

  result = value;
  for (value >>= 1U; value != 0U; value >>= 1U)
  {
    result <<= 1U;
    result |= value & 1U;
    s--;
  }
  result <<= s;

  return result;
}
# 403 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline uint8_t __CLZ(uint32_t value)
{
# 414 "/headers/cmsis/cmsis_gcc.h"
  if (value == 0U)
  {
    return 32U;
  }
  return __builtin_clz(value);
}
# 707 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline int32_t __SSAT(int32_t val, uint32_t sat)
{
  if ((sat >= 1U) && (sat <= 32U))
  {
    const int32_t max = (int32_t)((1U << (sat - 1U)) - 1U);
    const int32_t min = -1 - max ;
    if (val > max)
    {
      return max;
    }
    else if (val < min)
    {
      return min;
    }
  }
  return val;
}
# 732 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline uint32_t __USAT(int32_t val, uint32_t sat)
{
  if (sat <= 31U)
  {
    const uint32_t max = ((1U << sat) - 1U);
    if (val > (int32_t)max)
    {
      return max;
    }
    else if (val < 0)
    {
      return 0U;
    }
  }
  return (uint32_t)val;
}
# 949 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline void __enable_irq(void)
{
  __asm volatile ("cpsie i" : : : "memory");
}







__attribute__((always_inline)) static inline void __disable_irq(void)
{
  __asm volatile ("cpsid i" : : : "memory");
}







__attribute__((always_inline)) static inline uint32_t __get_CONTROL(void)
{
  uint32_t result;

  __asm volatile ("MRS %0, control" : "=r" (result) );
  return(result);
}
# 1001 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline void __set_CONTROL(uint32_t control)
{
  __asm volatile ("MSR control, %0" : : "r" (control) : "memory");
  __ISB();
}
# 1027 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline uint32_t __get_IPSR(void)
{
  uint32_t result;

  __asm volatile ("MRS %0, ipsr" : "=r" (result) );
  return(result);
}







__attribute__((always_inline)) static inline uint32_t __get_APSR(void)
{
  uint32_t result;

  __asm volatile ("MRS %0, apsr" : "=r" (result) );
  return(result);
}







__attribute__((always_inline)) static inline uint32_t __get_xPSR(void)
{
  uint32_t result;

  __asm volatile ("MRS %0, xpsr" : "=r" (result) );
  return(result);
}







__attribute__((always_inline)) static inline uint32_t __get_PSP(void)
{
  uint32_t result;

  __asm volatile ("MRS %0, psp" : "=r" (result) );
  return(result);
}
# 1099 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline void __set_PSP(uint32_t topOfProcStack)
{
  __asm volatile ("MSR psp, %0" : : "r" (topOfProcStack) : );
}
# 1123 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline uint32_t __get_MSP(void)
{
  uint32_t result;

  __asm volatile ("MRS %0, msp" : "=r" (result) );
  return(result);
}
# 1153 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline void __set_MSP(uint32_t topOfMainStack)
{
  __asm volatile ("MSR msp, %0" : : "r" (topOfMainStack) : );
}
# 1204 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline uint32_t __get_PRIMASK(void)
{
  uint32_t result;

  __asm volatile ("MRS %0, primask" : "=r" (result) );
  return(result);
}
# 1234 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline void __set_PRIMASK(uint32_t priMask)
{
  __asm volatile ("MSR primask, %0" : : "r" (priMask) : "memory");
}
# 1588 "/headers/cmsis/cmsis_gcc.h"
__attribute__((always_inline)) static inline uint32_t __get_FPSCR(void)
{
# 1604 "/headers/cmsis/cmsis_gcc.h"
  return(0U);

}







__attribute__((always_inline)) static inline void __set_FPSCR(uint32_t fpscr)
{
# 1627 "/headers/cmsis/cmsis_gcc.h"
  (void)fpscr;

}
# 2209 "/headers/cmsis/cmsis_gcc.h"
#pragma GCC diagnostic pop
# 55 "/headers/cmsis/cmsis_compiler.h" 2
# 116 "/headers/cmsis/core_cm0plus.h" 2
# 210 "/headers/cmsis/core_cm0plus.h"
typedef union
{
  struct
  {
    uint32_t _reserved0:28;
    uint32_t V:1;
    uint32_t C:1;
    uint32_t Z:1;
    uint32_t N:1;
  } b;
  uint32_t w;
} APSR_Type;
# 240 "/headers/cmsis/core_cm0plus.h"
typedef union
{
  struct
  {
    uint32_t ISR:9;
    uint32_t _reserved0:23;
  } b;
  uint32_t w;
} IPSR_Type;
# 258 "/headers/cmsis/core_cm0plus.h"
typedef union
{
  struct
  {
    uint32_t ISR:9;
    uint32_t _reserved0:15;
    uint32_t T:1;
    uint32_t _reserved1:3;
    uint32_t V:1;
    uint32_t C:1;
    uint32_t Z:1;
    uint32_t N:1;
  } b;
  uint32_t w;
} xPSR_Type;
# 297 "/headers/cmsis/core_cm0plus.h"
typedef union
{
  struct
  {
    uint32_t nPRIV:1;
    uint32_t SPSEL:1;
    uint32_t _reserved1:30;
  } b;
  uint32_t w;
} CONTROL_Type;
# 328 "/headers/cmsis/core_cm0plus.h"
typedef struct
{
  volatile uint32_t ISER[1U];
        uint32_t RESERVED0[31U];
  volatile uint32_t ICER[1U];
        uint32_t RESERVED1[31U];
  volatile uint32_t ISPR[1U];
        uint32_t RESERVED2[31U];
  volatile uint32_t ICPR[1U];
        uint32_t RESERVED3[31U];
        uint32_t RESERVED4[64U];
  volatile uint32_t IP[8U];
} NVIC_Type;
# 355 "/headers/cmsis/core_cm0plus.h"
typedef struct
{
  volatile const uint32_t CPUID;
  volatile uint32_t ICSR;

  volatile uint32_t VTOR;



  volatile uint32_t AIRCR;
  volatile uint32_t SCR;
  volatile uint32_t CCR;
        uint32_t RESERVED1;
  volatile uint32_t SHP[2U];
  volatile uint32_t SHCSR;
} SCB_Type;
# 472 "/headers/cmsis/core_cm0plus.h"
typedef struct
{
  volatile uint32_t CTRL;
  volatile uint32_t LOAD;
  volatile uint32_t VAL;
  volatile const uint32_t CALIB;
} SysTick_Type;
# 741 "/headers/cmsis/core_cm0plus.h"
static inline void __NVIC_EnableIRQ(IRQn_Type IRQn)
{
  if ((int32_t)(IRQn) >= 0)
  {
    __asm volatile("":::"memory");
    ((NVIC_Type *) ((0xE000E000UL) + 0x0100UL) )->ISER[0U] = (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
    __asm volatile("":::"memory");
  }
}
# 760 "/headers/cmsis/core_cm0plus.h"
static inline uint32_t __NVIC_GetEnableIRQ(IRQn_Type IRQn)
{
  if ((int32_t)(IRQn) >= 0)
  {
    return((uint32_t)(((((NVIC_Type *) ((0xE000E000UL) + 0x0100UL) )->ISER[0U] & (1UL << (((uint32_t)IRQn) & 0x1FUL))) != 0UL) ? 1UL : 0UL));
  }
  else
  {
    return(0U);
  }
}
# 779 "/headers/cmsis/core_cm0plus.h"
static inline void __NVIC_DisableIRQ(IRQn_Type IRQn)
{
  if ((int32_t)(IRQn) >= 0)
  {
    ((NVIC_Type *) ((0xE000E000UL) + 0x0100UL) )->ICER[0U] = (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
    __DSB();
    __ISB();
  }
}
# 798 "/headers/cmsis/core_cm0plus.h"
static inline uint32_t __NVIC_GetPendingIRQ(IRQn_Type IRQn)
{
  if ((int32_t)(IRQn) >= 0)
  {
    return((uint32_t)(((((NVIC_Type *) ((0xE000E000UL) + 0x0100UL) )->ISPR[0U] & (1UL << (((uint32_t)IRQn) & 0x1FUL))) != 0UL) ? 1UL : 0UL));
  }
  else
  {
    return(0U);
  }
}
# 817 "/headers/cmsis/core_cm0plus.h"
static inline void __NVIC_SetPendingIRQ(IRQn_Type IRQn)
{
  if ((int32_t)(IRQn) >= 0)
  {
    ((NVIC_Type *) ((0xE000E000UL) + 0x0100UL) )->ISPR[0U] = (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
  }
}
# 832 "/headers/cmsis/core_cm0plus.h"
static inline void __NVIC_ClearPendingIRQ(IRQn_Type IRQn)
{
  if ((int32_t)(IRQn) >= 0)
  {
    ((NVIC_Type *) ((0xE000E000UL) + 0x0100UL) )->ICPR[0U] = (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
  }
}
# 850 "/headers/cmsis/core_cm0plus.h"
static inline void __NVIC_SetPriority(IRQn_Type IRQn, uint32_t priority)
{
  if ((int32_t)(IRQn) >= 0)
  {
    ((NVIC_Type *) ((0xE000E000UL) + 0x0100UL) )->IP[( (((uint32_t)(int32_t)(IRQn)) >> 2UL) )] = ((uint32_t)(((NVIC_Type *) ((0xE000E000UL) + 0x0100UL) )->IP[( (((uint32_t)(int32_t)(IRQn)) >> 2UL) )] & ~(0xFFUL << ( ((((uint32_t)(int32_t)(IRQn)) ) & 0x03UL) * 8UL))) |
       (((priority << (8U - 2)) & (uint32_t)0xFFUL) << ( ((((uint32_t)(int32_t)(IRQn)) ) & 0x03UL) * 8UL)));
  }
  else
  {
    ((SCB_Type *) ((0xE000E000UL) + 0x0D00UL) )->SHP[( (((((uint32_t)(int32_t)(IRQn)) & 0x0FUL)-8UL) >> 2UL) )] = ((uint32_t)(((SCB_Type *) ((0xE000E000UL) + 0x0D00UL) )->SHP[( (((((uint32_t)(int32_t)(IRQn)) & 0x0FUL)-8UL) >> 2UL) )] & ~(0xFFUL << ( ((((uint32_t)(int32_t)(IRQn)) ) & 0x03UL) * 8UL))) |
       (((priority << (8U - 2)) & (uint32_t)0xFFUL) << ( ((((uint32_t)(int32_t)(IRQn)) ) & 0x03UL) * 8UL)));
  }
}
# 874 "/headers/cmsis/core_cm0plus.h"
static inline uint32_t __NVIC_GetPriority(IRQn_Type IRQn)
{

  if ((int32_t)(IRQn) >= 0)
  {
    return((uint32_t)(((((NVIC_Type *) ((0xE000E000UL) + 0x0100UL) )->IP[ ( (((uint32_t)(int32_t)(IRQn)) >> 2UL) )] >> ( ((((uint32_t)(int32_t)(IRQn)) ) & 0x03UL) * 8UL) ) & (uint32_t)0xFFUL) >> (8U - 2)));
  }
  else
  {
    return((uint32_t)(((((SCB_Type *) ((0xE000E000UL) + 0x0D00UL) )->SHP[( (((((uint32_t)(int32_t)(IRQn)) & 0x0FUL)-8UL) >> 2UL) )] >> ( ((((uint32_t)(int32_t)(IRQn)) ) & 0x03UL) * 8UL) ) & (uint32_t)0xFFUL) >> (8U - 2)));
  }
}
# 899 "/headers/cmsis/core_cm0plus.h"
static inline uint32_t NVIC_EncodePriority (uint32_t PriorityGroup, uint32_t PreemptPriority, uint32_t SubPriority)
{
  uint32_t PriorityGroupTmp = (PriorityGroup & (uint32_t)0x07UL);
  uint32_t PreemptPriorityBits;
  uint32_t SubPriorityBits;

  PreemptPriorityBits = ((7UL - PriorityGroupTmp) > (uint32_t)(2)) ? (uint32_t)(2) : (uint32_t)(7UL - PriorityGroupTmp);
  SubPriorityBits = ((PriorityGroupTmp + (uint32_t)(2)) < (uint32_t)7UL) ? (uint32_t)0UL : (uint32_t)((PriorityGroupTmp - 7UL) + (uint32_t)(2));

  return (
           ((PreemptPriority & (uint32_t)((1UL << (PreemptPriorityBits)) - 1UL)) << SubPriorityBits) |
           ((SubPriority & (uint32_t)((1UL << (SubPriorityBits )) - 1UL)))
         );
}
# 926 "/headers/cmsis/core_cm0plus.h"
static inline void NVIC_DecodePriority (uint32_t Priority, uint32_t PriorityGroup, uint32_t* const pPreemptPriority, uint32_t* const pSubPriority)
{
  uint32_t PriorityGroupTmp = (PriorityGroup & (uint32_t)0x07UL);
  uint32_t PreemptPriorityBits;
  uint32_t SubPriorityBits;

  PreemptPriorityBits = ((7UL - PriorityGroupTmp) > (uint32_t)(2)) ? (uint32_t)(2) : (uint32_t)(7UL - PriorityGroupTmp);
  SubPriorityBits = ((PriorityGroupTmp + (uint32_t)(2)) < (uint32_t)7UL) ? (uint32_t)0UL : (uint32_t)((PriorityGroupTmp - 7UL) + (uint32_t)(2));

  *pPreemptPriority = (Priority >> SubPriorityBits) & (uint32_t)((1UL << (PreemptPriorityBits)) - 1UL);
  *pSubPriority = (Priority ) & (uint32_t)((1UL << (SubPriorityBits )) - 1UL);
}
# 950 "/headers/cmsis/core_cm0plus.h"
static inline void __NVIC_SetVector(IRQn_Type IRQn, uint32_t vector)
{

  uint32_t *vectors = (uint32_t *)((SCB_Type *) ((0xE000E000UL) + 0x0D00UL) )->VTOR;
  vectors[(int32_t)IRQn + 16] = vector;





}
# 971 "/headers/cmsis/core_cm0plus.h"
static inline uint32_t __NVIC_GetVector(IRQn_Type IRQn)
{

  uint32_t *vectors = (uint32_t *)((SCB_Type *) ((0xE000E000UL) + 0x0D00UL) )->VTOR;
  return vectors[(int32_t)IRQn + 16];




}






__attribute__((__noreturn__)) static inline void __NVIC_SystemReset(void)
{
  __DSB();

  ((SCB_Type *) ((0xE000E000UL) + 0x0D00UL) )->AIRCR = ((0x5FAUL << 16U) |
                 (1UL << 2U));
  __DSB();

  for(;;)
  {
    __asm volatile ("nop");
  }
}
# 1027 "/headers/cmsis/core_cm0plus.h"
static inline uint32_t SCB_GetFPUType(void)
{
    return 0U;
}
# 1058 "/headers/cmsis/core_cm0plus.h"
static inline uint32_t SysTick_Config(uint32_t ticks)
{
  if ((ticks - 1UL) > (0xFFFFFFUL ))
  {
    return (1UL);
  }

  ((SysTick_Type *) ((0xE000E000UL) + 0x0010UL) )->LOAD = (uint32_t)(ticks - 1UL);
  __NVIC_SetPriority (SysTick_IRQn, (1UL << 2) - 1UL);
  ((SysTick_Type *) ((0xE000E000UL) + 0x0010UL) )->VAL = 0UL;
  ((SysTick_Type *) ((0xE000E000UL) + 0x0010UL) )->CTRL = (1UL << 2U) |
                   (1UL << 1U) |
                   (1UL );
  return (0UL);
}
# 80 "/pdl/devices/include/cy8c4046fni_t412.h" 2
# 128 "/pdl/devices/include/cy8c4046fni_t412.h"
# 1 "/interface/system_cat2.h" 1
# 273 "/interface/system_cat2.h"
    extern void SystemInit(void);


extern void Cy_SystemInit(void);

extern void SystemCoreClockUpdate(void);



extern void Default_Handler (void);

extern void Cy_OnResetUser(void);
extern void Cy_BootStatus(void);

extern uint32_t cy_delayFreqKhz;
extern uint8_t cy_delayFreqMhz;
extern uint32_t cy_delay32kMs;


typedef void (* cy_israddress)(void);


extern cy_israddress __RAM_VECTOR_TABLE[(48U)];
extern const cy_israddress __Vectors[(48U)];
# 305 "/interface/system_cat2.h"
extern uint32_t SystemCoreClock;
# 129 "/pdl/devices/include/cy8c4046fni_t412.h" 2

# 1 "/pdl/devices/include/psoc4000t_config.h" 1
# 27 "/pdl/devices/include/psoc4000t_config.h"
typedef enum
{
    PCLK_SCB0_CLOCK = 0x0000u,
    PCLK_SCB1_CLOCK = 0x0001u,
    PCLK_TCPWM_CLOCKS0 = 0x0002u,
    PCLK_TCPWM_CLOCKS1 = 0x0003u
} en_clk_dst_t;







typedef enum
{
    TRIG0_IN_CPUSS_ZERO = 0x00000000u,
    TRIG0_IN_TCPWM_TR_OVERFLOW0 = 0x00000001u,
    TRIG0_IN_TCPWM_TR_OVERFLOW1 = 0x00000002u,
    TRIG0_IN_TCPWM_TR_COMPARE_MATCH0 = 0x00000003u,
    TRIG0_IN_TCPWM_TR_COMPARE_MATCH1 = 0x00000004u,
    TRIG0_IN_TCPWM_TR_UNDERFLOW0 = 0x00000005u,
    TRIG0_IN_TCPWM_TR_UNDERFLOW1 = 0x00000006u,
    TRIG0_IN_SCB0_TR_I2C_SCL_FILTERED = 0x00000007u,
    TRIG0_IN_SCB1_TR_I2C_SCL_FILTERED = 0x00000008u
} en_trig_input_grp0_t;



typedef enum
{
    TRIG0_OUT_TCPWM_TR_IN7 = 0x40000000u,
    TRIG0_OUT_TCPWM_TR_IN8 = 0x40000001u,
    TRIG0_OUT_TCPWM_TR_IN9 = 0x40000002u,
    TRIG0_OUT_TCPWM_TR_IN10 = 0x40000003u,
    TRIG0_OUT_TCPWM_TR_IN11 = 0x40000004u,
    TRIG0_OUT_TCPWM_TR_IN12 = 0x40000005u,
    TRIG0_OUT_TCPWM_TR_IN13 = 0x40000006u
} en_trig_output_grp0_t;


# 1 "/pdl/devices/include/ip/cyip_sflash_psoc4000t.h" 1
# 26 "/pdl/devices/include/ip/cyip_sflash_psoc4000t.h"
# 1 "/pdl/devices/include/ip/cyip_headers.h" 1
# 27 "/pdl/devices/include/ip/cyip_sflash_psoc4000t.h" 2
# 37 "/pdl/devices/include/ip/cyip_sflash_psoc4000t.h"
typedef struct {
   volatile const uint8_t RESERVED[139];
  volatile uint8_t MSCLP_TRIM_CTL_46;
  volatile uint8_t MSCLP_CLK_IMO_TRIM1_46;
  volatile uint8_t MSCLP_CLK_IMO_TRIM2_46;
  volatile uint8_t MSCLP_CLK_IMO_TRIM3_46;
   volatile const uint8_t RESERVED1[5];
  volatile uint8_t MSCLP_TRIM_CTL_38;
  volatile uint8_t MSCLP_CLK_IMO_TRIM1_38;
  volatile uint8_t MSCLP_CLK_IMO_TRIM2_38;
  volatile uint8_t MSCLP_CLK_IMO_TRIM3_38;
   volatile const uint8_t RESERVED2[5];
  volatile uint8_t MSCLP_TRIM_CTL_25;
  volatile uint8_t MSCLP_CLK_IMO_TRIM1_25;
  volatile uint8_t MSCLP_CLK_IMO_TRIM2_25;
  volatile uint8_t MSCLP_CLK_IMO_TRIM3_25;
   volatile const uint8_t RESERVED3[26];
  volatile uint8_t CREF_COEFF0;
  volatile uint8_t CREF_COEFF1;
  volatile uint8_t CFINE_COEFF0;
  volatile uint8_t CFINE_COEFF1;
   volatile const uint8_t RESERVED4[133];
  volatile uint32_t SILICON_ID;
   volatile const uint32_t RESERVED5[2];
  volatile uint16_t HIB_KEY_DELAY;
  volatile uint16_t DPSLP_KEY_DELAY;
  volatile uint8_t SWD_CONFIG;
   volatile const uint8_t RESERVED6[3];
  volatile uint32_t SWD_LISTEN;
  volatile uint32_t FLASH_START;
   volatile const uint16_t RESERVED7[47];
  volatile uint8_t IMO_TRIM_USBMODE_24;
  volatile uint8_t IMO_TRIM_USBMODE_48;
   volatile const uint32_t RESERVED8[3];
  volatile uint8_t IMO_TCTRIM_LT[25];
  volatile uint8_t IMO_TRIM_LT[25];
} SFLASH_Type;
# 69 "/pdl/devices/include/psoc4000t_config.h" 2
# 1 "/pdl/devices/include/ip/cyip_peri.h" 1
# 38 "/pdl/devices/include/ip/cyip_peri.h"
typedef struct {
  volatile uint32_t TR_OUT_CTL[128];
} PERI_TR_GROUP_Type;




typedef struct {
  volatile uint32_t DIV_CMD;
   volatile const uint32_t RESERVED[63];
  volatile uint32_t PCLK_CTL[64];
  volatile uint32_t DIV_8_CTL[64];
  volatile uint32_t DIV_16_CTL[64];
  volatile uint32_t DIV_16_5_CTL[64];
  volatile uint32_t DIV_24_5_CTL[63];
   volatile const uint32_t RESERVED1;
  volatile uint32_t TR_CTL;
   volatile const uint32_t RESERVED2[1663];
        PERI_TR_GROUP_Type TR_GROUP[16];
} PERI_Type;
# 70 "/pdl/devices/include/psoc4000t_config.h" 2
# 1 "/pdl/devices/include/ip/cyip_hsiom.h" 1
# 38 "/pdl/devices/include/ip/cyip_hsiom.h"
typedef struct {
  volatile uint32_t PORT_SEL;
   volatile const uint32_t RESERVED[63];
} HSIOM_PRT_Type;




typedef struct {
        HSIOM_PRT_Type PRT[16];
   volatile const uint32_t RESERVED[1024];
  volatile uint32_t PUMP_CTL;
   volatile const uint32_t RESERVED1[63];
  volatile uint32_t AMUX_SPLIT_CTL[8];
} HSIOM_Type;
# 71 "/pdl/devices/include/psoc4000t_config.h" 2
# 1 "/pdl/devices/include/ip/cyip_srsslt.h" 1
# 37 "/pdl/devices/include/ip/cyip_srsslt.h"
typedef struct {
  volatile uint32_t PWR_CONTROL;
  volatile uint32_t PWR_KEY_DELAY;
   volatile const uint32_t RESERVED;
  volatile uint32_t PWR_DDFT_SELECT;
   volatile const uint32_t RESERVED1;
  volatile uint32_t TST_MODE;
   volatile const uint32_t RESERVED2[4];
  volatile uint32_t CLK_SELECT;
  volatile uint32_t CLK_ILO_CONFIG;
  volatile uint32_t CLK_IMO_CONFIG;
  volatile uint32_t CLK_DFT_SELECT;
  volatile uint32_t WDT_DISABLE_KEY;
   volatile const uint32_t WDT_COUNTER;
  volatile uint32_t WDT_MATCH;
  volatile uint32_t SRSS_INTR;
  volatile uint32_t SRSS_INTR_SET;
  volatile uint32_t SRSS_INTR_MASK;
   volatile const uint32_t RESERVED3;
  volatile uint32_t RES_CAUSE;
   volatile const uint32_t RESERVED4[940];
  volatile uint32_t CLK_IMO_SELECT;
  volatile uint32_t CLK_IMO_TRIM1;
  volatile uint32_t CLK_IMO_TRIM2;
  volatile uint32_t PWR_PWRSYS_TRIM1;
  volatile uint32_t CLK_IMO_TRIM3;
} SRSSLT_Type;
# 72 "/pdl/devices/include/psoc4000t_config.h" 2
# 1 "/pdl/devices/include/ip/cyip_gpio.h" 1
# 38 "/pdl/devices/include/ip/cyip_gpio.h"
typedef struct {
  volatile uint32_t DR;
   volatile const uint32_t PS;
  volatile uint32_t PC;
  volatile uint32_t INTR_CFG;
  volatile uint32_t INTR;
  volatile uint32_t SIO;
  volatile uint32_t PC2;
   volatile const uint32_t RESERVED[2];
  volatile uint32_t MSC_ANA;
   volatile const uint32_t RESERVED1[6];
  volatile uint32_t DR_SET;
  volatile uint32_t DR_CLR;
  volatile uint32_t DR_INV;
  volatile uint32_t DS;
  volatile uint32_t FILT_CONFIG;
   volatile const uint32_t RESERVED2[11];
  volatile uint32_t VREFGEN;
   volatile const uint32_t RESERVED3[31];
} GPIO_PRT_Type;




typedef struct {
        GPIO_PRT_Type PRT[16];
   volatile const uint32_t INTR_CAUSE;
   volatile const uint32_t RESERVED[3];
  volatile uint32_t DFT_IO_TEST;
   volatile const uint32_t RESERVED1[3];
   volatile const uint32_t GPIOV1P2_DET;
} GPIO_Type;
# 73 "/pdl/devices/include/psoc4000t_config.h" 2
# 1 "/pdl/devices/include/ip/cyip_cpuss_v3.h" 1
# 37 "/pdl/devices/include/ip/cyip_cpuss_v3.h"
typedef struct {
  volatile uint32_t CONFIG;
  volatile uint32_t SYSREQ;
  volatile uint32_t SYSARG;
  volatile uint32_t PROTECTION;
  volatile uint32_t PRIV_ROM;
  volatile uint32_t PRIV_RAM;
  volatile uint32_t PRIV_FLASH;
  volatile uint32_t WOUNDING;
  volatile uint32_t INT_SEL;
  volatile uint32_t INT_MODE;
  volatile uint32_t NMI_MODE;
   volatile const uint32_t RESERVED;
  volatile uint32_t FLASH_CTL;
  volatile uint32_t ROM_CTL;
  volatile uint32_t RAM_CTL;
  volatile uint32_t DMAC_CTL;
   volatile const uint32_t RESERVED1[24];
  volatile uint32_t PRIV_RAM1;
  volatile uint32_t RAM1_CTL;
   volatile const uint32_t RESERVED2[2];
  volatile uint32_t MTB_CTL;
   volatile const uint32_t RESERVED3[19];
  volatile uint32_t SL_CTL[24];
} CPUSS_Type;
# 74 "/pdl/devices/include/psoc4000t_config.h" 2
# 1 "/pdl/devices/include/ip/cyip_dmac_v3.h" 1
# 38 "/pdl/devices/include/ip/cyip_dmac_v3.h"
typedef struct {
  volatile uint32_t PING_SRC;
  volatile uint32_t PING_DST;
  volatile uint32_t PING_CTL;
  volatile uint32_t PING_STATUS;
  volatile uint32_t PONG_SRC;
  volatile uint32_t PONG_DST;
  volatile uint32_t PONG_CTL;
  volatile uint32_t PONG_STATUS;
} DMAC_DESCR_Type;




typedef struct {
  volatile uint32_t CTL;
   volatile const uint32_t RESERVED[3];
   volatile const uint32_t STATUS;
   volatile const uint32_t STATUS_SRC_ADDR;
   volatile const uint32_t STATUS_DST_ADDR;
   volatile const uint32_t STATUS_CH_ACT;
   volatile const uint32_t RESERVED1[24];
  volatile uint32_t CH_CTL[32];
   volatile const uint32_t RESERVED2[444];
  volatile uint32_t INTR;
  volatile uint32_t INTR_SET;
  volatile uint32_t INTR_MASK;
   volatile const uint32_t INTR_MASKED;
        DMAC_DESCR_Type DESCR[32];
} DMAC_Type;
# 75 "/pdl/devices/include/psoc4000t_config.h" 2
# 1 "/pdl/devices/include/ip/cyip_spcif_v3.h" 1
# 37 "/pdl/devices/include/ip/cyip_spcif_v3.h"
typedef struct {
  volatile uint32_t GEOMETRY;
   volatile const uint32_t RESERVED[6];
  volatile uint32_t NVL_WR_DATA;
   volatile const uint32_t RESERVED1[500];
  volatile uint32_t INTR;
  volatile uint32_t INTR_SET;
  volatile uint32_t INTR_MASK;
   volatile const uint32_t INTR_MASKED;
} SPCIF_Type;
# 76 "/pdl/devices/include/psoc4000t_config.h" 2
# 1 "/pdl/devices/include/ip/cyip_tcpwm_v2.h" 1
# 38 "/pdl/devices/include/ip/cyip_tcpwm_v2.h"
typedef struct {
  volatile uint32_t CTRL;
   volatile const uint32_t STATUS;
  volatile uint32_t COUNTER;
  volatile uint32_t CC;
  volatile uint32_t CC_BUFF;
  volatile uint32_t PERIOD;
  volatile uint32_t PERIOD_BUFF;
   volatile const uint32_t RESERVED;
  volatile uint32_t TR_CTRL0;
  volatile uint32_t TR_CTRL1;
  volatile uint32_t TR_CTRL2;
   volatile const uint32_t RESERVED1;
  volatile uint32_t INTR;
  volatile uint32_t INTR_SET;
  volatile uint32_t INTR_MASK;
   volatile const uint32_t INTR_MASKED;
} TCPWM_CNT_Type;




typedef struct {
  volatile uint32_t CTRL;
   volatile const uint32_t RESERVED;
  volatile uint32_t CMD;
   volatile const uint32_t INTR_CAUSE;
   volatile const uint32_t RESERVED1[60];
        TCPWM_CNT_Type CNT[8];
} TCPWM_Type;
# 77 "/pdl/devices/include/psoc4000t_config.h" 2
# 1 "/pdl/devices/include/ip/cyip_scb_v3.h" 1
# 37 "/pdl/devices/include/ip/cyip_scb_v3.h"
typedef struct {
  volatile uint32_t CTRL;
   volatile const uint32_t STATUS;
  volatile uint32_t CMD_RESP_CTRL;
   volatile const uint32_t CMD_RESP_STATUS;
   volatile const uint32_t RESERVED[4];
  volatile uint32_t SPI_CTRL;
   volatile const uint32_t SPI_STATUS;
  volatile uint32_t SPI_TX_CTRL;
  volatile uint32_t SPI_RX_CTRL;
   volatile const uint32_t RESERVED1[4];
  volatile uint32_t UART_CTRL;
  volatile uint32_t UART_TX_CTRL;
  volatile uint32_t UART_RX_CTRL;
   volatile const uint32_t UART_RX_STATUS;
  volatile uint32_t UART_FLOW_CTRL;
   volatile const uint32_t RESERVED2[3];
  volatile uint32_t I2C_CTRL;
   volatile const uint32_t I2C_STATUS;
  volatile uint32_t I2C_M_CMD;
  volatile uint32_t I2C_S_CMD;
  volatile uint32_t I2C_CFG;
  volatile uint32_t I2C_STRETCH_CTRL;
   volatile const uint32_t I2C_STRETCH_STATUS;
   volatile const uint32_t RESERVED3;
  volatile uint32_t I2C_CTRL_HS;
   volatile const uint32_t RESERVED4[95];
  volatile uint32_t TX_CTRL;
  volatile uint32_t TX_FIFO_CTRL;
   volatile const uint32_t TX_FIFO_STATUS;
   volatile const uint32_t RESERVED5[13];
   volatile uint32_t TX_FIFO_WR;
   volatile const uint32_t RESERVED6[47];
  volatile uint32_t RX_CTRL;
  volatile uint32_t RX_FIFO_CTRL;
   volatile const uint32_t RX_FIFO_STATUS;
   volatile const uint32_t RESERVED7;
  volatile uint32_t RX_MATCH;
   volatile const uint32_t RESERVED8[11];
   volatile const uint32_t RX_FIFO_RD;
   volatile const uint32_t RX_FIFO_RD_SILENT;
   volatile const uint32_t RESERVED9[46];
  volatile uint32_t EZ_DATA[512];
   volatile const uint32_t RESERVED10[128];
   volatile const uint32_t INTR_CAUSE;
   volatile const uint32_t RESERVED11[31];
  volatile uint32_t INTR_I2C_EC;
   volatile const uint32_t RESERVED12;
  volatile uint32_t INTR_I2C_EC_MASK;
   volatile const uint32_t INTR_I2C_EC_MASKED;
   volatile const uint32_t RESERVED13[12];
  volatile uint32_t INTR_SPI_EC;
   volatile const uint32_t RESERVED14;
  volatile uint32_t INTR_SPI_EC_MASK;
   volatile const uint32_t INTR_SPI_EC_MASKED;
   volatile const uint32_t RESERVED15[12];
  volatile uint32_t INTR_M;
  volatile uint32_t INTR_M_SET;
  volatile uint32_t INTR_M_MASK;
   volatile const uint32_t INTR_M_MASKED;
   volatile const uint32_t RESERVED16[12];
  volatile uint32_t INTR_S;
  volatile uint32_t INTR_S_SET;
  volatile uint32_t INTR_S_MASK;
   volatile const uint32_t INTR_S_MASKED;
   volatile const uint32_t RESERVED17[12];
  volatile uint32_t INTR_TX;
  volatile uint32_t INTR_TX_SET;
  volatile uint32_t INTR_TX_MASK;
   volatile const uint32_t INTR_TX_MASKED;
   volatile const uint32_t RESERVED18[12];
  volatile uint32_t INTR_RX;
  volatile uint32_t INTR_RX_SET;
  volatile uint32_t INTR_RX_MASK;
   volatile const uint32_t INTR_RX_MASKED;
} CySCB_Type;
# 78 "/pdl/devices/include/psoc4000t_config.h" 2
# 1 "/pdl/devices/include/ip/cyip_msclp.h" 1
# 39 "/pdl/devices/include/ip/cyip_msclp.h"
typedef struct {
  volatile uint32_t SENSE_DUTY_CTL;
  volatile uint32_t SW_SEL_CDAC_FL;
  volatile uint32_t SW_SEL_TOP;
  volatile uint32_t SW_SEL_COMP;
  volatile uint32_t SW_SEL_SH;
  volatile uint32_t SW_SEL_CMOD1;
  volatile uint32_t SW_SEL_CMOD2;
   volatile const uint32_t RESERVED;
  volatile uint32_t SW_SEL_CMOD3;
  volatile uint32_t SW_SEL_CMOD4;
   volatile const uint32_t RESERVED1[6];
} MSCLP_MODE_Type;




typedef struct {
  volatile uint32_t SENSOR_DATA[1024];
  volatile uint32_t SNS_LP_AOS_SNS_CTL0;
  volatile uint32_t SNS_LP_AOS_SNS_CTL1;
  volatile uint32_t SNS_LP_AOS_SNS_CTL2;
  volatile uint32_t SNS_LP_AOS_SNS_CTL3;
  volatile uint32_t SNS_LP_AOS_SNS_CTL4;
  volatile uint32_t SNS_SW_SEL_CSW_HI_MASK2;
  volatile uint32_t SNS_SW_SEL_CSW_HI_MASK1;
  volatile uint32_t SNS_SW_SEL_CSW_HI_MASK0;
  volatile uint32_t SNS_SW_SEL_CSW_LO_MASK2;
  volatile uint32_t SNS_SW_SEL_CSW_LO_MASK1;
  volatile uint32_t SNS_SW_SEL_CSW_LO_MASK0;
  volatile uint32_t SNS_SCAN_CTL;
  volatile uint32_t SNS_CDAC_CTL;
  volatile uint32_t SNS_CTL;
   volatile const uint32_t RESERVED[114];
   volatile const uint32_t RESULT_FIFO_RD;
   volatile const uint32_t RESERVED1[127];
   volatile const uint32_t STATUS1;
   volatile const uint32_t STATUS2;
   volatile const uint32_t STATUS3;
   volatile const uint32_t STATUS4;
   volatile const uint32_t RESULT_FIFO_STATUS;
   volatile const uint32_t RESULT_FIFO_STATUS2;
   volatile const uint32_t CE_STATUS;
   volatile const uint32_t BRIDGE_STATUS;
   volatile const uint32_t RESERVED2[248];
  volatile uint32_t FRAME_CMD;
  volatile uint32_t CE_CMD;
  volatile uint32_t FIFO_CMD;
   volatile const uint32_t RESERVED3[253];
  volatile uint32_t CE_INIT_CTL;
   volatile const uint32_t RESERVED4[255];
} MSCLP_SNS_Type;




typedef struct {
  volatile uint32_t CTL;
  volatile uint32_t SPARE;
  volatile uint32_t SCAN_CTL1;
  volatile uint32_t SCAN_CTL2;
  volatile uint32_t INIT_CTL1;
  volatile uint32_t INIT_CTL2;
  volatile uint32_t INIT_CTL3;
  volatile uint32_t INIT_CTL4;
  volatile uint32_t SENSE_DUTY_CTL;
  volatile uint32_t SENSE_PERIOD_CTL;
  volatile uint32_t FILTER_CTL;
   volatile const uint32_t RESERVED;
  volatile uint32_t CCOMP_CDAC_CTL;
  volatile uint32_t DITHER_CDAC_CTL;
  volatile uint32_t MSCCMP_CTL;
   volatile const uint32_t RESERVED1[5];
  volatile uint32_t OBS_CTL;
   volatile const uint32_t RESERVED2[7];
  volatile uint32_t AOS_CTL;
  volatile uint32_t CE_CTL;
   volatile const uint32_t RESERVED3[2];
  volatile uint32_t PUMP_CTL;
  volatile uint32_t IMO_CTL;
   volatile const uint32_t RESERVED4[30];
  volatile uint32_t INTR;
  volatile uint32_t INTR_SET;
  volatile uint32_t INTR_MASK;
   volatile const uint32_t INTR_MASKED;
   volatile const uint32_t RESERVED5[4];
  volatile uint32_t INTR_LP;
  volatile uint32_t INTR_LP_SET;
  volatile uint32_t INTR_LP_MASK;
   volatile const uint32_t INTR_LP_MASKED;
   volatile const uint32_t RESERVED6[4];
  volatile uint32_t WAKEUP_CMD;
  volatile uint32_t MRSS_CMD;
   volatile const uint32_t RESERVED7[14];
   volatile const uint32_t MRSS_STATUS;
   volatile const uint32_t AOS_STATUS;
   volatile const uint32_t RESERVED8[30];
  volatile uint32_t SW_SEL_GPIO;
  volatile uint32_t SW_SEL_CDAC_RE;
  volatile uint32_t SW_SEL_CDAC_CO;
  volatile uint32_t SW_SEL_CDAC_CF;
   volatile const uint32_t RESERVED9[4];
  volatile uint32_t SW_SEL_BGR;
   volatile const uint32_t RESERVED10[55];
  volatile uint32_t SW_SEL_CSW[64];
  volatile uint32_t SW_SEL_CSW_FUNC[8];
   volatile const uint32_t RESERVED11[56];
  volatile uint32_t CSW_CTL_LO;
  volatile uint32_t CSW_CTL_HI;
   volatile const uint32_t RESERVED12[62];
        MSCLP_MODE_Type MODE[4];
   volatile const uint32_t RESERVED13[1600];
        MSCLP_SNS_Type SNS;
   volatile const uint32_t RESERVED14[12224];
  volatile uint32_t TRIM_CTL;
  volatile uint32_t CLK_IMO_TRIM1;
  volatile uint32_t CLK_IMO_TRIM2;
  volatile uint32_t CLK_IMO_TRIM3;
  volatile uint32_t PWR_BG_TRIM1;
  volatile uint32_t PWR_BG_TRIM2;
  volatile uint32_t PWR_BG_TRIM3;
} MSCLP_Type;
# 79 "/pdl/devices/include/psoc4000t_config.h" 2
# 131 "/pdl/devices/include/cy8c4046fni_t412.h" 2
# 1 "/pdl/devices/include/gpio_psoc4000t_25_wlcsp.h" 1
# 27 "/pdl/devices/include/gpio_psoc4000t_25_wlcsp.h"
enum
{
    CY_GPIO_PACKAGE_QFN,
    CY_GPIO_PACKAGE_BGA,
    CY_GPIO_PACKAGE_CSP,
    CY_GPIO_PACKAGE_WLCSP,
    CY_GPIO_PACKAGE_LQFP,
    CY_GPIO_PACKAGE_TQFP,
    CY_GPIO_PACKAGE_SMT,
    CY_GPIO_PACKAGE_DFN,
    CY_GPIO_PACKAGE_SOIC,
    CY_GPIO_PACKAGE_SSOP,
    CY_GPIO_PACKAGE_LGA,
};





enum
{
    AMUXBUS_AMUXBUS_A,
    AMUXBUS_AMUXBUS_B,
};


typedef enum
{
    AMUX_SPLIT_CTL_NONE = 0x0000u
} cy_en_amux_split_t;
# 193 "/pdl/devices/include/gpio_psoc4000t_25_wlcsp.h"
typedef enum
{

    HSIOM_SEL_GPIO = 0,
    HSIOM_SEL_GPIO_DSI = 1,
    HSIOM_SEL_DSI_DSI = 2,
    HSIOM_SEL_DSI_GPIO = 3,
    HSIOM_SEL_CSD_SENSE = 4,
    HSIOM_SEL_CSD_SHIELD = 5,
    HSIOM_SEL_AMUXA = 6,
    HSIOM_SEL_AMUXB = 7,
    HSIOM_SEL_ACT_0 = 8,
    HSIOM_SEL_ACT_1 = 9,
    HSIOM_SEL_ACT_2 = 10,
    HSIOM_SEL_ACT_3 = 11,
    HSIOM_SEL_LCD_COM = 12,
    HSIOM_SEL_LCD_SEG = 13,
    HSIOM_SEL_DS_0 = 12,
    HSIOM_SEL_DS_1 = 13,
    HSIOM_SEL_DS_2 = 14,
    HSIOM_SEL_DS_3 = 15,


    P0_0_GPIO = 0,
    P0_0_MSCLP_SENSE = 4,
    P0_0_MSCLP_SHIELD = 5,
    P0_0_AMUXA = 6,
    P0_0_AMUXB = 7,
    P0_0_TCPWM_TR_IN0 = 11,
    P0_0_MSCLP_MSC_DDRV0 = 12,
    P0_0_MSCLP_EXT_SYNC = 13,
    P0_0_SCB0_SPI_SELECT1 = 15,


    P0_1_GPIO = 0,
    P0_1_MSCLP_SENSE = 4,
    P0_1_MSCLP_SHIELD = 5,
    P0_1_AMUXA = 6,
    P0_1_AMUXB = 7,
    P0_1_TCPWM_TR_IN1 = 11,
    P0_1_MSCLP_MSC_DDRV1 = 12,
    P0_1_MSCLP_EXT_SYNC_CLK = 13,
    P0_1_SCB0_SPI_SELECT2 = 15,


    P0_2_GPIO = 0,
    P0_2_MSCLP_SENSE = 4,
    P0_2_MSCLP_SHIELD = 5,
    P0_2_AMUXA = 6,
    P0_2_AMUXB = 7,
    P0_2_SCB0_UART_RX = 9,
    P0_2_MSCLP_MSC_DDRV2 = 12,
    P0_2_SCB0_I2C_SCL = 14,
    P0_2_SCB0_SPI_MOSI = 15,


    P0_3_GPIO = 0,
    P0_3_MSCLP_SENSE = 4,
    P0_3_MSCLP_SHIELD = 5,
    P0_3_AMUXA = 6,
    P0_3_AMUXB = 7,
    P0_3_SCB0_UART_TX = 9,
    P0_3_MSCLP_MSC_DDRV3 = 12,
    P0_3_SCB0_I2C_SDA = 14,
    P0_3_SCB0_SPI_MISO = 15,


    P0_4_GPIO = 0,
    P0_4_MSCLP_SENSE = 4,
    P0_4_MSCLP_SHIELD = 5,
    P0_4_AMUXA = 6,
    P0_4_AMUXB = 7,
    P0_4_SRSS_EXT_CLK = 8,
    P0_4_SCB0_UART_CTS = 9,
    P0_4_MSCLP_MSC_DDRV4 = 12,
    P0_4_MSCLP_EXT_FRM_START = 13,
    P0_4_SCB0_SPI_CLK = 15,


    P0_5_GPIO = 0,
    P0_5_MSCLP_SENSE = 4,
    P0_5_MSCLP_SHIELD = 5,
    P0_5_AMUXA = 6,
    P0_5_AMUXB = 7,
    P0_5_SCB0_UART_RTS = 9,
    P0_5_MSCLP_MSC_DDRV5 = 12,
    P0_5_SCB0_SPI_SELECT0 = 15,


    P1_0_GPIO = 0,
    P1_0_MSCLP_SENSE = 4,
    P1_0_MSCLP_SHIELD = 5,
    P1_0_AMUXA = 6,
    P1_0_AMUXB = 7,
    P1_0_TCPWM_LINE1 = 8,
    P1_0_TCPWM_TR_IN2 = 11,
    P1_0_MSCLP_MSC_DDRV6 = 12,
    P1_0_SCB0_SPI_SELECT3 = 15,


    P2_0_GPIO = 0,
    P2_0_MSCLP_SENSE = 4,
    P2_0_MSCLP_SHIELD = 5,
    P2_0_AMUXA = 6,
    P2_0_AMUXB = 7,
    P2_0_TCPWM_LINE_COMPL1 = 8,
    P2_0_TCPWM_TR_IN3 = 11,
    P2_0_MSCLP_MSC_DDRV7 = 12,
    P2_0_MSCLP_OBS_DATA3 = 13,


    P2_1_GPIO = 0,
    P2_1_MSCLP_SENSE = 4,
    P2_1_MSCLP_SHIELD = 5,
    P2_1_AMUXA = 6,
    P2_1_AMUXB = 7,
    P2_1_MSCLP_MSC_DDRV8 = 12,
    P2_1_MSCLP_OBS_DATA2 = 13,


    P2_2_GPIO = 0,
    P2_2_MSCLP_SENSE = 4,
    P2_2_MSCLP_SHIELD = 5,
    P2_2_AMUXA = 6,
    P2_2_AMUXB = 7,
    P2_2_TCPWM_LINE0 = 8,
    P2_2_SCB0_UART_RX = 9,
    P2_2_TCPWM_TR_IN4 = 11,
    P2_2_MSCLP_MSC_DDRV9 = 12,
    P2_2_MSCLP_OBS_DATA1 = 13,
    P2_2_SCB1_I2C_SCL = 14,
    P2_2_SCB0_SPI_MOSI = 15,


    P2_3_GPIO = 0,
    P2_3_MSCLP_SENSE = 4,
    P2_3_MSCLP_SHIELD = 5,
    P2_3_AMUXA = 6,
    P2_3_AMUXB = 7,
    P2_3_TCPWM_LINE_COMPL0 = 8,
    P2_3_SCB0_UART_TX = 9,
    P2_3_TCPWM_TR_IN5 = 11,
    P2_3_MSCLP_MSC_DDRV10 = 12,
    P2_3_MSCLP_OBS_DATA0 = 13,
    P2_3_SCB1_I2C_SDA = 14,
    P2_3_SCB0_SPI_MISO = 15,


    P2_4_GPIO = 0,
    P2_4_MSCLP_SENSE = 4,
    P2_4_MSCLP_SHIELD = 5,
    P2_4_AMUXA = 6,
    P2_4_AMUXB = 7,
    P2_4_TCPWM_LINE1 = 8,
    P2_4_SCB0_UART_CTS = 9,
    P2_4_MSCLP_MSC_DDRV11 = 12,
    P2_4_MSCLP_EXT_SYNC = 13,
    P2_4_SCB0_SPI_CLK = 15,


    P2_5_GPIO = 0,
    P2_5_MSCLP_SENSE = 4,
    P2_5_MSCLP_SHIELD = 5,
    P2_5_AMUXA = 6,
    P2_5_AMUXB = 7,
    P2_5_TCPWM_LINE_COMPL1 = 8,
    P2_5_SCB0_UART_RTS = 9,
    P2_5_MSCLP_MSC_DDRV12 = 12,
    P2_5_MSCLP_EXT_SYNC_CLK = 13,
    P2_5_SCB0_SPI_SELECT0 = 15,


    P3_0_GPIO = 0,
    P3_0_MSCLP_SENSE = 4,
    P3_0_MSCLP_SHIELD = 5,
    P3_0_AMUXA = 6,
    P3_0_AMUXB = 7,
    P3_0_TCPWM_LINE0 = 8,
    P3_0_SCB0_UART_RX = 9,
    P3_0_MSCLP_MSC_DDRV13 = 12,
    P3_0_MSCLP_EXT_FRM_START = 13,
    P3_0_SCB0_I2C_SCL = 14,
    P3_0_SCB0_SPI_MOSI = 15,


    P3_1_GPIO = 0,
    P3_1_MSCLP_SENSE = 4,
    P3_1_MSCLP_SHIELD = 5,
    P3_1_AMUXA = 6,
    P3_1_AMUXB = 7,
    P3_1_TCPWM_LINE_COMPL0 = 8,
    P3_1_SCB0_UART_TX = 9,
    P3_1_MSCLP_MSC_DDRV14 = 12,
    P3_1_SCB0_I2C_SDA = 14,
    P3_1_SCB0_SPI_MISO = 15,


    P3_2_GPIO = 0,
    P3_2_MSCLP_SENSE = 4,
    P3_2_MSCLP_SHIELD = 5,
    P3_2_AMUXA = 6,
    P3_2_AMUXB = 7,
    P3_2_TCPWM_LINE1 = 8,
    P3_2_SCB0_UART_CTS = 9,
    P3_2_MSCLP_MSC_DDRV15 = 12,
    P3_2_CPUSS_SWD_DATA = 13,
    P3_2_SCB1_I2C_SDA = 14,
    P3_2_SCB0_SPI_CLK = 15,


    P3_3_GPIO = 0,
    P3_3_MSCLP_SENSE = 4,
    P3_3_MSCLP_SHIELD = 5,
    P3_3_AMUXA = 6,
    P3_3_AMUXB = 7,
    P3_3_TCPWM_LINE_COMPL1 = 8,
    P3_3_SCB0_UART_RTS = 9,
    P3_3_MSCLP_MSC_DDRV16 = 12,
    P3_3_CPUSS_SWD_CLK = 13,
    P3_3_SCB1_I2C_SCL = 14,
    P3_3_SCB0_SPI_SELECT0 = 15,


    P4_0_GPIO = 0,
    P4_0_MSCLP_SENSE = 4,
    P4_0_MSCLP_SHIELD = 5,
    P4_0_AMUXA = 6,
    P4_0_AMUXB = 7,
    P4_0_SCB0_UART_RX = 9,
    P4_0_TCPWM_TR_IN6 = 11,
    P4_0_MSCLP_MSC_DDRV17 = 12,
    P4_0_SCB0_I2C_SCL = 14,
    P4_0_SCB0_SPI_MOSI = 15,


    P4_1_GPIO = 0,
    P4_1_MSCLP_SENSE = 4,
    P4_1_MSCLP_SHIELD = 5,
    P4_1_AMUXA = 6,
    P4_1_AMUXB = 7,
    P4_1_SCB0_UART_TX = 9,
    P4_1_MSCLP_MSC_DDRV18 = 12,
    P4_1_SCB0_I2C_SDA = 14,
    P4_1_SCB0_SPI_MISO = 15,


    P4_2_GPIO = 0,
    P4_2_MSCLP_SENSE = 4,
    P4_2_MSCLP_SHIELD = 5,
    P4_2_AMUXA = 6,
    P4_2_AMUXB = 7,
    P4_2_SCB0_UART_CTS = 9,
    P4_2_MSCLP_MSC_CMOD1_DDRV = 12,
    P4_2_SCB0_SPI_CLK = 15,


    P4_3_GPIO = 0,
    P4_3_MSCLP_SENSE = 4,
    P4_3_MSCLP_SHIELD = 5,
    P4_3_AMUXA = 6,
    P4_3_AMUXB = 7,
    P4_3_SCB0_UART_RTS = 9,
    P4_3_MSCLP_MSC_CMOD2_DDRV = 12,
    P4_3_SCB0_SPI_SELECT0 = 15
} en_hsiom_sel_t;
# 132 "/pdl/devices/include/cy8c4046fni_t412.h" 2
# 1420 "/pdl/devices/include/cy_device_headers.h" 2
# 33 "/pdl/drivers/include/cy_device.h" 2

# 1 "/tool/lib/gcc/arm-none-eabi/14.2.1/include/stddef.h" 1 3 4
# 35 "/pdl/drivers/include/cy_device.h" 2
# 506 "/pdl/drivers/include/cy_syspm.h" 2
# 1 "/pdl/drivers/include/cy_syslib.h" 1
# 196 "/pdl/drivers/include/cy_syslib.h"
# 1 "/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include/cy_utils.h" 1
# 58 "/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include/cy_utils.h"
       
# 71 "/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include/cy_utils.h"
typedef char cy_char8_t;
typedef float cy_float32_t;
typedef double cy_float64_t;
# 197 "/pdl/drivers/include/cy_syslib.h" 2
# 1 "/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include/cy_result.h" 1
# 93 "/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include/cy_result.h"
       
# 183 "/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include/cy_result.h"
typedef enum
{

    CY_RSLT_TYPE_INFO = 0U,

    CY_RSLT_TYPE_WARNING = 1U,

    CY_RSLT_TYPE_ERROR = 2U,

    CY_RSLT_TYPE_FATAL = 3U
} cy_en_rslt_type_t;
# 239 "/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include/cy_result.h"
typedef enum
{

    CY_RSLT_MODULE_DRIVER_SAR = 0x0001,

    CY_RSLT_MODULE_DRIVER_DFU = 0x0006,

    CY_RSLT_MODULE_DRIVER_CAPSENSE = 0x0007,

    CY_RSLT_MODULE_DRIVER_USB_DEV = 0x0008,


    CY_RSLT_MODULE_DRIVER_CTB = 0x000b,

    CY_RSLT_MODULE_DRIVER_CRYPTO = 0x000c,

    CY_RSLT_MODULE_DRIVER_SYSPM = 0x0010,

    CY_RSLT_MODULE_DRIVER_SYSLIB = 0x0011,

    CY_RSLT_MODULE_DRIVER_SYSCLK = 0x0012,

    CY_RSLT_MODULE_DRIVER_DMA = 0x0013,

    CY_RSLT_MODULE_DRIVER_FLASH = 0x0014,

    CY_RSLT_MODULE_DRIVER_SYSINT = 0x0015,

    CY_RSLT_MODULE_DRIVER_GPIO = 0x0016,


    CY_RSLT_MODULE_DRIVER_SYSANALOG = 0x0017,

    CY_RSLT_MODULE_DRIVER_CTDAC = 0x0019,

    CY_RSLT_MODULE_DRIVER_EFUSE = 0x001a,

    CY_RSLT_MODULE_DRIVER_EM_EEPROM = 0x001b,

    CY_RSLT_MODULE_DRIVER_PROFILE = 0x001e,

    CY_RSLT_MODULE_DRIVER_I2S = 0x0020,

    CY_RSLT_MODULE_DRIVER_IPC = 0x0022,


    CY_RSLT_MODULE_DRIVER_LPCOMP = 0x0023,

    CY_RSLT_MODULE_DRIVER_PDM_PCM = 0x0026,

    CY_RSLT_MODULE_DRIVER_RTC = 0x0028,


    CY_RSLT_MODULE_DRIVER_SCB = 0x002a,

    CY_RSLT_MODULE_DRIVER_SMIF = 0x002c,


    CY_RSLT_MODULE_DRIVER_TCPWM = 0x002d,

    CY_RSLT_MODULE_DRIVER_PROT = 0x0030,

    CY_RSLT_MODULE_DRIVER_HVSS = 0x0031,

    CY_RSLT_MODULE_DRIVER_CRWDT = 0x0032,

    CY_RSLT_MODULE_DRIVER_TRIGMUX = 0x0033,

    CY_RSLT_MODULE_DRIVER_WDT = 0x0034,

    CY_RSLT_MODULE_DRIVER_MCWDT = 0x0035,

    CY_RSLT_MODULE_DRIVER_LTC = 0x0036,

    CY_RSLT_MODULE_DRIVER_LIN = 0x0037,

    CY_RSLT_MODULE_DRIVER_LVD = 0x0039,

    CY_RSLT_MODULE_DRIVER_SD_HOST = 0x003a,

    CY_RSLT_MODULE_DRIVER_USBFS = 0x003b,

    CY_RSLT_MODULE_DRIVER_DMAC = 0x003f,

    CY_RSLT_MODULE_DRIVER_SEGLCD = 0x0040,

    CY_RSLT_MODULE_DRIVER_CSD = 0x0041,

    CY_RSLT_MODULE_DRIVER_SMARTIO = 0x0042,

    CY_RSLT_MODULE_DRIVER_CSDIDAC = 0x0044,

    CY_RSLT_MODULE_DRIVER_CANFD = 0x0045,

    CY_RSLT_MODULE_DRIVER_PRA = 0x0046,

    CY_RSLT_MODULE_DRIVER_MSC = 0x0047,



    CY_RSLT_MODULE_DRIVER_ADCMIC = 0x0048,

    CY_RSLT_MODULE_DRIVER_MSCLP = 0x0049,

    CY_RSLT_MODULE_DRIVER_EVTGEN = 0x004a,

    CY_RSLT_MODULE_DRIVER_SAR2 = 0x004b,

    CY_RSLT_MODULE_DRIVER_DSADC = 0x0050,

    CY_RSLT_MODULE_DRIVER_CAN2B = 0x0051,

    CY_RSLT_MODULE_DRIVER_ISOUART = 0x0052,

    CY_RSLT_MODULE_DRIVER_KEYSCAN = 0x0072,

    CY_RSLT_MODULE_DRIVER_PDM_PCM2 = 0x0073,

    CY_RSLT_MODULE_DRIVER_CRYPTOLITE = 0x0074,

    CY_RSLT_MODULE_DRIVER_SYSFAULT = 0x0076,

    CY_RSLT_MODULE_DRIVER_LVD_HT = 0x0078,

    CY_RSLT_MODULE_DRIVER_WHD = 0x0080,

    CY_RSLT_MODULE_DRIVER_BTHCI = 0x0081,



    CY_RSLT_MODULE_ABSTRACTION_HAL = 0x0100,

    CY_RSLT_MODULE_ABSTRACTION_BSP = 0x0180,

    CY_RSLT_MODULE_ABSTRACTION_FS = 0x0181,

    CY_RSLT_MODULE_ABSTRACTION_RESOURCE = 0x0182,

    CY_RSLT_MODULE_ABSTRACTION_OS = 0x0183,

    CY_RSLT_MODULE_ABSTRACTION_DATA_STREAMING= 0x0184,

    CY_RSLT_MODULE_ABSTRACTION_BLOCK_STORAGE= 0x0185,


    CY_RSLT_MODULE_BOARD_LIB_RETARGET_IO = 0x1A0,

    CY_RSLT_MODULE_BOARD_LIB_RGB_LED = 0x01A1,

    CY_RSLT_MODULE_BOARD_LIB_SERIAL_MEMORY = 0x01A2,


    CY_RSLT_MODULE_BOARD_LIB_SERIAL_FLASH = CY_RSLT_MODULE_BOARD_LIB_SERIAL_MEMORY,


    CY_RSLT_MODULE_BOARD_LIB_WHD_INTEGRATION = 0x01A3,


    CY_RSLT_MODULE_BOARD_SHIELD_028_EPD = 0x01B8,

    CY_RSLT_MODULE_BOARD_SHIELD_028_TFT = 0x01B9,

    CY_RSLT_MODULE_BOARD_SHIELD_032 = 0x01BA,

    CY_RSLT_MODULE_BOARD_SHIELD_028_SENSE = 0x01BB,


    CY_RSLT_MODULE_BOARD_HARDWARE_BMI160 = 0x01C0,


    CY_RSLT_MODULE_BOARD_HARDWARE_E2271CS021 = 0x01C1,

    CY_RSLT_MODULE_BOARD_HARDWARE_THERMISTOR = 0x01C2,


    CY_RSLT_MODULE_BOARD_HARDWARE_SSD1306 = 0x01C3,

    CY_RSLT_MODULE_BOARD_HARDWARE_ST7789V = 0x01C4,

    CY_RSLT_MODULE_BOARD_HARDWARE_LIGHT_SENSOR = 0x01C5,

    CY_RSLT_MODULE_BOARD_HARDWARE_AK4954A = 0x01C6,


    CY_RSLT_MODULE_BOARD_HARDWARE_BMX160 = 0x01C7,


    CY_RSLT_MODULE_BOARD_HARDWARE_DPS3XX = 0x01C8,

    CY_RSLT_MODULE_BOARD_HARDWARE_WM8960 = 0x01C9,


    CY_RSLT_MODULE_BOARD_HARDWARE_XENSIV_PASCO2 = 0x01CA,


    CY_RSLT_MODULE_BOARD_HARDWARE_XENSIV_BGT60TRXX = 0x01CC,

    CY_RSLT_MODULE_BOARD_HARDWARE_LM49450 = 0x01CE,


    CY_RSLT_MODULE_BOARD_HARDWARE_TLV320DAC3100 = 0x01CF,


    CY_RSLT_MODULE_MIDDLEWARE_MNDS = 0x200,

    CY_RSLT_MODULE_MIDDLEWARE_AWS = 0x201,

    CY_RSLT_MODULE_MIDDLEWARE_JSON = 0x202,

    CY_RSLT_MODULE_MIDDLEWARE_LINKED_LIST = 0x203,

    CY_RSLT_MODULE_MIDDLEWARE_COMMAND_CONSOLE = 0x204,

    CY_RSLT_MODULE_MIDDLEWARE_HTTP_SERVER = 0x205,

    CY_RSLT_MODULE_MIDDLEWARE_ENTERPRISE_SECURITY = 0x206,

    CY_RSLT_MODULE_MIDDLEWARE_TCPIP = 0x207,


    CY_RSLT_MODULE_MIDDLEWARE_MW = 0x208,

    CY_RSLT_MODULE_MIDDLEWARE_TLS = 0x209,

    CY_RSLT_MODULE_MIDDLEWARE_SECURE_SOCKETS = 0x20a,


    CY_RSLT_MODULE_MIDDLEWARE_WCM = 0x20b,

    CY_RSLT_MODULE_MIDDLEWARE_LWIP_WHD_PORT = 0x20c,

    CY_RSLT_MODULE_MIDDLEWARE_OTA_UPDATE = 0x20d,

    CY_RSLT_MODULE_MIDDLEWARE_HTTP_CLIENT = 0x20e,

    CY_RSLT_MODULE_MIDDLEWARE_ML = 0x20f,

    CY_RSLT_MODULE_MIDDLEWARE_EM_EEPROM = 0x24f,

    CY_RSLT_MODULE_MIDDLEWARE_KVSTORE = 0x250,

    CY_RSLT_MODULE_MIDDLEWARE_LIN = 0x0251,

    CY_RSLT_MODULE_MIDDLEWARE_UBM = 0x0252,

    CY_RSLT_MODULE_MIDDLEWARE_KVSTORE_CAT5 = 0x0253,

    CY_RSLT_MODULE_MIDDLEWARE_MCDI = 0x0254,

    CY_RSLT_MODULE_MIDDLEWARE_PWRCONV = 0x0255,

    CY_RSLT_MODULE_MIDDLEWARE_ASYNC_TRANSFER = 0x0256,

    CY_RSLT_MODULE_MIDDLEWARE_IPC = 0x0257,

    CY_RSLT_MODULE_MIDDLEWARE_AFX = 0x0258,

    CY_RSLT_MODULE_MIDDLEWARE_SRF = 0x0259,

    CY_RSLT_MODULE_MIDDLEWARE_PMBUS = 0x025a
} cy_en_rslt_module_t;
# 512 "/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include/cy_result.h"
typedef uint32_t cy_rslt_t;
# 526 "/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include/cy_result.h"
typedef union
{
    cy_rslt_t raw;

    struct
    {
        uint16_t code : (16U);
        cy_en_rslt_type_t type : (2U);

        cy_en_rslt_module_t module : (14U);



    };
} cy_rslt_decode_t;
# 198 "/pdl/drivers/include/cy_syslib.h" 2
# 281 "/pdl/drivers/include/cy_syslib.h"
typedef enum
{
    CY_SYSLIB_SUCCESS = 0x00UL,
    CY_SYSLIB_BAD_PARAM = ((uint32_t)((uint32_t)((0x11U) & (((1UL << ((14U))) - 1U))) << ((18U)))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0x01UL,
    CY_SYSLIB_TIMEOUT = ((uint32_t)((uint32_t)((0x11U) & (((1UL << ((14U))) - 1U))) << ((18U)))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0x02UL,
    CY_SYSLIB_INVALID_STATE = ((uint32_t)((uint32_t)((0x11U) & (((1UL << ((14U))) - 1U))) << ((18U)))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0x03UL,
    CY_SYSLIB_UNKNOWN = ((uint32_t)((uint32_t)((0x11U) & (((1UL << ((14U))) - 1U))) << ((18U)))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0xFFUL
} cy_en_syslib_status_t;
# 316 "/pdl/drivers/include/cy_syslib.h"
    typedef struct
    {
        uint32_t r0;
        uint32_t r1;
        uint32_t r2;
        uint32_t r3;
        uint32_t r12;
        uint32_t lr;
        uint32_t pc;
        uint32_t psr;
    } cy_stc_fault_frame_t;
# 349 "/pdl/drivers/include/cy_syslib.h"
typedef char char_t;
typedef float float32_t;
typedef double float64_t;
# 364 "/pdl/drivers/include/cy_syslib.h"
    extern __attribute__ ((section(".noinit"))) cy_stc_fault_frame_t cy_faultFrame;
# 477 "/pdl/drivers/include/cy_syslib.h"




              ;
# 493 "/pdl/drivers/include/cy_syslib.h"
void Cy_SysLib_Delay(uint32_t milliseconds);
void Cy_SysLib_DelayUs(uint16_t microseconds);




void Cy_SysLib_DelayCycles(uint32_t cycles);
void Cy_SysLib_ClearFlashCacheAndBuffer(void);
uint32_t Cy_SysLib_GetResetReason(void);
void Cy_SysLib_ClearResetReason(void);

    void Cy_SysLib_FaultHandler(uint32_t const *faultStackAddr);
    void Cy_SysLib_ProcessingFault(void);

void Cy_SysLib_SetWaitStates(uint32_t clkHfMHz);
# 529 "/pdl/drivers/include/cy_syslib.h"
uint32_t Cy_SysLib_EnterCriticalSection(void);
# 544 "/pdl/drivers/include/cy_syslib.h"
void Cy_SysLib_ExitCriticalSection(uint32_t savedIntrStatus);
# 563 "/pdl/drivers/include/cy_syslib.h"
uint64_t Cy_SysLib_GetUniqueId(void);




;
# 507 "/pdl/drivers/include/cy_syspm.h" 2
# 567 "/pdl/drivers/include/cy_syspm.h"
typedef enum
{
    CY_SYSPM_SUCCESS = 0x0U,
    CY_SYSPM_BAD_PARAM = (((uint32_t)((uint32_t)((0x10U) & (((1UL << ((14U))) - 1U))) << ((18U))))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0x01U,
    CY_SYSPM_TIMEOUT = (((uint32_t)((uint32_t)((0x10U) & (((1UL << ((14U))) - 1U))) << ((18U))))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0x02U,
    CY_SYSPM_INVALID_STATE = (((uint32_t)((uint32_t)((0x10U) & (((1UL << ((14U))) - 1U))) << ((18U))))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0x03U,

    CY_SYSPM_FAIL = (((uint32_t)((uint32_t)((0x10U) & (((1UL << ((14U))) - 1U))) << ((18U))))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0xFFU
} cy_en_syspm_status_t;
# 584 "/pdl/drivers/include/cy_syspm.h"
typedef enum
{
    CY_SYSPM_SLEEP = 0U,
    CY_SYSPM_DEEPSLEEP = 1U,
    CY_SYSPM_HIBERNATE = 2U,

} cy_en_syspm_callback_type_t;
# 618 "/pdl/drivers/include/cy_syspm.h"
typedef enum
{
    CY_SYSPM_CHECK_READY = 0x01U,


    CY_SYSPM_CHECK_FAIL = 0x02U,




    CY_SYSPM_BEFORE_TRANSITION = 0x04U,



    CY_SYSPM_AFTER_TRANSITION = 0x08U

} cy_en_syspm_callback_mode_t;
# 663 "/pdl/drivers/include/cy_syspm.h"
typedef struct
{
    void *base;


    void *context;


} cy_stc_syspm_callback_params_t;


typedef cy_en_syspm_status_t (*Cy_SysPmCallback) (cy_stc_syspm_callback_params_t *callbackParams, cy_en_syspm_callback_mode_t mode);


typedef struct cy_stc_syspm_callback
{
    Cy_SysPmCallback callback;
    cy_en_syspm_callback_type_t type;
    uint32_t skipMode;







    cy_stc_syspm_callback_params_t *callbackParams;


    struct cy_stc_syspm_callback *prevItm;





    struct cy_stc_syspm_callback *nextItm;




    uint8_t order;





} cy_stc_syspm_callback_t;
# 723 "/pdl/drivers/include/cy_syspm.h"
cy_en_syspm_status_t Cy_SysPm_CpuEnterSleep(void);
cy_en_syspm_status_t Cy_SysPm_CpuEnterDeepSleep(void);
void Cy_SysPm_CpuEnterSleepNoCallbacks(void);
void Cy_SysPm_CpuEnterDeepSleepNoCallbacks(void);
void Cy_SysPm_SleepOnExit(
# 727 "/pdl/drivers/include/cy_syspm.h" 3 4
                                         _Bool 
# 727 "/pdl/drivers/include/cy_syspm.h"
                                              enable);
# 752 "/pdl/drivers/include/cy_syspm.h"

# 752 "/pdl/drivers/include/cy_syspm.h" 3 4
_Bool 
# 752 "/pdl/drivers/include/cy_syspm.h"
    Cy_SysPm_RegisterCallback(cy_stc_syspm_callback_t *handler);

# 753 "/pdl/drivers/include/cy_syspm.h" 3 4
_Bool 
# 753 "/pdl/drivers/include/cy_syspm.h"
    Cy_SysPm_UnregisterCallback(cy_stc_syspm_callback_t const *handler);
cy_en_syspm_status_t Cy_SysPm_ExecuteCallback(cy_en_syspm_callback_type_t type, cy_en_syspm_callback_mode_t mode);
cy_stc_syspm_callback_t* Cy_SysPm_GetFailedCallback(cy_en_syspm_callback_type_t type);
# 27 "/pdl/drivers/source/cy_syspm.c" 2
# 1 "/pdl/drivers/include/cy_sysclk.h" 1
# 603 "/pdl/drivers/include/cy_sysclk.h"
# 1 "/pdl/drivers/include/cy_syspm.h" 1
# 604 "/pdl/drivers/include/cy_sysclk.h" 2
# 1 "/pdl/drivers/include/cy_wdt.h" 1
# 494 "/pdl/drivers/include/cy_wdt.h"
void Cy_WDT_Init(void);
static inline void Cy_WDT_Enable(void);
static inline 
# 496 "/pdl/drivers/include/cy_wdt.h" 3 4
               _Bool 
# 496 "/pdl/drivers/include/cy_wdt.h"
                    Cy_WDT_IsEnabled(void);
static inline void Cy_WDT_Disable(void);
static inline uint32_t Cy_WDT_GetCount(void);


    void Cy_WDT_SetMatch(uint32_t match);
    static inline uint32_t Cy_WDT_GetMatch(void);
    void Cy_WDT_SetIgnoreBits(uint32_t bitsNum);
    static inline uint32_t Cy_WDT_GetIgnoreBits(void);


static inline void Cy_WDT_MaskInterrupt(void);
static inline void Cy_WDT_UnmaskInterrupt(void);
static inline 
# 509 "/pdl/drivers/include/cy_wdt.h" 3 4
               _Bool 
# 509 "/pdl/drivers/include/cy_wdt.h"
                    Cy_WDT_GetInterruptStatusMasked(void);
void Cy_WDT_ClearInterrupt(void);
static inline void Cy_WDT_ClearWatchdog(void);
# 549 "/pdl/drivers/include/cy_wdt.h"
static inline void Cy_WDT_Enable(void)
{

    (((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->WDT_DISABLE_KEY) = (0UL);




}
# 575 "/pdl/drivers/include/cy_wdt.h"
static inline 
# 575 "/pdl/drivers/include/cy_wdt.h" 3 4
               _Bool 
# 575 "/pdl/drivers/include/cy_wdt.h"
                    Cy_WDT_IsEnabled(void)
{

    return((0xACED8865UL) != (((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->WDT_DISABLE_KEY));



}
# 603 "/pdl/drivers/include/cy_wdt.h"
static inline void Cy_WDT_Disable(void)
{

    (((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->WDT_DISABLE_KEY) = (0xACED8865UL);
# 617 "/pdl/drivers/include/cy_wdt.h"
}
# 631 "/pdl/drivers/include/cy_wdt.h"
static inline uint32_t Cy_WDT_GetMatch(void)
{
    return ((((uint32_t)((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->WDT_MATCH)) & 0xFFFFUL) >> 0UL));
}
# 646 "/pdl/drivers/include/cy_wdt.h"
static inline uint32_t Cy_WDT_GetCount(void)
{

    return ((((uint32_t)((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->WDT_COUNTER)) & 0xFFFFUL) >> 0UL));



}
# 668 "/pdl/drivers/include/cy_wdt.h"
static inline uint32_t Cy_WDT_GetIgnoreBits(void)
{
    return ((((uint32_t)((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->WDT_MATCH)) & 0xF0000UL) >> 16UL));
}
# 682 "/pdl/drivers/include/cy_wdt.h"
static inline void Cy_WDT_MaskInterrupt(void)
{

    (((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->SRSS_INTR_MASK) &= ~0x1UL;



}
# 699 "/pdl/drivers/include/cy_wdt.h"
static inline void Cy_WDT_UnmaskInterrupt(void)
{

    (((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->SRSS_INTR_MASK) |= 0x1UL;



}
# 725 "/pdl/drivers/include/cy_wdt.h"
static inline 
# 725 "/pdl/drivers/include/cy_wdt.h" 3 4
               _Bool 
# 725 "/pdl/drivers/include/cy_wdt.h"
                    Cy_WDT_GetInterruptStatusMasked(void)
{

    return (((((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->SRSS_INTR_MASK)) & (0x1UL)) != 0UL) &&
            ((((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->SRSS_INTR)) & (0x1UL)) != 0UL));



}
# 744 "/pdl/drivers/include/cy_wdt.h"
static inline void Cy_WDT_ClearWatchdog(void)
{
    Cy_WDT_ClearInterrupt();
}
# 605 "/pdl/drivers/include/cy_sysclk.h" 2
# 643 "/pdl/drivers/include/cy_sysclk.h"
typedef enum
{
    CY_SYSCLK_SUCCESS = 0x00UL,
    CY_SYSCLK_BAD_PARAM = (((uint32_t)((uint32_t)((0x12U) & (((1UL << ((14U))) - 1U))) << ((18U)))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0x01UL),
    CY_SYSCLK_TIMEOUT = (((uint32_t)((uint32_t)((0x12U) & (((1UL << ((14U))) - 1U))) << ((18U)))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0x02UL),
    CY_SYSCLK_INVALID_STATE = (((uint32_t)((uint32_t)((0x12U) & (((1UL << ((14U))) - 1U))) << ((18U)))) | ((uint32_t)CY_RSLT_TYPE_ERROR << ((16U))) | 0x03UL),
    CY_SYSCLK_STARTED = (((uint32_t)((uint32_t)((0x12U) & (((1UL << ((14U))) - 1U))) << ((18U)))) | ((uint32_t)CY_RSLT_TYPE_WARNING << ((16U))) | 0x04UL)
} cy_en_sysclk_status_t;
# 662 "/pdl/drivers/include/cy_sysclk.h"
    void Cy_SysClk_ExtClkSetFrequency(uint32_t freq);
uint32_t Cy_SysClk_ExtClkGetFrequency(void);
# 786 "/pdl/drivers/include/cy_sysclk.h"
typedef enum
{
    CY_SYSCLK_IMO_24MHZ = 24000000UL,
    CY_SYSCLK_IMO_28MHZ = 28000000UL,
    CY_SYSCLK_IMO_32MHZ = 32000000UL,
    CY_SYSCLK_IMO_36MHZ = 36000000UL,
    CY_SYSCLK_IMO_40MHZ = 40000000UL,
    CY_SYSCLK_IMO_44MHZ = 44000000UL,
    CY_SYSCLK_IMO_48MHZ = 48000000UL,
    CY_SYSCLK_IMO_49_152MHZ= 49152000UL
} cy_en_sysclk_imo_freq_t;
# 813 "/pdl/drivers/include/cy_sysclk.h"
cy_en_sysclk_status_t Cy_SysClk_ImoSetFrequency(cy_en_sysclk_imo_freq_t freq);
uint32_t Cy_SysClk_ImoGetFrequency(void);







static inline void Cy_SysClk_ImoEnable(void);
static inline void Cy_SysClk_ImoDisable(void);
static inline 
# 824 "/pdl/drivers/include/cy_sysclk.h" 3 4
               _Bool 
# 824 "/pdl/drivers/include/cy_sysclk.h"
                    Cy_SysClk_ImoIsEnabled(void);
# 836 "/pdl/drivers/include/cy_sysclk.h"
static inline void Cy_SysClk_ImoEnable(void)
{





    (((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_IMO_CONFIG) = 0x80000000UL;




}
# 857 "/pdl/drivers/include/cy_sysclk.h"
static inline 
# 857 "/pdl/drivers/include/cy_sysclk.h" 3 4
               _Bool 
# 857 "/pdl/drivers/include/cy_sysclk.h"
                    Cy_SysClk_ImoIsEnabled(void)
{
    return(((((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_IMO_CONFIG)) & (0x80000000UL)) != 0UL));
}
# 869 "/pdl/drivers/include/cy_sysclk.h"
static inline void Cy_SysClk_ImoDisable(void)
{
# 879 "/pdl/drivers/include/cy_sysclk.h"
    (((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_IMO_CONFIG) = 0UL;







}
# 1739 "/pdl/drivers/include/cy_sysclk.h"
static inline void Cy_SysClk_IloEnable(void);
static inline 
# 1740 "/pdl/drivers/include/cy_sysclk.h" 3 4
               _Bool 
# 1740 "/pdl/drivers/include/cy_sysclk.h"
                    Cy_SysClk_IloIsEnabled(void);
static inline cy_en_sysclk_status_t Cy_SysClk_IloDisable(void);
                 void Cy_SysClk_IloStartMeasurement(void);
                 void Cy_SysClk_IloStopMeasurement(void);
cy_en_sysclk_status_t Cy_SysClk_IloCompensate(uint32_t desiredDelay , uint32_t * compensatedCycles);
# 1770 "/pdl/drivers/include/cy_sysclk.h"
static inline void Cy_SysClk_IloEnable(void)
{






    (((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_ILO_CONFIG) |= 0x80000000UL;




}
# 1796 "/pdl/drivers/include/cy_sysclk.h"
static inline 
# 1796 "/pdl/drivers/include/cy_sysclk.h" 3 4
               _Bool 
# 1796 "/pdl/drivers/include/cy_sysclk.h"
                    Cy_SysClk_IloIsEnabled(void)
{
    return(((((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_ILO_CONFIG)) & (0x80000000UL)) != 0UL));
}
# 1826 "/pdl/drivers/include/cy_sysclk.h"
static inline cy_en_sysclk_status_t Cy_SysClk_IloDisable(void)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_INVALID_STATE;
# 1849 "/pdl/drivers/include/cy_sysclk.h"
    if (!Cy_WDT_IsEnabled())
    {
        (((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_ILO_CONFIG) &= ~0x80000000UL;
        retVal = CY_SYSCLK_SUCCESS;
    }


    return (retVal);
}
# 1987 "/pdl/drivers/include/cy_sysclk.h"
typedef enum
{
    CY_SYSCLK_CLKHF_IN_IMO = 0U,
    CY_SYSCLK_CLKHF_IN_EXTCLK = 1U,
# 2014 "/pdl/drivers/include/cy_sysclk.h"
} cy_en_sysclk_clkhf_src_t;






typedef enum
{
    CY_SYSCLK_NO_DIV = 0U,
    CY_SYSCLK_DIV_2 = 1U,
    CY_SYSCLK_DIV_4 = 2U,
    CY_SYSCLK_DIV_8 = 3U
} cy_en_sysclk_dividers_t;
# 2041 "/pdl/drivers/include/cy_sysclk.h"
                  cy_en_sysclk_status_t Cy_SysClk_ClkHfSetSource(cy_en_sysclk_clkhf_src_t source);
               cy_en_sysclk_clkhf_src_t Cy_SysClk_ClkHfGetSource(void);
static inline void Cy_SysClk_ClkHfSetDivider(cy_en_sysclk_dividers_t divider);
static inline cy_en_sysclk_dividers_t Cy_SysClk_ClkHfGetDivider(void);
                               uint32_t Cy_SysClk_ClkHfGetFrequency(void);
# 2070 "/pdl/drivers/include/cy_sysclk.h"
static inline void Cy_SysClk_ClkHfSetDivider(cy_en_sysclk_dividers_t divider)
{
    if ((((divider) == CY_SYSCLK_NO_DIV) || ((divider) == CY_SYSCLK_DIV_2) || ((divider) == CY_SYSCLK_DIV_4) || ((divider) == CY_SYSCLK_DIV_8)))
    {





        (((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_SELECT)) = (((((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_SELECT))) & ((uint32_t)(~(0xCUL)))) | ((((uint32_t)((divider)) << 2UL) & 0xCUL))));




    }
}
# 2104 "/pdl/drivers/include/cy_sysclk.h"
static inline cy_en_sysclk_dividers_t Cy_SysClk_ClkHfGetDivider(void)
{
    do{}while(
# 2106 "/pdl/drivers/include/cy_sysclk.h" 3 4
   0
# 2106 "/pdl/drivers/include/cy_sysclk.h"
   );
    return ((cy_en_sysclk_dividers_t)((((uint32_t)((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_SELECT)) & 0xCUL) >> 2UL)));
}
# 2617 "/pdl/drivers/include/cy_sysclk.h"
static inline void Cy_SysClk_ClkSysSetDivider(cy_en_sysclk_dividers_t divider);
static inline cy_en_sysclk_dividers_t Cy_SysClk_ClkSysGetDivider(void);
static inline uint32_t Cy_SysClk_ClkSysGetFrequency(void);
# 2634 "/pdl/drivers/include/cy_sysclk.h"
static inline uint32_t Cy_SysClk_ClkSysGetFrequency(void)
{

    uint32_t locDiv = 1UL << (uint32_t)Cy_SysClk_ClkSysGetDivider();

    return ((((Cy_SysClk_ClkHfGetFrequency()) + ((locDiv) / 2U)) / (locDiv)));
}
# 2667 "/pdl/drivers/include/cy_sysclk.h"
static inline void Cy_SysClk_ClkSysSetDivider(cy_en_sysclk_dividers_t divider)
{
    if ((((divider) == CY_SYSCLK_NO_DIV) || ((divider) == CY_SYSCLK_DIV_2) || ((divider) == CY_SYSCLK_DIV_4) || ((divider) == CY_SYSCLK_DIV_8)))
    {





        (((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_SELECT)) = (((((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_SELECT))) & ((uint32_t)(~(0xC0UL)))) | ((((uint32_t)((divider)) << 6UL) & 0xC0UL))));




    }
}
# 2701 "/pdl/drivers/include/cy_sysclk.h"
static inline cy_en_sysclk_dividers_t Cy_SysClk_ClkSysGetDivider(void)
{
    do{}while(
# 2703 "/pdl/drivers/include/cy_sysclk.h" 3 4
   0
# 2703 "/pdl/drivers/include/cy_sysclk.h"
   );
    return ((cy_en_sysclk_dividers_t)(((uint32_t)((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_SELECT)) & 0xC0UL) >> 6UL));
}
# 2717 "/pdl/drivers/include/cy_sysclk.h"
typedef enum
{
    CY_SYSCLK_DIV_8_BIT = 0U,
    CY_SYSCLK_DIV_16_BIT = 1U,
    CY_SYSCLK_DIV_16_5_BIT = 2U,
    CY_SYSCLK_DIV_24_5_BIT = 3U
} cy_en_sysclk_divider_types_t;
# 2746 "/pdl/drivers/include/cy_sysclk.h"
cy_en_sysclk_status_t Cy_SysClk_PeriphSetDivider(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum, uint32_t dividerValue);
             uint32_t Cy_SysClk_PeriphGetDivider(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum);
cy_en_sysclk_status_t Cy_SysClk_PeriphSetFracDivider(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum, uint32_t dividerIntValue, uint32_t dividerFracValue);
                 void Cy_SysClk_PeriphGetFracDivider(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum, uint32_t *dividerIntValue, uint32_t *dividerFracValue);
cy_en_sysclk_status_t Cy_SysClk_PeriphAssignDivider(en_clk_dst_t periphNum, cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum);
cy_en_sysclk_status_t Cy_SysClk_PeriphEnableDivider(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum);
cy_en_sysclk_status_t Cy_SysClk_PeriphDisableDivider(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum);
cy_en_sysclk_status_t Cy_SysClk_PeriphEnablePhaseAlignDivider(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum, cy_en_sysclk_divider_types_t dividerTypePA, uint32_t dividerNumPA);
                 
# 2754 "/pdl/drivers/include/cy_sysclk.h" 3 4
                _Bool 
# 2754 "/pdl/drivers/include/cy_sysclk.h"
                     Cy_SysClk_PeriphDividerIsEnabled(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum);
             uint32_t Cy_SysClk_PeriphGetFrequency(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum);
             uint32_t Cy_SysClk_PeriphSetFrequency(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum, uint32_t frequency);
static inline uint32_t Cy_SysClk_PeriphGetAssignedDivider(en_clk_dst_t periphNum);
# 2774 "/pdl/drivers/include/cy_sysclk.h"
static inline uint32_t Cy_SysClk_PeriphGetAssignedDivider(en_clk_dst_t periphNum)
{
    do { if(!(4u > (uint32_t)periphNum)) { do { __asm("    bkpt    1"); } while(
# 2776 "/pdl/drivers/include/cy_sysclk.h" 3 4
   0
# 2776 "/pdl/drivers/include/cy_sysclk.h"
   ); } } while (
# 2776 "/pdl/drivers/include/cy_sysclk.h" 3 4
   0
# 2776 "/pdl/drivers/include/cy_sysclk.h"
   );
    return ((((PERI_Type *) ((PERI_Type*) 0x40010000UL))->PCLK_CTL)[periphNum] & (0x3FUL | 0xC0UL));
}
# 2794 "/pdl/drivers/include/cy_sysclk.h"
typedef enum
{
    CY_SYSCLK_PUMP_IN_GND = 0UL,
    CY_SYSCLK_PUMP_IN_IMO = 1UL,
    CY_SYSCLK_PUMP_IN_HFCLK = 2UL
} cy_en_sysclk_clkpump_src_t;
# 2812 "/pdl/drivers/include/cy_sysclk.h"
                     cy_en_sysclk_status_t Cy_SysClk_ClkPumpSetSource(cy_en_sysclk_clkpump_src_t source);
static inline cy_en_sysclk_clkpump_src_t Cy_SysClk_ClkPumpGetSource(void);
static inline uint32_t Cy_SysClk_ClkPumpGetFrequency(void);
# 2832 "/pdl/drivers/include/cy_sysclk.h"
static inline cy_en_sysclk_clkpump_src_t Cy_SysClk_ClkPumpGetSource(void)
{
    do{}while(
# 2834 "/pdl/drivers/include/cy_sysclk.h" 3 4
   0
# 2834 "/pdl/drivers/include/cy_sysclk.h"
   );
    return ((cy_en_sysclk_clkpump_src_t)(((uint32_t)((((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->CLK_SELECT)) & 0x30UL) >> 4UL));
}
# 2851 "/pdl/drivers/include/cy_sysclk.h"
static inline uint32_t Cy_SysClk_ClkPumpGetFrequency(void)
{
    uint32_t freq = 0UL;

    switch (Cy_SysClk_ClkPumpGetSource())
    {
        case CY_SYSCLK_PUMP_IN_IMO:
            freq = Cy_SysClk_ImoGetFrequency();
            break;

        case CY_SYSCLK_PUMP_IN_HFCLK:
            freq = Cy_SysClk_ClkHfGetFrequency();
            break;

        default:
            break;
    }

    return (freq);
}
# 2891 "/pdl/drivers/include/cy_sysclk.h"
typedef void (*cy_cb_sysclk_t) (uint32_t event);





typedef struct
{

    cy_cb_sysclk_t callback;



} cy_stc_sysclk_context_t;







static inline void Cy_SysClk_RegisterCallback(cy_cb_sysclk_t callback, cy_stc_sysclk_context_t * context);
cy_en_syspm_status_t Cy_SysClk_DeepSleepCallback(cy_stc_syspm_callback_params_t * callbackParams, cy_en_syspm_callback_mode_t mode);
# 2937 "/pdl/drivers/include/cy_sysclk.h"
static inline void Cy_SysClk_RegisterCallback(cy_cb_sysclk_t callback, cy_stc_sysclk_context_t * context)
{
    if (
# 2939 "/pdl/drivers/include/cy_sysclk.h" 3 4
       ((void *)0) 
# 2939 "/pdl/drivers/include/cy_sysclk.h"
            != context)
    {
        context->callback = callback;
    }
}
# 28 "/pdl/drivers/source/cy_syspm.c" 2
# 43 "/pdl/drivers/source/cy_syspm.c"
static cy_stc_syspm_callback_t* pmCallbackRoot[(3U)] = {
# 43 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                                   ((void *)0)
# 43 "/pdl/drivers/source/cy_syspm.c"
                                                                       , 
# 43 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                                         ((void *)0)
# 43 "/pdl/drivers/source/cy_syspm.c"
                                                                             , 
# 43 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                                               ((void *)0)
# 43 "/pdl/drivers/source/cy_syspm.c"
                                                                                   };


static cy_stc_syspm_callback_t* failedCallback[(3U)] = {
# 46 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                                   ((void *)0)
# 46 "/pdl/drivers/source/cy_syspm.c"
                                                                       , 
# 46 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                                         ((void *)0)
# 46 "/pdl/drivers/source/cy_syspm.c"
                                                                             , 
# 46 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                                               ((void *)0)
# 46 "/pdl/drivers/source/cy_syspm.c"
                                                                                   };
# 102 "/pdl/drivers/source/cy_syspm.c"
cy_en_syspm_status_t Cy_SysPm_CpuEnterSleep(void)
{
    uint32_t interruptState;
    uint32_t cbSleepRootIdx = (uint32_t) CY_SYSPM_SLEEP;
    cy_en_syspm_status_t retVal = CY_SYSPM_SUCCESS;


    if (pmCallbackRoot[cbSleepRootIdx] != 
# 109 "/pdl/drivers/source/cy_syspm.c" 3 4
                                         ((void *)0)
# 109 "/pdl/drivers/source/cy_syspm.c"
                                             )
    {
        retVal = Cy_SysPm_ExecuteCallback(CY_SYSPM_SLEEP, CY_SYSPM_CHECK_READY);
    }





    if(retVal == CY_SYSPM_SUCCESS)
    {



        interruptState = Cy_SysLib_EnterCriticalSection();
        if (pmCallbackRoot[cbSleepRootIdx] != 
# 124 "/pdl/drivers/source/cy_syspm.c" 3 4
                                             ((void *)0)
# 124 "/pdl/drivers/source/cy_syspm.c"
                                                 )
        {
            (void) Cy_SysPm_ExecuteCallback(CY_SYSPM_SLEEP, CY_SYSPM_BEFORE_TRANSITION);
        }

        Cy_SysPm_CpuEnterSleepNoCallbacks();

        Cy_SysLib_ExitCriticalSection(interruptState);




        if (pmCallbackRoot[cbSleepRootIdx] != 
# 136 "/pdl/drivers/source/cy_syspm.c" 3 4
                                             ((void *)0)
# 136 "/pdl/drivers/source/cy_syspm.c"
                                                 )
        {
            (void) Cy_SysPm_ExecuteCallback(CY_SYSPM_SLEEP, CY_SYSPM_AFTER_TRANSITION);
        }
    }
    else
    {




        (void) Cy_SysPm_ExecuteCallback(CY_SYSPM_SLEEP, CY_SYSPM_CHECK_FAIL);
        retVal = CY_SYSPM_FAIL;
    }
    return retVal;
}
# 169 "/pdl/drivers/source/cy_syspm.c"
void Cy_SysPm_CpuEnterSleepNoCallbacks(void)
{

    (((SCB_Type *)((SCB_Type *) ((0xE000E000UL) + 0x0D00UL) ))->SCR) &= (uint32_t) ~(1UL << 2U);
    __asm volatile ("wfi":::"memory");
}
# 239 "/pdl/drivers/source/cy_syspm.c"
cy_en_syspm_status_t Cy_SysPm_CpuEnterDeepSleep(void)
{
    uint32_t interruptState;
    uint32_t cbDeepSleepRootIdx = (uint32_t) CY_SYSPM_DEEPSLEEP;
    cy_en_syspm_status_t retVal = CY_SYSPM_SUCCESS;




    if (pmCallbackRoot[cbDeepSleepRootIdx] != 
# 248 "/pdl/drivers/source/cy_syspm.c" 3 4
                                             ((void *)0)
# 248 "/pdl/drivers/source/cy_syspm.c"
                                                 )
    {
        retVal = Cy_SysPm_ExecuteCallback(CY_SYSPM_DEEPSLEEP, CY_SYSPM_CHECK_READY);
    }





    if (retVal == CY_SYSPM_SUCCESS)
    {



        interruptState = Cy_SysLib_EnterCriticalSection();
        if (pmCallbackRoot[cbDeepSleepRootIdx] != 
# 263 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                 ((void *)0)
# 263 "/pdl/drivers/source/cy_syspm.c"
                                                     )
        {
            (void) Cy_SysPm_ExecuteCallback(CY_SYSPM_DEEPSLEEP, CY_SYSPM_BEFORE_TRANSITION);
        }

        Cy_SysPm_CpuEnterDeepSleepNoCallbacks();

        Cy_SysLib_ExitCriticalSection(interruptState);
    }

    if (retVal == CY_SYSPM_SUCCESS)
    {



        if (pmCallbackRoot[cbDeepSleepRootIdx] != 
# 278 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                 ((void *)0)
# 278 "/pdl/drivers/source/cy_syspm.c"
                                                     )
        {
            (void) Cy_SysPm_ExecuteCallback(CY_SYSPM_DEEPSLEEP, CY_SYSPM_AFTER_TRANSITION);
        }
    }
    else
    {




        if (pmCallbackRoot[cbDeepSleepRootIdx] != 
# 289 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                 ((void *)0)
# 289 "/pdl/drivers/source/cy_syspm.c"
                                                     )
        {
            (void) Cy_SysPm_ExecuteCallback(CY_SYSPM_DEEPSLEEP, CY_SYSPM_CHECK_FAIL);
        }

    }
    return retVal;
}
# 314 "/pdl/drivers/source/cy_syspm.c"
void Cy_SysPm_CpuEnterDeepSleepNoCallbacks(void)
{

    (((SRSSLT_Type *) ((SRSSLT_Type*) 0x40030000UL))->PWR_KEY_DELAY) = (((SFLASH_Type *) ((SFLASH_Type*) 0x0FFFF000UL))->DPSLP_KEY_DELAY);


    (((SCB_Type *)((SCB_Type *) ((0xE000E000UL) + 0x0D00UL) ))->SCR) |= (1UL << 2U);
    __asm volatile ("wfi":::"memory");
}
# 340 "/pdl/drivers/source/cy_syspm.c"
void Cy_SysPm_SleepOnExit(
# 340 "/pdl/drivers/source/cy_syspm.c" 3 4
                         _Bool 
# 340 "/pdl/drivers/source/cy_syspm.c"
                              enable)
{
    if(enable)
    {

        (((SCB_Type *)((SCB_Type *) ((0xE000E000UL) + 0x0D00UL) ))->SCR) |= (1UL << 1U);
    }
    else
    {

        (((SCB_Type *)((SCB_Type *) ((0xE000E000UL) + 0x0D00UL) ))->SCR) &= (uint32_t) ~((1UL << 1U));
    }

}
# 390 "/pdl/drivers/source/cy_syspm.c"

# 390 "/pdl/drivers/source/cy_syspm.c" 3 4
_Bool 
# 390 "/pdl/drivers/source/cy_syspm.c"
    Cy_SysPm_RegisterCallback(cy_stc_syspm_callback_t* handler)
{
    
# 392 "/pdl/drivers/source/cy_syspm.c" 3 4
   _Bool 
# 392 "/pdl/drivers/source/cy_syspm.c"
        retVal = 
# 392 "/pdl/drivers/source/cy_syspm.c" 3 4
                 0
# 392 "/pdl/drivers/source/cy_syspm.c"
                      ;


    if ((handler != 
# 395 "/pdl/drivers/source/cy_syspm.c" 3 4
                   ((void *)0)
# 395 "/pdl/drivers/source/cy_syspm.c"
                       ) && (handler->callbackParams != 
# 395 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                        ((void *)0)
# 395 "/pdl/drivers/source/cy_syspm.c"
                                                            ) && (handler->callback != 
# 395 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                                                       ((void *)0)
# 395 "/pdl/drivers/source/cy_syspm.c"
                                                                                           ))
    {
        uint32_t callbackRootIdx = (uint32_t) handler->type;


        if (pmCallbackRoot[callbackRootIdx] != 
# 400 "/pdl/drivers/source/cy_syspm.c" 3 4
                                              ((void *)0)
# 400 "/pdl/drivers/source/cy_syspm.c"
                                                  )
        {
            cy_stc_syspm_callback_t* curCallback = pmCallbackRoot[callbackRootIdx];
            cy_stc_syspm_callback_t* insertPos = curCallback;




            while ((
# 408 "/pdl/drivers/source/cy_syspm.c" 3 4
                   ((void *)0) 
# 408 "/pdl/drivers/source/cy_syspm.c"
                        != curCallback->nextItm) && (curCallback != handler))
            {
                curCallback = curCallback->nextItm;



                if (curCallback->order <= handler->order)
                {
                    insertPos = curCallback;
                }
            }

            if (curCallback != handler)
            {

                if ((insertPos->prevItm == 
# 423 "/pdl/drivers/source/cy_syspm.c" 3 4
                                          ((void *)0)
# 423 "/pdl/drivers/source/cy_syspm.c"
                                              ) && (handler->order < insertPos->order))
                {
                    handler->nextItm = insertPos;
                    handler->prevItm = 
# 426 "/pdl/drivers/source/cy_syspm.c" 3 4
                                      ((void *)0)
# 426 "/pdl/drivers/source/cy_syspm.c"
                                          ;
                    handler->nextItm->prevItm = handler;
                    pmCallbackRoot[callbackRootIdx] = handler;
                }
                else
                {
                    handler->nextItm = insertPos->nextItm;
                    handler->prevItm = insertPos;


                    if (handler->nextItm != 
# 436 "/pdl/drivers/source/cy_syspm.c" 3 4
                                           ((void *)0)
# 436 "/pdl/drivers/source/cy_syspm.c"
                                               )
                    {
                        handler->nextItm->prevItm = handler;
                    }
                    insertPos->nextItm = handler;
                }
                retVal = 
# 442 "/pdl/drivers/source/cy_syspm.c" 3 4
                        1
# 442 "/pdl/drivers/source/cy_syspm.c"
                            ;
            }
        }
        else
        {

            pmCallbackRoot[callbackRootIdx] = handler;
            handler->nextItm = 
# 449 "/pdl/drivers/source/cy_syspm.c" 3 4
                              ((void *)0)
# 449 "/pdl/drivers/source/cy_syspm.c"
                                  ;
            handler->prevItm = 
# 450 "/pdl/drivers/source/cy_syspm.c" 3 4
                              ((void *)0)
# 450 "/pdl/drivers/source/cy_syspm.c"
                                  ;
            retVal = 
# 451 "/pdl/drivers/source/cy_syspm.c" 3 4
                    1
# 451 "/pdl/drivers/source/cy_syspm.c"
                        ;
        }
    }
    return retVal;
}
# 475 "/pdl/drivers/source/cy_syspm.c"

# 475 "/pdl/drivers/source/cy_syspm.c" 3 4
_Bool 
# 475 "/pdl/drivers/source/cy_syspm.c"
    Cy_SysPm_UnregisterCallback(cy_stc_syspm_callback_t const *handler)
{
    
# 477 "/pdl/drivers/source/cy_syspm.c" 3 4
   _Bool 
# 477 "/pdl/drivers/source/cy_syspm.c"
        retVal = 
# 477 "/pdl/drivers/source/cy_syspm.c" 3 4
                 0
# 477 "/pdl/drivers/source/cy_syspm.c"
                      ;

    if (handler != 
# 479 "/pdl/drivers/source/cy_syspm.c" 3 4
                  ((void *)0)
# 479 "/pdl/drivers/source/cy_syspm.c"
                      )
    {
        uint32_t callbackRootIdx = (uint32_t) handler->type;
        cy_stc_syspm_callback_t* curCallback = pmCallbackRoot[callbackRootIdx];


        while (curCallback != 
# 485 "/pdl/drivers/source/cy_syspm.c" 3 4
                             ((void *)0)
# 485 "/pdl/drivers/source/cy_syspm.c"
                                 )
        {

            if (curCallback == handler)
            {
                retVal = 
# 490 "/pdl/drivers/source/cy_syspm.c" 3 4
                        1
# 490 "/pdl/drivers/source/cy_syspm.c"
                            ;
                break;
            }


            curCallback = curCallback->nextItm;
        }

        if (retVal)
        {

            if (pmCallbackRoot[callbackRootIdx] == handler)
            {

                if (pmCallbackRoot[callbackRootIdx]->nextItm != 
# 504 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                               ((void *)0)
# 504 "/pdl/drivers/source/cy_syspm.c"
                                                                   )
                {
                    pmCallbackRoot[callbackRootIdx] = pmCallbackRoot[callbackRootIdx]->nextItm;
                    pmCallbackRoot[callbackRootIdx]->prevItm = 
# 507 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                              ((void *)0)
# 507 "/pdl/drivers/source/cy_syspm.c"
                                                                  ;
                }
                else
                {

                    pmCallbackRoot[callbackRootIdx] = 
# 512 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                     ((void *)0)
# 512 "/pdl/drivers/source/cy_syspm.c"
                                                         ;
                }
            }
            else
            {

                curCallback->prevItm->nextItm = curCallback->nextItm;

                if (curCallback->nextItm != 
# 520 "/pdl/drivers/source/cy_syspm.c" 3 4
                                           ((void *)0)
# 520 "/pdl/drivers/source/cy_syspm.c"
                                               )
                {
                    curCallback->nextItm->prevItm = curCallback->prevItm;
                }
            }
        }
    }

    return retVal;
}
# 564 "/pdl/drivers/source/cy_syspm.c"
cy_en_syspm_status_t Cy_SysPm_ExecuteCallback(cy_en_syspm_callback_type_t type, cy_en_syspm_callback_mode_t mode)
{
    do { if(!((((type) == CY_SYSPM_SLEEP) || ((type) == CY_SYSPM_DEEPSLEEP)))) { do { __asm("    bkpt    1"); } while(
# 566 "/pdl/drivers/source/cy_syspm.c" 3 4
   0
# 566 "/pdl/drivers/source/cy_syspm.c"
   ); } } while (
# 566 "/pdl/drivers/source/cy_syspm.c" 3 4
   0
# 566 "/pdl/drivers/source/cy_syspm.c"
   );
    do { if(!((((mode) == CY_SYSPM_CHECK_READY) || ((mode) == CY_SYSPM_CHECK_FAIL) || ((mode) == CY_SYSPM_BEFORE_TRANSITION) || ((mode) == CY_SYSPM_AFTER_TRANSITION)))) { do { __asm("    bkpt    1"); } while(
# 567 "/pdl/drivers/source/cy_syspm.c" 3 4
   0
# 567 "/pdl/drivers/source/cy_syspm.c"
   ); } } while (
# 567 "/pdl/drivers/source/cy_syspm.c" 3 4
   0
# 567 "/pdl/drivers/source/cy_syspm.c"
   );

    static cy_stc_syspm_callback_t* lastExecutedCallback = 
# 569 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                          ((void *)0)
# 569 "/pdl/drivers/source/cy_syspm.c"
                                                              ;
    cy_en_syspm_status_t retVal = CY_SYSPM_SUCCESS;
    cy_stc_syspm_callback_t* curCallback = pmCallbackRoot[(uint32_t) type];
    cy_stc_syspm_callback_params_t curParams;

    if ((mode == CY_SYSPM_BEFORE_TRANSITION) || (mode == CY_SYSPM_CHECK_READY))
    {




        while ((curCallback != 
# 580 "/pdl/drivers/source/cy_syspm.c" 3 4
                              ((void *)0)
# 580 "/pdl/drivers/source/cy_syspm.c"
                                  ) && ((retVal != CY_SYSPM_FAIL) || (mode != CY_SYSPM_CHECK_READY)))
        {

            if (0UL == ((uint32_t) mode & curCallback->skipMode))
            {

                curParams.base = curCallback->callbackParams->base;
                curParams.context = curCallback->callbackParams->context;

                retVal = curCallback->callback(&curParams, mode);







                lastExecutedCallback = curCallback;
            }
            curCallback = curCallback->nextItm;
        }

        if (mode == CY_SYSPM_CHECK_READY)
        {





            if(retVal == CY_SYSPM_FAIL)
            {
                failedCallback[(uint32_t) type] = lastExecutedCallback;
            }
            else
            {
                failedCallback[(uint32_t) type] = 
# 615 "/pdl/drivers/source/cy_syspm.c" 3 4
                                                 ((void *)0)
# 615 "/pdl/drivers/source/cy_syspm.c"
                                                     ;
            }
        }
    }
    else
    {






        if (mode != CY_SYSPM_CHECK_FAIL)
        {
            while (curCallback->nextItm != 
# 629 "/pdl/drivers/source/cy_syspm.c" 3 4
                                          ((void *)0)
# 629 "/pdl/drivers/source/cy_syspm.c"
                                              )
            {
                curCallback = curCallback->nextItm;
            }
        }
        else
        {



            curCallback = lastExecutedCallback;

            if (curCallback != 
# 641 "/pdl/drivers/source/cy_syspm.c" 3 4
                              ((void *)0)
# 641 "/pdl/drivers/source/cy_syspm.c"
                                  )
            {
                curCallback = curCallback->prevItm;
            }
        }


        while (curCallback != 
# 648 "/pdl/drivers/source/cy_syspm.c" 3 4
                             ((void *)0)
# 648 "/pdl/drivers/source/cy_syspm.c"
                                 )
        {

            if (0UL == ((uint32_t) mode & curCallback->skipMode))
            {

                curParams.base = curCallback->callbackParams->base;
                curParams.context = curCallback->callbackParams->context;

                retVal = curCallback->callback(&curParams, mode);
            }
            curCallback = curCallback->prevItm;
        }
    }

    return retVal;
}
# 689 "/pdl/drivers/source/cy_syspm.c"
cy_stc_syspm_callback_t* Cy_SysPm_GetFailedCallback(cy_en_syspm_callback_type_t type)
{
    return failedCallback[(uint32_t) type];
}
