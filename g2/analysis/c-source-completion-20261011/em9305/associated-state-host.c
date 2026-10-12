#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_radio_record_available_307410(uint32_t);
extern uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t);
extern uint32_t opencfw_em9305_associated_action_32b5ec(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_event_32b4e4(uintptr_t);
/* Native30a328..30a378. Return retains native incidental R0. */
uint32_t opencfw_em9305_init_lower_30a328(uint32_t incoming)
{
 (void)incoming;uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(config+4u);
 *(volatile uint32_t *)(uintptr_t)0x802978u=(uint32_t)(uintptr_t)opencfw_em9305_associated_event_32b4e4;
 *(volatile uint32_t *)(uintptr_t)0x801310u=(uint32_t)(uintptr_t)opencfw_em9305_radio_record_available_307410;
 *(volatile uint32_t *)(uintptr_t)0x805224u=0u;
 if(version<9u)return (uint32_t)config;
 uint32_t flags=*(volatile uint32_t *)(uintptr_t)0x805b30u;flags|=1u<<13u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=flags;
 if(version<12u)return flags;
 uint32_t second=*(volatile uint32_t *)(uintptr_t)0x805b34u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=flags;
 *(volatile uint32_t *)(uintptr_t)0x805b34u=second|(1u<<4u);
 return flags;
}
/* Native32b4e4..32b536: event over one or every active2824B associated row. */
uint32_t opencfw_em9305_associated_event_32b4e4(uintptr_t event)
{
 *(volatile uint32_t *)(uintptr_t)0x805cc0u=(uint32_t)event;
 if(*(volatile uint8_t *)(event+2u)!=255u){
  uintptr_t record=opencfw_em9305_radio_record_find_31aa64(*(volatile uint8_t *)event);
  if(record==0u)return 0u;
  return opencfw_em9305_associated_action_32b5ec(record,*(volatile uint8_t *)(event+3u));
 }
 uint32_t number=0u,offset=0u;
 for(;;){
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t count=*(volatile uint8_t *)(config+12u);
  if(number>=count)return count;
  uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c38u;record+=offset;
  if(*(volatile uint8_t *)record!=0u)(void)opencfw_em9305_associated_action_32b5ec(record,*(volatile uint8_t *)(event+3u));
  offset+=2824u;number++;
 }
}
extern uint32_t opencfw_em9305_associated_action_324b3c(uintptr_t);
extern uint32_t opencfw_em9305_associated_action_324c60(uintptr_t);
extern uint32_t opencfw_em9305_associated_action_324aa8(uintptr_t);
extern uint32_t opencfw_em9305_associated_action_324aa0(uintptr_t);
extern uint32_t opencfw_em9305_associated_action_324a8c(uintptr_t);
typedef uint32_t (*opencfw_em9305_associated_action_fn)(uintptr_t);
const opencfw_em9305_associated_action_fn opencfw_em9305_associated_actions_335328[16]={
0,opencfw_em9305_associated_action_324b3c,0,0,0,opencfw_em9305_associated_action_324c60,opencfw_em9305_associated_action_324aa8,0,0,opencfw_em9305_associated_action_324aa0,opencfw_em9305_associated_action_324aa0,opencfw_em9305_associated_action_324a8c,0,opencfw_em9305_associated_action_324aa0,opencfw_em9305_associated_action_324aa0,0
};
const uint8_t opencfw_em9305_associated_transitions_335368[16]={0u,1u,0u,0u,3u,1u,2u,0u,3u,2u,2u,0u,3u,3u,3u,0u};
/* Native32b5ec..32b614: callback-mutated state is reloaded before transition. */
uint32_t opencfw_em9305_associated_action_32b5ec(uintptr_t record,uint32_t action)
{
 uint32_t state=*(volatile uint8_t *)(record+368u);
 opencfw_em9305_associated_action_fn callback=opencfw_em9305_associated_actions_335328[state*4u+action];
 if(callback!=0){(void)callback(record);state=*(volatile uint8_t *)(record+368u);}
 uint32_t next=opencfw_em9305_associated_transitions_335368[state*4u+action];
 *(volatile uint8_t *)(record+368u)=(uint8_t)next;return next;
}

static uint8_t rows[16*2824] __attribute__((aligned(4))),config[20],event[4];static unsigned calls;
uint32_t opencfw_em9305_radio_record_available_307410(uint32_t p){return p;}
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t p){return p<16&&rows[p*2824]? (uintptr_t)(rows+p*2824):0;}
static uint32_t hook(uintptr_t p){calls++;uint8_t*r=(void*)p;r[368]=(r[368]+1)%4;return 991;}
uint32_t opencfw_em9305_associated_action_324b3c(uintptr_t p){return hook(p);}
uint32_t opencfw_em9305_associated_action_324c60(uintptr_t p){return hook(p);}
uint32_t opencfw_em9305_associated_action_324aa8(uintptr_t p){return hook(p);}
uint32_t opencfw_em9305_associated_action_324aa0(uintptr_t p){return hook(p);}
uint32_t opencfw_em9305_associated_action_324a8c(uintptr_t p){return hook(p);}
int main(void){
 if(mmap((void*)0x800000,0x7000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 *(volatile uint32_t*)0x805cac=(uint32_t)(uintptr_t)config;*(volatile uint32_t*)0x805c38=(uint32_t)(uintptr_t)rows;
 unsigned cases=0;
 for(unsigned version=0;version<256;version++)for(unsigned seed=0;seed<256;seed++){
 config[4]=version;uint32_t first=seed*0x1020304u,second=~first;*(volatile uint32_t*)0x805b30=first;*(volatile uint32_t*)0x805b34=second;*(volatile uint32_t*)0x805224=~seed;
 uint32_t expected=version<9?(uint32_t)(uintptr_t)config:first|(1u<<13);
 if(opencfw_em9305_init_lower_30a328(seed)!=expected||*(volatile uint32_t*)0x805224||*(volatile uint32_t*)0x805b30!=(version<9?first:expected)||*(volatile uint32_t*)0x805b34!=(version<12?second:second|16)||*(volatile uint32_t*)0x802978!=(uint32_t)(uintptr_t)opencfw_em9305_associated_event_32b4e4||*(volatile uint32_t*)0x801310!=(uint32_t)(uintptr_t)opencfw_em9305_radio_record_available_307410)abort();
 cases++;
 }
 for(unsigned state=0;state<4;state++)for(unsigned action=0;action<4;action++){
 rows[368]=state;calls=0;unsigned present=opencfw_em9305_associated_actions_335328[state*4+action]!=0;unsigned nextstate=present?(state+1)%4:state;unsigned expected=opencfw_em9305_associated_transitions_335368[nextstate*4+action];
 if(opencfw_em9305_associated_action_32b5ec((uintptr_t)rows,action)!=expected||rows[368]!=expected||calls!=present)abort();
 cases++;
 }
 for(unsigned n=0;n<=16;n++)for(unsigned mask=0;mask<256;mask++){
 memset(rows,0,sizeof rows);config[12]=n;event[2]=255;event[3]=1;unsigned expectcalls=0;
 for(unsigned i=0;i<n;i++){rows[i*2824]= (mask>>(i%8))&1;rows[i*2824+368]=0;expectcalls+=rows[i*2824];}
 calls=0;if(opencfw_em9305_associated_event_32b4e4((uintptr_t)event)!=n||calls!=expectcalls||*(volatile uint32_t*)0x805cc0!=(uint32_t)(uintptr_t)event)abort();
 cases++;
 }
 for(unsigned id=0;id<17;id++)for(unsigned present=0;present<2;present++){
 memset(rows,0,sizeof rows);if(id<16)rows[id*2824]=present;event[0]=id;event[2]=0;event[3]=1;calls=0;unsigned expected=(id<16&&present)?1:0;
 if(opencfw_em9305_associated_event_32b4e4((uintptr_t)event)!=expected||calls!=(id<16&&present))abort();
 cases++;
 }
 printf("PASS %u version/callback/row cases\n",cases);return 0;
}
