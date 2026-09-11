# SPDX-License-Identifier: MIT
from tests import test_gx8002_frequency_dispatch as baseline
from tools import verify_gx8002_clock_size_probe as probe

class ProbeDispatchTests(baseline.FrequencyDispatchTests):
    @classmethod
    def setUpClass(cls):
        probe.verify()
        out=probe.ROOT/'build/gx8002-clock-frequency-size-probe'
        cls.code=probe.decode((out/'analysis.disassembly.txt').read_text())
        elf=probe.Elf32((out/'analysis.elf').read_bytes(),'frequency size probe')
        cls.table=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency'))
