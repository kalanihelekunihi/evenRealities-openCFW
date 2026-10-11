#!/usr/bin/env python3
"""Bounded native FFT VAD policy transitions and bit selection."""
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_audio_vad_policy.c"
STUB = '''#include <stdint.h>
#include <stdarg.h>
#include <string.h>
struct state { uint32_t low,middle,high; uint16_t index; };
struct chips { uint16_t a,b,c,d; };
struct weights { uint8_t a,b,c; };
struct state sample;
uint32_t trace[96], count;
static void record(uint32_t id,uint32_t a,uint32_t b,uint32_t c,uint32_t d) {
  uint32_t n=count; trace[n]=id;trace[n+1]=a;trace[n+2]=b;
  trace[n+3]=c;trace[n+4]=d;count=n+5;
}
uint32_t gx8002_image_b_audio_read_status_10005cb0(void){return 0;}
int32_t gx8002_image_b_set_fftvad_curve_1_10005b34(uint32_t a,uint32_t b){record(1,a,b,0,0);return 0;}
int32_t gx8002_image_b_set_fftvad_curve_2_10005b68(uint32_t a,uint32_t b){record(2,a,b,0,0);return 0;}
int32_t gx8002_image_b_set_fftvad_curve_3_10005b9c(uint16_t a,int16_t b){record(3,a,(uint16_t)b,0,0);return 0;}
int32_t gx8002_image_b_set_fftvad_curve_4_10005bdc(uint32_t a,uint32_t b){record(4,a,b,0,0);return 0;}
int32_t gx8002_image_b_set_fftvad_curve_5_10005c10(uint32_t a){record(5,a,0,0,0);return 0;}
int32_t gx8002_image_b_set_fftvad_chipping_10005c30(struct chips x){record(6,x.a,x.b,x.c,x.d);return 0;}
int32_t gx8002_image_b_set_fftvad_w_10005af8(struct weights x){record(7,x.a,x.b,x.c,0);return 0;}
int32_t gx8002_image_b_get_fftvad_state_10005c80(struct state *out){record(8,0,0,0,0);*out=sample;return 0;}
int gx8002_image_b_heap_log_10009934(const char *format,...){
  va_list args;va_start(args,format);uint32_t status=va_arg(args,uint32_t);va_end(args);
  uint32_t mode=strstr(format,"param 3")?3:strstr(format,"param 2")?2:1;
  record(9,mode,status,0,0);return 0;
}
'''


class Sample(ctypes.Structure):
    _fields_ = [("low",ctypes.c_uint32),("middle",ctypes.c_uint32),
                ("high",ctypes.c_uint32),("index",ctypes.c_uint16)]


def main():
    with tempfile.TemporaryDirectory() as temporary:
        stub = Path(temporary) / "stub.c"
        stub.write_text(STUB)
        binary = Path(temporary) / "vad.so"
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11", str(SOURCE), str(stub), "-o", str(binary)], check=True)
        lib = ctypes.CDLL(str(binary))
        policy = lib.gx8002_image_b_audio_vad_policy_at_1000a470
        policy.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        policy.restype = ctypes.c_uint32
        sample = Sample.in_dll(lib,"sample")
        trace = (ctypes.c_uint32*96).in_dll(lib,"trace")
        count = ctypes.c_uint32.in_dll(lib,"count")
        mode = ctypes.c_uint32(0)
        def run(status):
            count.value=0
            result=policy(status,ctypes.byref(mode))
            calls=list(trace)[:count.value]
            return result,[calls[i:i+5] for i in range(0,len(calls),5)]
        cases=0

        sample.index=1;sample.low=1;sample.middle=0;sample.high=0
        result,calls=run(0x002fffff)
        assert result==1 and mode.value==4
        assert [row[0] for row in calls]==[1,2,3,4,5,6,7,8]
        assert calls[0][1:3]==[1229,3840] and calls[3][1:3]==[2560,1024]
        assert calls[6][1:4]==[3,0,0]
        cases+=1

        result,calls=run(0)
        assert result==1 and [row[0] for row in calls]==[8]
        cases+=1

        result,calls=run(0x00300000)
        assert mode.value==3 and [row[0] for row in calls]==[9,1,2,3,4,5,6,7,8]
        assert calls[0][1:3]==[3,0x300000] and calls[4][1:3]==[1843,819]
        assert calls[7][1:4]==[1,1,3]
        cases+=1

        result,calls=run(0x005fffff)
        assert mode.value==3 and [row[0] for row in calls]==[8]
        cases+=1

        result,calls=run(0x00600000)
        assert mode.value==2 and calls[0][1:3]==[2,0x600000]
        assert calls[7][1:4]==[1,1,10]
        cases+=1

        result,calls=run(0x01400000)
        assert mode.value==2 and [row[0] for row in calls]==[8]
        cases+=1

        sample.low=0
        result,calls=run(0x01400001)
        assert mode.value==1 and result==1 and calls[0][1:3]==[1,0x1400001]
        assert calls[1][1:3]==[1024,3840] and calls[2][1:3]==[1229,1536]
        cases+=1

        result,calls=run(0xffffffff)
        assert mode.value==1 and result==1 and [row[0] for row in calls]==[8]
        cases+=1

        mode.value=2
        sample.index=33;sample.middle=1;sample.low=0
        result,calls=run(0x00600000)
        assert result==1 and [row[0] for row in calls]==[8]
        cases+=1

        sample.index=0;sample.middle=0;sample.high=1<<30
        result,calls=run(0x00600000)
        assert result==1 and [row[0] for row in calls]==[8]
        cases+=1

        sample.high=0
        result,calls=run(0x00600000)
        assert result==0 and [row[0] for row in calls]==[8]
        cases+=1

        sample.index=1;sample.low=1
        result,calls=run(0x00600000)
        assert result==1 and [row[0] for row in calls]==[8]
        cases+=1

    receipt={"native_entry":"0x1000a470","image_sha256":"d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "bounded_cases":cases,"result":"PASS",
             "native_evidence":"Complete 0x1000a470..0x1000a702 ISA trace, including mode 1/2/3 transitions marked unreachable in retained decompiler; exact curve, chipping, weight constants and logger strings at 0x100132b8/d4/f0.",
             "limit":"Host setter/getter stubs and relocated mode word; real audio MMIO, boot initialization of 0x2002cb84, and physical VAD unqualified."}
    path=HERE/"audio-vad-policy-receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(path)


if __name__=="__main__":main()
