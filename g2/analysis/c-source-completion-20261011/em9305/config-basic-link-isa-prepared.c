/* Native326f2a..326f4c: original wide accumulator shift retained for full/limited DSP configurations.
 * Argument is the already-selected maximum time; return is native ceil interval R4. */
extern uint32_t opencfw_em9305_config_link_interval_326f2a(uint32_t);
__asm__(
".text\n"
".align 2\n"
".global opencfw_em9305_config_link_interval_326f2a\n"
".type opencfw_em9305_config_link_interval_326f2a,@function\n"
"opencfw_em9305_config_link_interval_326f2a:\n"
"mpydu 0,r0,0x1a36e3\n"
"mov r4,225\n"
"aslacc r4\n"
"mov r8,1250\n"
"mov r4,r58\n"
"mpywhul r12,r8,r58\n"
"cmp_s r12,r0\n"
"add.c r4,r4,1\n"
"j_s.d [blink]\n"
"mov_s r0,r4\n"
".size opencfw_em9305_config_link_interval_326f2a,.-opencfw_em9305_config_link_interval_326f2a\n"
);
static inline uint32_t opencfw_em9305_config_link_mpywhul(uint32_t a,uint32_t b)
{uint32_t r;__asm__ volatile("mpywhul %0,%1,%2":"=r"(r):"r"(a),"r"(b));return r;}
static inline uint32_t opencfw_em9305_config_link_divu_prior(uint32_t a,uint32_t b,uint32_t prior)
{__asm__ volatile("divu %0,%1,%2":"+r"(prior):"r"(a),"r"(b));return prior;}
