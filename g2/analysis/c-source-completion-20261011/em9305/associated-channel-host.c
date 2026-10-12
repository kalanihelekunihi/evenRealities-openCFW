#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* Native324c98..324d6a: three bytewise permutations/MAM steps, native
 * low16 multiplier lanes, reciprocal37 and channel-map remap. */
uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t channels,uint32_t seed)
{
 uint32_t identity=*(volatile uint16_t *)(channels+48u),value=seed^identity;
 for(uint32_t round=0u;round<3u;++round){
  value=(value&0xf0f0u)|((value<<8u)&0xf0f00u);
  value=(value&0xcccc0u)|((value<<4u)&0x333300u);
  value=(value&0x2aaa80u)|((value<<2u)&0x555500u);
  value>>=7u;
  value=(value&65535u)*17u+identity;
 }
 uint32_t pseudo=value^identity;
 uint32_t quotient=((pseudo&65535u)*0xdd68u)>>21u;
 uint32_t choice=pseudo+(uint32_t)((int32_t)(int16_t)quotient*-37);
 uint32_t high=*(volatile uint32_t *)(channels+4u),low=*(volatile uint32_t *)channels;
 uint32_t index=((uint16_t)choice)&63u;
 uint32_t shifted=index==0u?low:index<32u?(low>>index)|(high<<(32u-index)):high>>(index-32u);
 if((shifted&1u)==0u){
  uint32_t count=*(volatile uint8_t *)(channels+45u);
  uint32_t remap=(count*(pseudo&65535u))>>16u;
  choice=*(volatile uint8_t *)(channels+8u+remap);
 }
 return (uint8_t)choice;
}

static unsigned reverse(unsigned b){unsigned r=0;for(unsigned i=0;i<8;i++)r=(r<<1)|((b>>i)&1);return r;}
static unsigned reference(uint8_t *r,unsigned seed){unsigned id=*(uint16_t*)(r+48),v=(seed^id)&65535;for(unsigned i=0;i<3;i++)v=(17*((reverse(v>>8)<<8)|reverse(v&255))+id)&65535;v^=id;unsigned channel=v%37;uint64_t map=*(uint32_t*)r|((uint64_t)*(uint32_t*)(r+4)<<32);if(!((map>>channel)&1))channel=r[8+((r[45]*v)>>16)];return channel;}
int main(void){unsigned ids[16]={0,1,2,3,17,255,256,257,1234,32767,32768,40000,60000,65533,65534,65535};unsigned cases=0;uint8_t r[64] __attribute__((aligned(4)));
for(unsigned identity=0;identity<16;identity++)for(unsigned kind=0;kind<4;kind++){
 memset(r,0x91,sizeof r);uint64_t map=kind==0?0x1fffffffffull:kind==1?0x1555555555ull:kind==2?0x100008002ull:0;*(uint32_t*)r=(uint32_t)map;*(uint32_t*)(r+4)=(uint32_t)(map>>32);unsigned n=0;for(unsigned i=0;i<37;i++)if((map>>i)&1)r[8+n++]=i;r[45]=n;*(uint16_t*)(r+48)=ids[identity];
 for(unsigned seed=0;seed<65536;seed++){
 if(opencfw_em9305_associated_channel_seed_324c98((uintptr_t)r,seed)!=reference(r,seed))abort();
 cases++;
 }
}
printf("PASS %u channel permutation/remap cases\n",cases);return 0;}
