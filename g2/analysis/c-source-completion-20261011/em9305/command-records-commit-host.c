#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uintptr_t R,S,Rows,Data,Cfg;static unsigned seed,phase,randoms,fail;
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){if(id!=seed)fail++;return phase==1?0:R;}
static uint32_t opencfw_em9305_config_limit_mpyuw(uint32_t a,uint32_t b){return (a&65535)*(b&65535);}
static uint32_t opencfw_em9305_radio_duration_312be4(uint32_t phy,uint32_t requested,uint32_t timing,uint32_t spacing,uint32_t size,uint32_t extended,uint32_t mode,uint32_t overhead){if(phy!=1||requested||timing||spacing!=1200||extended||mode!=2||overhead!=5)fail++;return size*10+200;}
static void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
static uint32_t opencfw_em9305_pal_random_step(void){return seed*0x01010101u+randoms++;}
/* Authenticated 334550..334950 CRC table, stock image SHA 0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03. */
static const uint32_t opencfw_em9305_crc_table_334550[256]={
 0x00000000u,0x77073096u,0xee0e612cu,0x990951bau,0x076dc419u,0x706af48fu,0xe963a535u,0x9e6495a3u,
 0x0edb8832u,0x79dcb8a4u,0xe0d5e91eu,0x97d2d988u,0x09b64c2bu,0x7eb17cbdu,0xe7b82d07u,0x90bf1d91u,
 0x1db71064u,0x6ab020f2u,0xf3b97148u,0x84be41deu,0x1adad47du,0x6ddde4ebu,0xf4d4b551u,0x83d385c7u,
 0x136c9856u,0x646ba8c0u,0xfd62f97au,0x8a65c9ecu,0x14015c4fu,0x63066cd9u,0xfa0f3d63u,0x8d080df5u,
 0x3b6e20c8u,0x4c69105eu,0xd56041e4u,0xa2677172u,0x3c03e4d1u,0x4b04d447u,0xd20d85fdu,0xa50ab56bu,
 0x35b5a8fau,0x42b2986cu,0xdbbbc9d6u,0xacbcf940u,0x32d86ce3u,0x45df5c75u,0xdcd60dcfu,0xabd13d59u,
 0x26d930acu,0x51de003au,0xc8d75180u,0xbfd06116u,0x21b4f4b5u,0x56b3c423u,0xcfba9599u,0xb8bda50fu,
 0x2802b89eu,0x5f058808u,0xc60cd9b2u,0xb10be924u,0x2f6f7c87u,0x58684c11u,0xc1611dabu,0xb6662d3du,
 0x76dc4190u,0x01db7106u,0x98d220bcu,0xefd5102au,0x71b18589u,0x06b6b51fu,0x9fbfe4a5u,0xe8b8d433u,
 0x7807c9a2u,0x0f00f934u,0x9609a88eu,0xe10e9818u,0x7f6a0dbbu,0x086d3d2du,0x91646c97u,0xe6635c01u,
 0x6b6b51f4u,0x1c6c6162u,0x856530d8u,0xf262004eu,0x6c0695edu,0x1b01a57bu,0x8208f4c1u,0xf50fc457u,
 0x65b0d9c6u,0x12b7e950u,0x8bbeb8eau,0xfcb9887cu,0x62dd1ddfu,0x15da2d49u,0x8cd37cf3u,0xfbd44c65u,
 0x4db26158u,0x3ab551ceu,0xa3bc0074u,0xd4bb30e2u,0x4adfa541u,0x3dd895d7u,0xa4d1c46du,0xd3d6f4fbu,
 0x4369e96au,0x346ed9fcu,0xad678846u,0xda60b8d0u,0x44042d73u,0x33031de5u,0xaa0a4c5fu,0xdd0d7cc9u,
 0x5005713cu,0x270241aau,0xbe0b1010u,0xc90c2086u,0x5768b525u,0x206f85b3u,0xb966d409u,0xce61e49fu,
 0x5edef90eu,0x29d9c998u,0xb0d09822u,0xc7d7a8b4u,0x59b33d17u,0x2eb40d81u,0xb7bd5c3bu,0xc0ba6cadu,
 0xedb88320u,0x9abfb3b6u,0x03b6e20cu,0x74b1d29au,0xead54739u,0x9dd277afu,0x04db2615u,0x73dc1683u,
 0xe3630b12u,0x94643b84u,0x0d6d6a3eu,0x7a6a5aa8u,0xe40ecf0bu,0x9309ff9du,0x0a00ae27u,0x7d079eb1u,
 0xf00f9344u,0x8708a3d2u,0x1e01f268u,0x6906c2feu,0xf762575du,0x806567cbu,0x196c3671u,0x6e6b06e7u,
 0xfed41b76u,0x89d32be0u,0x10da7a5au,0x67dd4accu,0xf9b9df6fu,0x8ebeeff9u,0x17b7be43u,0x60b08ed5u,
 0xd6d6a3e8u,0xa1d1937eu,0x38d8c2c4u,0x4fdff252u,0xd1bb67f1u,0xa6bc5767u,0x3fb506ddu,0x48b2364bu,
 0xd80d2bdau,0xaf0a1b4cu,0x36034af6u,0x41047a60u,0xdf60efc3u,0xa867df55u,0x316e8eefu,0x4669be79u,
 0xcb61b38cu,0xbc66831au,0x256fd2a0u,0x5268e236u,0xcc0c7795u,0xbb0b4703u,0x220216b9u,0x5505262fu,
 0xc5ba3bbeu,0xb2bd0b28u,0x2bb45a92u,0x5cb36a04u,0xc2d7ffa7u,0xb5d0cf31u,0x2cd99e8bu,0x5bdeae1du,
 0x9b64c2b0u,0xec63f226u,0x756aa39cu,0x026d930au,0x9c0906a9u,0xeb0e363fu,0x72076785u,0x05005713u,
 0x95bf4a82u,0xe2b87a14u,0x7bb12baeu,0x0cb61b38u,0x92d28e9bu,0xe5d5be0du,0x7cdcefb7u,0x0bdbdf21u,
 0x86d3d2d4u,0xf1d4e242u,0x68ddb3f8u,0x1fda836eu,0x81be16cdu,0xf6b9265bu,0x6fb077e1u,0x18b74777u,
 0x88085ae6u,0xff0f6a70u,0x66063bcau,0x11010b5cu,0x8f659effu,0xf862ae69u,0x616bffd3u,0x166ccf45u,
 0xa00ae278u,0xd70dd2eeu,0x4e048354u,0x3903b3c2u,0xa7672661u,0xd06016f7u,0x4969474du,0x3e6e77dbu,
 0xaed16a4au,0xd9d65adcu,0x40df0b66u,0x37d83bf0u,0xa9bcae53u,0xdebb9ec5u,0x47b2cf7fu,0x30b5ffe9u,
 0xbdbdf21cu,0xcabac28au,0x53b39330u,0x24b4a3a6u,0xbad03605u,0xcdd70693u,0x54de5729u,0x23d967bfu,
 0xb3667a2eu,0xc4614ab8u,0x5d681b02u,0x2a6f2b94u,0xb40bbe37u,0xc30c8ea1u,0x5a05df1bu,0x2d02ef8du,
};
/* Native304678..304698: ordered byte loads and complement of fullword state. */
uint32_t opencfw_em9305_crc_update_304678(uint32_t state,uint32_t count,uintptr_t input)
{
 if(count!=0u)do{uint32_t byte=*(volatile uint8_t *)input++;uint32_t index=(uint8_t)state^byte;state=(state>>8)^opencfw_em9305_crc_table_334550[index];}while(--count!=0u);
 return ~state;
}
/* Native3096a8..309874: complete validation, timing, free-slot allocation,
 * partial writes and fresh post-child base loads. */
