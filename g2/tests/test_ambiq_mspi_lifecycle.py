# SPDX-License-Identifier: MIT
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMPONENT=ROOT/'components/foundation/ambiq_mspi'
HARNESS=r'''
#include "ambiq_mspi_compat.h"
#include <assert.h>
#include <string.h>
static opencfw_mspi_registers_t regs[3];
static unsigned n; static uint32_t events[3],cq_result,delay_arg;
static am_hal_mspi_state_t *current;
opencfw_mspi_registers_t *opencfw_mspi_fixture_registers(uint32_t m){assert(m<3);return &regs[m];}
uint32_t mspi_cq_disable(void *h){assert(h==current);assert(current->prefix.s.bEnable);events[n++]=1;return cq_result;}
uint32_t mspi_cq_term(void *h){assert(h==current);assert(current->prefix.s.bEnable);events[n++]=2;return 0;}
void am_hal_delay_us(uint32_t d){assert(!current->prefix.s.bEnable);events[n++]=3;delay_arg=d;}
static void reset(am_hal_mspi_state_t *h,unsigned module){
    memset(h,0,sizeof(*h));h->prefix.u32=0x3bebebeu;h->ui32Module=module;
    h->ui32XIPOffMinDelay=17;memset(regs,0,sizeof(regs));current=h;n=0;cq_result=0;delay_arg=0;
}
int main(void){
    am_hal_mspi_state_t h,before; unsigned m;
    for(m=0;m<3;++m){
        reset(&h,m);h.ui32NumCQEntries=1;before=h;
        assert(am_hal_mspi_disable(&h)==3 && n==0 && memcmp(&h,&before,sizeof(h))==0);
        assert(am_hal_mspi_deinitialize(&h)==0 && n==0);
        assert(h.prefix.u32==0x2bebebeu && h.ui32Module==0 && h.ui32NumCQEntries==1);
        /* Successful deinit did not drain outstanding work or clear enable. */
        reset(&h,m);h.ui32NumHPEntries=1;before=h;
        assert(am_hal_mspi_disable(&h)==3 && n==0 && memcmp(&h,&before,sizeof(h))==0);
        reset(&h,m);h.pTCB=0x20008000u;cq_result=13;regs[m].DEV0XIP=1;before=h;
        assert(am_hal_mspi_disable(&h)==13 && n==1 && events[0]==1);
        assert(memcmp(&h,&before,sizeof(h))==0);
        n=0;assert(am_hal_mspi_deinitialize(&h)==0 && n==1 && events[0]==1);
        assert(h.prefix.u32==0x2bebebeu && h.ui32Module==0);
        reset(&h,m);h.pTCB=0x20008000u;regs[m].DEV0XIP=0x80000001u;
        assert(am_hal_mspi_disable(&h)==0 && n==3);
        assert(events[0]==1 && events[1]==2 && events[2]==3 && delay_arg==17);
        assert(h.prefix.u32==0x1bebebeu && h.ui32Module==m && h.pTCB==0x20008000u);
        n=0;assert(am_hal_mspi_disable(&h)==0 && n==0);
        reset(&h,m);regs[m].DEV0XIP=0x80000000u;
        assert(am_hal_mspi_disable(&h)==0 && n==0 && h.prefix.u32==0x1bebebeu);
        reset(&h,m);h.prefix.u32=0x1bebebeu;h.ui32NumCQEntries=5;
        assert(am_hal_mspi_disable(&h)==0 && n==0 && h.ui32NumCQEntries==5);
        reset(&h,m);h.prefix.u32=0x2bebebeu;before=h;
        assert(am_hal_mspi_disable(&h)==2 && n==0 && memcmp(&h,&before,sizeof(h))==0);
        assert(am_hal_mspi_deinitialize(&h)==2 && n==0);
        assert(am_hal_mspi_disable(0)==2 && am_hal_mspi_deinitialize(0)==2);
    }
    return 0;
}
'''

class AmbiqLifecycleTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('clang'),'clang unavailable')
    def test_busy_error_and_provider_order_contract(self):
        with tempfile.TemporaryDirectory(prefix='ambiq-lifecycle-host-') as directory:
            d=Path(directory);(d/'test.c').write_text(HARNESS)
            build=subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror',
                                  '-DOPENCFW_MSPI_HOST_FIXTURE','-I',str(COMPONENT),
                                  str(COMPONENT/'ambiq_mspi_lifecycle.c'),str(d/'test.c'),
                                  '-o',str(d/'test')],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stderr)
            run=subprocess.run([str(d/'test')],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)

    def test_optimized_lifecycle_verifier_rejected(self):
        run=subprocess.run([sys.executable,'-O',str(COMPONENT/'simulator/verify_lifecycle.py'),'--help'],capture_output=True,text=True)
        self.assertNotEqual(run.returncode,0)
        self.assertIn('optimized Python is rejected',run.stderr)

if __name__=='__main__':unittest.main()
