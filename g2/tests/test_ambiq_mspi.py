# SPDX-License-Identifier: MIT
import importlib.util
import json
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / 'components/foundation/ambiq_mspi'
VERIFY = COMPONENT / 'simulator/verify.py'
HARNESS = r'''
#include "ambiq_mspi_compat.h"
#include <assert.h>
#include <string.h>
static opencfw_mspi_registers_t regs[3];
static unsigned mappings;
opencfw_mspi_registers_t *opencfw_mspi_fixture_registers(uint32_t m) {
    assert(m<3); ++mappings; return &regs[m];
}
int main(void) {
    unsigned module;
    for(module=0;module<3;++module) {
        am_hal_mspi_state_t h={0}; uint32_t status=0xdeadbeefu;
        h.prefix.u32=0xffbebebeu; h.ui32Module=module;
        assert(h.prefix.s.magic==0xbebebeu && h.prefix.s.bInit);
        memset(regs,0,sizeof(regs));
        regs[module].INTEN=0xaaaaaaaau; regs[module].INTSTAT=0x80000001u;
        assert(am_hal_mspi_interrupt_enable(&h,0x55555555u)==0);
        assert(regs[module].INTEN==0xffffffffu);
        assert(am_hal_mspi_interrupt_disable(&h,0x55555555u)==0);
        assert(regs[module].INTEN==0xaaaaaaaau);
        assert(am_hal_mspi_interrupt_status_get(&h,&status,false)==0);
        assert(status==0x80000001u);
        assert(am_hal_mspi_interrupt_status_get(&h,&status,true)==0);
        assert(status==(0x80000001u&0xaaaaaaaau));
        assert(am_hal_mspi_interrupt_clear(&h,0x80000001u)==0);
        assert(regs[module].INTCLR==0x80000001u);
        /* Ordinary host memory is not a W1C peripheral. */
        assert(regs[module].INTSTAT==0x80000001u);
        h.prefix.u32=0xbebebeu; mappings=0; status=0xdeadbeefu;
        assert(am_hal_mspi_interrupt_enable(&h,~0u)==2);
        assert(am_hal_mspi_interrupt_disable(&h,~0u)==2);
        assert(am_hal_mspi_interrupt_status_get(&h,&status,true)==2);
        assert(status==0xdeadbeefu);
        assert(am_hal_mspi_interrupt_clear(&h,~0u)==2);
        assert(mappings==0);
        assert(am_hal_mspi_interrupt_enable(0,~0u)==2);
        assert(am_hal_mspi_interrupt_status_get(0,0,false)==2);
        assert(mappings==0);
        h.prefix.u32=0x1bebebfu;
        assert(am_hal_mspi_interrupt_clear(&h,~0u)==2 && mappings==0);
    }
    return 0;
}
'''

@unittest.skipUnless(shutil.which('clang'), 'clang unavailable')
class AmbiqMspiTests(unittest.TestCase):
    def test_host_interrupt_contract_all_modules(self):
        with tempfile.TemporaryDirectory(prefix='ambiq-mspi-host-') as directory:
            d = Path(directory)
            (d/'test.c').write_text(HARNESS)
            build = subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                                    '-DOPENCFW_MSPI_HOST_FIXTURE', '-I', str(COMPONENT),
                                    str(COMPONENT/'ambiq_mspi_interrupts.c'), str(d/'test.c'),
                                    '-o', str(d/'test')], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(d/'test')], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)

    @unittest.skipUnless(shutil.which('arm-none-eabi-ld'), 'ARM linker unavailable')
    def test_linked_cortex_m55_entries(self):
        spec = importlib.util.spec_from_file_location('ambiq_verify', VERIFY)
        verify = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verify)
        with tempfile.TemporaryDirectory(prefix='ambiq-mspi-link-') as directory:
            result = subprocess.run(['make', '-C', str(ROOT), 'ambiq-mspi-simulator',
                                     'AMBIQ_SIM_DIR='+directory], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            _, segments, symbols = verify.loader.elf_info(Path(directory)/'ambiq_mspi.elf')
            for operation in ['enable', 'disable', 'status', 'clear', 'controller_disable', 'deinitialize']:
                self.assertIn('ambiq_sim_'+operation, symbols)
                address = symbols['ambiq_sim_'+operation] & ~1
                self.assertTrue(any(s['flags'] & 1 and s['address'] <= address <
                                    s['address']+len(s['data']) for s in segments))

    def test_exact_pinned_source_function_excerpts(self):
        manifest = json.loads((COMPONENT/'SOURCE_PROVENANCE.json').read_text())
        text = (COMPONENT/'ambiq_mspi_interrupts.c').read_text()
        for name, expected in manifest['function_text_sha256'].items():
            text = (COMPONENT/manifest['function_source_paths'][name]).read_text()
            start = text.index('uint32_t\n'+name+'(')
            opening = text.index('{', start)
            depth, end = 1, opening+1
            while depth:
                depth += (text[end] == '{') - (text[end] == '}')
                end += 1
            self.assertEqual(hashlib.sha256(text[start:end].encode()).hexdigest(), expected)
        self.assertIn('Redistribution and use in source and binary forms', text)
        self.assertIn('Copyright (c) 2025, Ambiq Micro, Inc.', text)

    def test_optimized_verifier_rejected(self):
        result = subprocess.run([sys.executable, '-O', str(VERIFY), '--help'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('optimized Python is rejected', result.stderr)

if __name__ == '__main__':
    unittest.main()
