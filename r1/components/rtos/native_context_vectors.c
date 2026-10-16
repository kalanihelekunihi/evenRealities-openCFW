/* Source-owned partial application vector configuration, authenticated against
 * R1 application SHA0e788d... . Other vector slots retain separate gates. */
#include <stdint.h>
void SVC_Handler(void);
void PendSV_Handler(void);
/* SDK declares this anchor as uint32_t; placement is application flash. */
uint32_t __isr_vector
 __attribute__((section(".r1.application.initial_sp"),aligned(4)))=UINT32_C(0x2003beb8);
void (*const r1_application_svc_vector)(void)
 __attribute__((section(".r1.application.svc_vector"),aligned(4)))=SVC_Handler;
void (*const r1_application_pendsv_vector)(void)
 __attribute__((section(".r1.application.pendsv_vector"),aligned(4)))=PendSV_Handler;
_Static_assert(sizeof(uint32_t)==4 && sizeof(r1_application_svc_vector)==4,"native vector words");
