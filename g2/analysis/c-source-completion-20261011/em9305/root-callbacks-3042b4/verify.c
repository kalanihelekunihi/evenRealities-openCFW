#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#define R32(p) (*(uint32_t *)(uintptr_t)(p))
#define R8(p) (*(uint8_t *)(uintptr_t)(p))
uint32_t opencfw_em9305_callback_3042b4(uint32_t);
static unsigned cancels,finishes;static uint32_t expected_finish;
uint32_t opencfw_em9305_auxiliary_ready_303f68(void){return 0x810000;}
uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t p)
{assert(p==0x8015c4&&R8(p)==0);cancels++;return 505;}
uint32_t opencfw_em9305_common_radio_finish_3045c0(uint32_t p)
{assert(p==expected_finish);finishes++;return 606;}
int main(void)
{
 assert(mmap((void *)(uintptr_t)0x810000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)(uintptr_t)0x810000);
 assert(mmap((void *)(uintptr_t)0x801000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)(uintptr_t)0x801000);
 for(unsigned cb=0;cb<2;cb++)for(unsigned kind=0;kind<2;kind++)for(unsigned own=0;own<2;own++)for(unsigned flag=0;flag<3;flag++){
  cancels=finishes=0;R32(0x81002c)=0x810100;R32(0x810174)=cb?123:0;R8(0x810100)=kind?15:7;R8(0x8015c4)=flag;
  unsigned enabled=cb||kind;expected_finish=own?(cb?0x810100:15):505;
  uint32_t expected=!enabled?7:!own&&flag!=1?0x8015c4:606;
  assert(opencfw_em9305_callback_3042b4(own?99:0)==expected);
  assert(cancels==(enabled&&!own&&flag==1));assert(finishes==(enabled&&(own||flag==1)));
 }
 return 0;
}