uint32_t opencfw_em9305_command_records_commit_3096a8(uint32_t id,uint32_t count,uintptr_t rows)
{
 if(id>239u)return 18u;
 uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);
 if(record==0u)return 66u;
 uintptr_t row_state=record+796u;
 if(*(volatile uint8_t *)(record+718u)==0u)return 12u;
 if(count-1u>=15u)return 18u;
 for(uint32_t i=0u;i<count;++i){uintptr_t row=rows+i*8u;
  if(*(volatile uint8_t *)(row+3u)>251u)return 18u;
  uint32_t value=*(volatile uint8_t *)(row+1u),maximum=*(volatile uint8_t *)(row_state+2u);
  if(maximum<value)return 18u;
  uint32_t index=*(volatile uint8_t *)row;
  if(index>=15u)return 18u;
  uintptr_t configuration=*(volatile uint32_t *)(record+0xafcu);
  uint32_t start=*(volatile uint8_t *)(configuration+78u),span=*(volatile uint8_t *)(configuration+79u);
  if(start+span<=index||index<start)return 12u;
  uint32_t current=*(volatile uint8_t *)(row_state+3u);
  if(index<current)return 70u;
  if(index==current&&*(volatile uint8_t *)(row_state-107u)!=0u)return 70u;
 }
 for(uint32_t i=0u;i<count;++i){
  uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t spacing=*(volatile uint16_t *)(configuration+20u),live_spacing=*(volatile uint32_t *)(record+72u);
  if(live_spacing>spacing)spacing=live_spacing;
  uint32_t budget;
  if(*(volatile uint8_t *)(row_state+2u)!=0u)budget=opencfw_em9305_config_limit_mpyuw(*(volatile uint8_t *)row_state,1250u);
  else budget=*(volatile uint32_t *)(record+792u);
  uint32_t timing=0u;
  if(*(volatile uint8_t *)(row_state+8u)!=0u){uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801a14u;if(callback)timing=((uint32_t(*)(uint32_t))callback)(*(volatile uint8_t *)(row_state+8u));}
  uint32_t size=*(volatile uint8_t *)(rows+i*8u+3u),phy=*(volatile uint8_t *)(record+63u);
  uint32_t needed=opencfw_em9305_radio_duration_312be4(phy,0u,timing,(uint16_t)spacing,size,0u,2u,5u);
  if(budget-150u<needed)return 69u;
 }
 uintptr_t base=*(volatile uint32_t *)(row_state+364u);
 for(uint32_t i=0u;i<count;++i){
  uint32_t high=*(volatile uint32_t *)(base+0xf08u),low=*(volatile uint32_t *)(base+0xf04u);
  uintptr_t mask_pointer=base+0xf04u;
  uint32_t free_index=255u;
  for(uint32_t bit=0u;bit<15u;++bit)if((low&(1u<<bit))!=0u){free_index=bit;break;}
  if(free_index==255u)return 7u;
  uintptr_t row=rows+i*8u;
  uint32_t index=*(volatile uint8_t *)row;
  uintptr_t mapping=base+index+0xf0cu;
  if(*(volatile uint8_t *)mapping!=255u)return 18u;
  *(volatile uint8_t *)mapping=(uint8_t)free_index;
  base=*(volatile uint32_t *)(row_state+364u);
  uint32_t size=*(volatile uint8_t *)(row+3u);
  low&=~(1u<<free_index);
  uintptr_t slot=base+(free_index<<8);
  uintptr_t source=*(volatile uint32_t *)(row+4u);
  *(volatile uint32_t *)(mask_pointer+4u)=high;
  *(volatile uint32_t *)mask_pointer=low;
  *(volatile uint8_t *)(slot+1u)=(uint8_t)size;
  (void)opencfw_em9305_memcpy((void *)(slot+4u),(const void *)source,size);
  source=*(volatile uint32_t *)(row+4u);size=*(volatile uint8_t *)(row+3u);
  uint32_t seed=opencfw_em9305_pal_random_step();
  uint32_t checksum=opencfw_em9305_crc_update_304678(seed,size,source);
  base=*(volatile uint32_t *)(row_state+364u);
  uint32_t first=*(volatile uint8_t *)(row+1u),second=*(volatile uint8_t *)(row+2u);
  slot=base+(free_index<<8);
  *(volatile uint16_t *)(slot+2u)=(uint16_t)checksum;
  *(volatile uint8_t *)slot=1u;
  *(volatile uint8_t *)(base+0xf00u)=(uint8_t)first;
  *(volatile uint8_t *)(base+0xf01u)=(uint8_t)second;
 }
 *(volatile uint8_t *)(record+1156u)=1u;
 return 0u;
}

