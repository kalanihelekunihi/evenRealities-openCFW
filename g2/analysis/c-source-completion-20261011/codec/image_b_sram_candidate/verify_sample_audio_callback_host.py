#!/usr/bin/env python3
"""Bounded host state cuts for the experimental native-audio callback model.

This rebases MMIO/SRAM and substitutes only the C-SKY divu instruction with
host division on tested nonzero divisors. It is not original-byte equivalence.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_sample_app_audio_callback.c"
HERE = Path(__file__).resolve().parent
HARNESS = r'''
#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
volatile uint32_t fixture_state[11], fixture_flags[2], fixture_handle;
volatile uint32_t fixture_mmio_ts, fixture_mmio_audio;
static uint32_t frame_seen[2], pushes, logs;
int gx8002_image_b_heap_log_10009934(const char *format,...)
{ (void)format; ++logs; return 0; }
void fixture_push(uint32_t *frame)
{ frame_seen[0]=frame[0]; frame_seen[1]=frame[1]; ++pushes; }
extern void gx8002_image_b_sample_app_audio_callback_1000bef4(uint32_t,uint32_t);
static void reset(void)
{ memset((void*)fixture_state,0,sizeof fixture_state);
  memset((void*)fixture_flags,0,sizeof fixture_flags);
  frame_seen[0]=frame_seen[1]=pushes=logs=0;
  fixture_mmio_ts=fixture_mmio_audio=fixture_handle=0; }
static int check(int ok,const char *name)
{ if(!ok){fprintf(stderr,"FAIL %s\n",name);return 1;} return 0; }
int main(void)
{
  reset(); fixture_flags[0]=1; fixture_flags[1]=(uint32_t)-4;
  fixture_state[10]=64;
  gx8002_image_b_sample_app_audio_callback_1000bef4(0,1);
  if(check(pushes==1 && frame_seen[0]==0 && frame_seen[1]==1 &&
           fixture_flags[0]==1 && fixture_flags[1]==(uint32_t)-3 &&
           logs==3,"initial and recovery")) return 1;

  reset(); fixture_state[10]=100; fixture_state[9]=50;
  fixture_mmio_ts=100; fixture_mmio_audio=50;
  gx8002_image_b_sample_app_audio_callback_1000bef4(2,5);
  if(check(pushes==1 && frame_seen[0]==6 && frame_seen[1]==9 &&
           fixture_state[8]==50 && fixture_flags[0]==0 && logs==0,
           "direct window")) return 1;

  reset(); fixture_state[2]=UINT32_MAX; fixture_state[3]=UINT32_MAX;
  fixture_state[10]=64; fixture_mmio_ts=0; fixture_mmio_audio=0;
  gx8002_image_b_sample_app_audio_callback_1000bef4(0,2);
  if(check(fixture_state[4]==1 && fixture_state[5]==0 &&
           fixture_state[8]==6144 && pushes==1,"timestamp wrap")) return 1;

  puts("3 experimental audio callback state cuts PASS"); return 0;
}
'''

def main():
    source = SOURCE.read_text()
    source = """#include <stdint.h>
extern volatile uint32_t fixture_state[11], fixture_flags[2], fixture_handle;
extern volatile uint32_t fixture_mmio_ts, fixture_mmio_audio;
extern void fixture_push(uint32_t *);
""" + source
    addresses = {
        "0x2002d360": "(uintptr_t)fixture_state",
        "0x20016f6c": "(uintptr_t)fixture_flags",
        "0x2002d798": "(uintptr_t)&fixture_handle",
        "0xa0a00148": "(uintptr_t)&fixture_mmio_ts",
        "0xa0b80010": "(uintptr_t)&fixture_mmio_audio",
    }
    for original, replacement in addresses.items():
        source = source.replace("UINT32_C(" + original + ")", replacement)
    source, count = re.subn(
        r"static uint32_t native_unsigned_divide\(.*?\n\}\n\nvoid gx8002",
        "static uint32_t native_unsigned_divide(uint32_t n,uint32_t d) "
        "{ return n/d; }\n\nvoid gx8002", source, flags=re.S)
    if count != 1:
        raise RuntimeError("native divider replacement failed")
    source = source.replace(
        "(void)gx8002_image_b_audio_out_push_frame_10006b60(\n"
        "        *audio_handle, (uint32_t)(uintptr_t)frame);",
        "(void)audio_handle; fixture_push(frame);")
    with tempfile.TemporaryDirectory(prefix="audio-callback-host-",dir=HERE) as temp:
        out = Path(temp)
        (out / "source.c").write_text(source)
        (out / "test.c").write_text(HARNESS)
        subprocess.run(["clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        str(out / "source.c"), str(out / "test.c"),
                        "-o", str(out / "test")], check=True)
        run = subprocess.run([str(out / "test")], text=True,
                             capture_output=True)
        if run.returncode:
            raise RuntimeError(run.stdout + run.stderr)
        receipt = {
            "source": str(SOURCE.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "cases": ["initial_and_recovery", "direct_window", "timestamp_wrap"],
            "result": "PASS",
            "scope": "host MMIO/SRAM rebasing, stubbed logger/output and nonzero host divider only; no original-byte or hardware proof",
        }
        (HERE / "sample-audio-callback-host-receipt.json").write_text(
            json.dumps(receipt, indent=2) + "\n")
        print(run.stdout.strip())

if __name__ == "__main__":
    main()
