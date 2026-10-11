#!/usr/bin/env python3
"""Bounded native branch, SRAM field and child-call checks for 0x1000a080."""
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_audio_channel_prepare.c"

STUB = '''#include <stdint.h>
uint32_t trace[64], trace_count, sample_bytes = 65;
static void record(uint32_t id, uint32_t a, uint32_t b, uint32_t c, uint32_t d) {
  uint32_t n=trace_count; trace[n]=id; trace[n+1]=a; trace[n+2]=b;
  trace[n+3]=c; trace[n+4]=d; trace_count=n+5;
}
uint32_t gx8002_image_b_audio_channel_address_1000a05c(uint32_t c) { return c; }
uint32_t gx8002_image_b_audio_channel_extent_1000a034(uint32_t c) { return c; }
uint32_t gx8002_image_b_audio_runtime_pointer_1000324c(void) { return 0; }
uint32_t gx8002_image_b_audio_sample_bytes_10009f5c(void) { return sample_bytes; }
int32_t gx8002_image_b_set_logfbank_enable_10005ab4(uint32_t a,uint32_t b) {record(1,a,b,0,0);return 0;}
uint32_t gx8002_image_b_dual_buffer_100054cc(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g) {record(2,a,b,c,d);record(3,e,f,g,0);return 0;}
uint32_t gx8002_image_b_pcm_path_1000568c(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f) {record(4,a,b,c,d);record(5,e,f,0,0);return 0;}
uint32_t gx8002_image_b_audio_capture_setup_100055e0(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e) {record(6,a,b,c,d);record(7,e,0,0,0);return 0;}
uint32_t gx8002_image_b_i2s_input_10005794(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g) {record(8,a,b,c,d);record(9,e,f,g,0);return 0;}
int32_t gx8002_image_b_audio_i2s_output_mode_100058ac(uint32_t a) {record(10,a,0,0,0);return 0;}
'''


def main():
    with tempfile.TemporaryDirectory() as temporary:
        stub = Path(temporary) / "stub.c"
        stub.write_text(STUB)
        binary = Path(temporary) / "audio.so"
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11", str(SOURCE), str(stub), "-o", str(binary)], check=True)
        lib = ctypes.CDLL(str(binary))
        function = lib.gx8002_image_b_audio_channel_prepare_at_1000a080
        function.argtypes = [ctypes.POINTER(ctypes.c_uint32)] + [ctypes.c_uint32] * 4
        function.restype = None
        trace = (ctypes.c_uint32 * 64).in_dll(lib, "trace")
        count = ctypes.c_uint32.in_dll(lib, "trace_count")
        sample_bytes = ctypes.c_uint32.in_dll(lib, "sample_bytes")

        def run(flags, channel, address, extent, byte5=0, byte21=0,
                preset=None):
            state = (ctypes.c_uint32 * 64)()
            count.value = 0
            for offset, value in (preset or {}).items():
                state[offset // 4] = value
            raw = (ctypes.c_uint8 * ctypes.sizeof(state)).from_buffer(state)
            raw[5] = byte5
            raw[0x21] = byte21
            function(state, flags, channel, address, extent)
            return state, list(trace)[:count.value]

        cases = 0
        state, calls = run(0, 1, 0x103, 512, byte5=8)
        assert [state[x // 4] for x in (0x7c,0x80,0x84,0x88,0x8c)] == [0x100,0x200,256,256,0]
        assert calls == [2,1,0x100,0x200,256,3,256,0,0,0]
        cases += 1

        state, calls = run(8, 1, 0x103, 512, byte5=8,
                           preset={0x80:0x777,0x90:0xabc,0xe8:3,0xec:4})
        assert [state[x // 4] for x in (0x7c,0x80,0x84,0x88,0xdc,0xe0,0xe4)] == [0x100,0x777,512,1024,0x100,512,64]
        assert calls == [1,1,1,0,0,4,1,0x100,512,64,5,3,4,0,0,2,1,0x100,0x777,512,3,1024,0,0xabc,0]
        cases += 1

        sample_bytes.value = 65
        state, calls = run(0, 2, 0x205, 512, byte21=8)
        assert [state[x // 4] for x in (0x94,0x98,0x9c,0xa0,0xa4)] == [0x200,0x300,256,64,0]
        assert calls[0:5] == [2,2,0x200,0x300,256]
        cases += 1

        sample_bytes.value = 0xffffffff
        state, calls = run(1, 2, 0x205, 512)
        assert [state[x // 4] for x in (0x94,0x98,0x9c,0xa0)] == [0x200,0,512,0]
        cases += 1

        state, calls = run(0, 4, 0x303, 99, preset={0xb8:3,0xbc:4})
        assert [state[x // 4] for x in (0xac,0xb0,0xb4)] == [0x300,99,1]
        assert calls == [1,1,1,0,0,6,0x300,99,1,3,7,4,0,0,0]
        cases += 1

        state, calls = run(0, 8, 0, 0,
                           preset={0xc0:1,0xc4:2,0xc8:3,0xcc:4,
                                   0xd0:5,0xd4:6,0xd8:7})
        assert calls == [8,1,2,3,4,9,5,6,7,0,10,0,0,0,0]
        cases += 1

        state, calls = run(0, 3, 0, 0)
        assert calls == [] and list(state) == [0] * 64
        cases += 1

    receipt = {"native_entry": "0x1000a080", "image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "bounded_cases": cases, "result": "PASS",
               "native_evidence": "Instruction span 0x1000a080..0x1000a29c, four channel cases, 7th stack argument at 0xa100/0xa168, logfbank r0=r1=1 at 0xa18c and 0xa262.",
               "limit": "Host relocated SRAM state and stubbed child calls; actual MMIO, runtime pointer placement and physical audio unqualified."}
    path = HERE / "audio-channel-prepare-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
