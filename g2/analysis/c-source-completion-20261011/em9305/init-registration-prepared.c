/* Native initializer registration identities. These extern functions are
 * referenced only by address; their signatures/bodies remain genuine gates. */
extern void opencfw_em9305_init_registered_31e8fc(void);
extern void opencfw_em9305_init_registered_321608(void);
extern void opencfw_em9305_init_registered_32182c(void);
extern void opencfw_em9305_init_registered_322d68(void);
extern void opencfw_em9305_init_registered_32613c(void);
extern void opencfw_em9305_init_registered_3263ec(void);
extern void opencfw_em9305_init_registered_32ce04(void);
extern void opencfw_em9305_init_registered_3266f8(void);
extern void opencfw_em9305_init_registered_324fb4(void);
/* Native307cb8..307cc2 equality getter, no incoming-argument use. */
uint32_t opencfw_em9305_init_state_one_307cb8(void)
{return *(volatile uint8_t *)(uintptr_t)0x8051a4u==1u;}
/* Native307c18..307c5a. Delayed slot zero occurs on both version branches. */
uint32_t opencfw_em9305_init_lower_307c18(uint32_t incoming)
{
 (void)incoming;uintptr_t cfg=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(cfg+4u);
 *(volatile uint32_t *)(uintptr_t)0x80297cu=(uint32_t)(uintptr_t)opencfw_em9305_init_registered_31e8fc;
 *(volatile uint32_t *)(uintptr_t)0x80130cu=(uint32_t)(uintptr_t)opencfw_em9305_init_state_one_307cb8;
 *(volatile uint32_t *)(uintptr_t)0x805228u=0u;
 if(version<9u)return version;
 uint32_t flags=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=flags|(1u<<13u);
 return 0x805b30u;
}
/* Native307cc8..307d0a. Callback identity stores precede version load. */
uint32_t opencfw_em9305_init_lower_307cc8(uint32_t incoming)
{
 (void)incoming;uintptr_t cfg=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint32_t *)(uintptr_t)0x802984u=(uint32_t)(uintptr_t)opencfw_em9305_init_registered_321608;
 uint32_t version=*(volatile uint8_t *)(cfg+4u);
 *(volatile uint32_t *)(uintptr_t)0x805230u=(uint32_t)(uintptr_t)opencfw_em9305_init_registered_32182c;
 if(version>=9u){uint32_t flags=*(volatile uint32_t *)(uintptr_t)0x805b30u;*(volatile uint32_t *)(uintptr_t)0x805b30u=flags|(1u<<13u);}
 *(volatile uint16_t *)(uintptr_t)0x805b22u=784u;
 return 0x805b0cu;
}
/* Native307d2c..307d60, native capability bit25 threshold10. */
uint32_t opencfw_em9305_init_lower_307d2c(uint32_t incoming)
{
 (void)incoming;uintptr_t cfg=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint32_t *)(uintptr_t)0x802980u=(uint32_t)(uintptr_t)opencfw_em9305_init_registered_322d68;
 uint32_t version=*(volatile uint8_t *)(cfg+4u);
 *(volatile uint32_t *)(uintptr_t)0x80522cu=0u;
 if(version<10u)return version;
 uint32_t flags=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=flags|(1u<<25u);
 return 0x805b30u;
}
/* Native307de8..307e2e, all five source relocation identities. */
uint32_t opencfw_em9305_init_lower_307de8(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x8052bcu=(uint32_t)(uintptr_t)opencfw_em9305_init_registered_32613c;
 *(volatile uint32_t *)(uintptr_t)0x8052c0u=(uint32_t)(uintptr_t)opencfw_em9305_init_registered_3263ec;
 *(volatile uint32_t *)(uintptr_t)0x8056d8u=(uint32_t)(uintptr_t)opencfw_em9305_init_registered_32ce04;
 *(volatile uint32_t *)(uintptr_t)0x8052c4u=(uint32_t)(uintptr_t)opencfw_em9305_init_registered_3266f8;
 *(volatile uint32_t *)(uintptr_t)0x8051f4u=(uint32_t)(uintptr_t)opencfw_em9305_init_registered_324fb4;
 return 0x8051f4u;
}
