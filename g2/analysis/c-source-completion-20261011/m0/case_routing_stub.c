
#include <stdint.h>
#include <stdbool.h>
bool case_legacy_known_dispatch(const uint8_t *p,uint32_t n,uint32_t *r)
{(void)n;*r=0x10000u+p[0];return p[0]!=0xeeu&&p[0]!=0xffu;}
uint32_t case_legacy_ee_prefix(const uint8_t *p,uint32_t n)
{(void)p;(void)n;return 0xee00u;}
uint32_t case_legacy_ff_prefix(const uint8_t *p,uint32_t n)
{(void)p;(void)n;return 0xff00u;}
bool case_binary_known_dispatch(const uint8_t *p,uint32_t n,uint32_t m,uint32_t *r)
{(void)n;(void)m;*r=0x20000u+p[0];return p[2]!=2u||(p[0]!=0x06u&&p[0]!=0x41u);}
uint32_t case_binary_06_41_candidate(const uint8_t *p,uint32_t n)
{(void)n;return p[0]==0x06u?0xee00u:0xff00u;}
uint32_t case_binary_ack0641(uint32_t x){return x;}