static uint32_t refcrc(uint32_t st,unsigned n,const uint8_t *data){for(unsigned i=0;i<n;i++){st^=data[i];for(unsigned b=0;b<8;b++)st=(st>>1)^((0u-(st&1u))&0xedb88320u);}return ~st;}
int main(void){if(mmap((void*)0x800000,0x60000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)return 2;R=0x810000;S=0x820000;Rows=0x830000;Data=0x831000;Cfg=0x832000;unsigned cases=0;
 uint8_t expected[4096],beforeR[2824];
 for(seed=0;seed<256;seed++)for(unsigned n=1;n<16;n++)for(phase=0;phase<16;phase++){
  memset((void*)R,0xa5,2824);memset((void*)S,0xa5,4096);memset((void*)Rows,0,128);for(unsigned i=0;i<256;i++)*(uint8_t*)(Data+i)=seed+37*i;
  *(uint8_t*)(R+718)=phase==2?0:1;*(uint8_t*)(R+798)=10;*(uint8_t*)(R+799)=phase==10?1:0;*(uint8_t*)(R+689)=phase==11?1:0;*(uint8_t*)(R+796)=10;*(uint8_t*)(R+804)=0;*(uint32_t*)(R+72)=1200;*(uint8_t*)(R+63)=1;
  *(uint32_t*)(R+0xafc)=Cfg;*(uint8_t*)(Cfg+78)=phase==9?1:0;*(uint8_t*)(Cfg+79)=phase==8?0:15;*(uint32_t*)0x805cac=Cfg;*(uint16_t*)(Cfg+20)=1000;*(uint32_t*)(R+1160)=S;
  if(phase==12){*(uint8_t*)(R+798)=0;*(uint32_t*)(R+792)=150;}
  *(uint32_t*)(S+0xf04)=phase==13?0:phase==15?1:32767;*(uint32_t*)(S+0xf08)=0xabcdef01;
  memset((void*)(S+0xf0c),255,15);if(phase==14)*(uint8_t*)(S+0xf0c)=2;
  unsigned size=seed%16;
  for(unsigned i=0;i<n;i++){uintptr_t row=Rows+i*8;*(uint8_t*)row=i;*(uint8_t*)(row+1)=phase==12?0:5;*(uint8_t*)(row+2)=7;*(uint8_t*)(row+3)=size;*(uint32_t*)(row+4)=Data;}
  if(phase==5)*(uint8_t*)(Rows+3)=252;if(phase==6)*(uint8_t*)(Rows+1)=11;if(phase==7)*(uint8_t*)Rows=15;
  unsigned count=phase==3?0:phase==4?16:n;
  memcpy(expected,(void*)S,4096);memcpy(beforeR,(void*)R,2824);randoms=0;
  uint32_t want=0;unsigned processed=n;
  if(seed>239){want=18;processed=0;}else if(phase==1){want=66;processed=0;}else if(phase==2){want=12;processed=0;}else if(phase>=3&&phase<=7){want=18;processed=0;}else if(phase==8||phase==9){want=12;processed=0;}else if(phase==10||phase==11){want=70;processed=0;}else if(phase==12){want=69;processed=0;}else if(phase==13){want=7;processed=0;}else if(phase==14){want=18;processed=0;}else if(phase==15&&n>1){want=7;processed=1;}
  for(unsigned i=0;i<processed;i++){
   expected[0xf0c+i]=i;*(uint32_t*)(expected+0xf04)&=~(1u<<i);expected[i*256+1]=size;memcpy(expected+i*256+4,(void*)Data,size);*(uint16_t*)(expected+i*256+2)=(uint16_t)refcrc(seed*0x01010101u+i,size,(void*)Data);expected[i*256]=1;expected[0xf00]=5;expected[0xf01]=7;
  }
  if(want==0)beforeR[1156]=1;
  uint32_t got=opencfw_em9305_command_records_commit_3096a8(seed,count,Rows);
  if(got!=want||randoms!=processed||memcmp(expected,(void*)S,4096)||memcmp(beforeR,(void*)R,2824)){if(fail<3)printf("mismatch %u/%u/%u got%u want%u random%u/%u\n",seed,n,phase,got,want,randoms,processed);fail++;}
  cases++;
 }
 printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;
}
