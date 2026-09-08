# SPDX-License-Identifier: MIT
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class PowerRegistrationTests(unittest.TestCase):
    def test_capacity_duplicate_and_null_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);harness=path/'test.c'
            harness.write_text('''
#include <assert.h>
#include <string.h>
#include "runtime_gx8002_power_registration.h"
struct open_cfw_gx8002_power_state open_cfw_gx8002_power_state;
void *open_cfw_gx8002_memcpy(void *d,const void *s,size_t n){return memcpy(d,s,n);}
#define CB(N) static int c##N(void *p){(void)p;return N;}
CB(0) CB(1) CB(2) CB(3) CB(4) CB(5) CB(6) CB(7) CB(8)
int main(void){
 int (*callbacks[])(void *)={c0,c1,c2,c3,c4,c5,c6,c7,c8};
 for(int mode=0;mode<2;++mode){
  memset(&open_cfw_gx8002_power_state,0,sizeof(open_cfw_gx8002_power_state));
  int (*reg)(struct open_cfw_app_power_registration *)=mode?open_cfw_gx8002_register_resume:open_cfw_gx8002_register_suspend;
  struct open_cfw_app_power_registration *slots=mode?open_cfw_gx8002_power_state.resume:open_cfw_gx8002_power_state.suspend;
  uint32_t *count=mode?&open_cfw_gx8002_power_state.resume_count:&open_cfw_gx8002_power_state.suspend_count;
  struct open_cfw_app_power_registration entry={0,(void *)123};
  assert(reg(&entry)==0 && *count==0 && slots[0].private_data==(void *)123);
  for(int i=0;i<8;++i){entry.callback=callbacks[i];assert(reg(&entry)==0 && *count==(unsigned)i+1);}
  entry.callback=c8;assert(reg(&entry)==-1 && *count==8);
  entry.callback=c3;entry.private_data=(void *)456;assert(reg(&entry)==0 && *count==8 && slots[3].private_data==(void *)456);
  entry.callback=0;assert(reg(&entry)==-1 && *count==8);
 }
 return 0;
}
''')
            source=ROOT/'components/shared/gx8002'
            subprocess.run(['clang','-DOPEN_CFW_GX8002_POWER_HOST_TEST','-I',str(source),str(harness),str(source/'runtime_gx8002_power_registration.c'),'-o',str(path/'test')],check=True)
            subprocess.run([str(path/'test')],check=True)

if __name__=='__main__':unittest.main()
