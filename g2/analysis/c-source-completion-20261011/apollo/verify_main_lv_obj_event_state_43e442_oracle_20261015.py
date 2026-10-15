#!/usr/bin/env python3
"""Compare Apollo LV base event-state callback with controlled stock calls."""
import hashlib, json, re, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_event_state_43e442.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-obj-event-state-43e442"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def put(c, address, value): c.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))

def cases():
    base = dict(code=0x1a, initial=0, cover_style=0, contains=1,
                color1=0xfd, color2=0xfd, b4=0, cc=0xfd, c0=0xfd,
                table=0, table_count=0, low_index=-1, draw_style=0,
                draw_enable=0)
    result = []
    def add(**fields): result.append(base | fields)
    add(code=0)
    add(initial=2)
    add(cover_style=1)
    add(contains=0)
    add(color1=0xfc)
    add(color2=0xfc)
    add(b4=1, cc=0xfc)
    add(b4=1, c0=0xfc)
    add()
    add(table=1, table_count=0)
    add(table=1, table_count=2, low_index=0)
    add(table=1, table_count=2, low_index=1)
    add(table=1, table_count=2)
    add(code=0x1d, draw_style=0)
    add(code=0x1d, draw_style=1)
    add(code=0x20, draw_enable=0, draw_style=1)
    add(code=0x20, draw_enable=1, draw_style=0)
    add(code=0x20, draw_enable=1, draw_style=1)
    return result

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        obj, shim, elf = directory / "event.o", directory / "shim.c", directory / "event.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-c",
                        str(SOURCE), "-o", str(obj)], check=True)
        providers = [line.split()[-1] for line in subprocess.check_output(
            ["arm-none-eabi-nm", "-u", str(obj)], text=True).splitlines()]
        addresses = {name: int(re.search(r"_([0-9a-f]{6})$", name).group(1), 16)
                     for name in providers}
        if len(addresses) != 21: raise RuntimeError("event-state provider set changed")
        shim.write_text("#include <stdint.h>\n" + "\n".join(
            f"uint32_t {name}(void){{return 0;}}" for name in providers) + "\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_obj_event_state_43e442",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, cfg):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            event, obj_addr, param, clip, table = (0x20011000, 0x20012000,
                                                   0x20013000, 0x20014000,
                                                   0x20015000)
            c.mem_write(event, bytes([0xa5]) * 0x30)
            c.mem_write(obj_addr, bytes([0x55]) * 0x80)
            c.mem_write(param, bytes([0x77]) * 0x30)
            c.mem_write(clip, bytes([0x22]) * 0x20)
            c.mem_write(table, bytes([0xff]) * 0x30)
            c.mem_write(obj_addr + 0x14, bytes(range(16)))
            put(c, event, obj_addr); put(c, event + 8, cfg["code"])
            put(c, event + 0x10, param)
            c.mem_write(param, bytes([cfg["initial"]]))
            put(c, param + 4, clip)
            c.mem_write(table + 10, bytes([cfg["table_count"]]))
            if cfg["low_index"] >= 0:
                c.mem_write(table + 3 + cfg["low_index"] * 5, b"\xfc")
            targets = {(syms[name] if compiled else native) & ~1: native
                       for name, native in addresses.items()}
            trace = []
            def hook(c, address, size, _):
                native = targets.get(address)
                if native is None: return
                op = f"{native:06x}"
                r0, r1, r2 = (c.reg_read(r) for r in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                value = 0
                if native in (0x450286, 0x451960):
                    trace.append((op, r0))
                    value = cfg["code"] if native == 0x450286 else 0x20016000
                elif native == 0x43dcc0:
                    data = bytes(c.mem_read(r1, 16))
                    trace.append((op, data))
                    c.mem_write(r0, data)
                elif native == 0x450b98:
                    trace.append((op, bytes(c.mem_read(r0, 16)), r1, r2))
                    c.mem_write(r0, bytes([0x66]) * 16)
                elif native == 0x450f28:
                    trace.append((op, r0, bytes(c.mem_read(r1, 16)), r2))
                    value = cfg["contains"]
                elif native == 0x451b9c:
                    trace.append((op,))
                    c.mem_write(r0, bytes(range(0x70)))
                elif native == 0x452616:
                    trace.append((op, r0, r1, bytes(c.mem_read(r2, 0x70))))
                    c.mem_write(r2 + 0x49, b"\x04")
                elif native == 0x451c6e:
                    trace.append((op, r0, bytes(c.mem_read(r1, 0x70)),
                                  bytes(c.mem_read(r2, 16))))
                elif native == 0x43e63e:
                    trace.append((op, r0, r1))
                else:
                    trace.append((op, r0, r1))
                    values = {0x43de54: cfg["cover_style"], 0x43de4a: 7,
                              0x43dd72: 2, 0x43dd7c: 3,
                              0x43dda8: cfg["color1"], 0x43de6a: cfg["color2"],
                              0x43ddb4: cfg["b4"], 0x43ddcc: cfg["cc"],
                              0x43ddc0: cfg["c0"], 0x43ddd8: table if cfg["table"] else 0,
                              0x43de06: cfg["draw_style"],
                              0x43ddfc: cfg["draw_enable"]}
                    value = values[native]
                c.reg_write(A.UC_ARM_REG_R0, value & 0xffffffff)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, event)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms["audio_uart_lv_obj_event_state_43e442"] if compiled else 0x43e442
            c.emu_start(start | 1, 0x600000, count=100000)
            return trace, bytes(c.mem_read(event, 0x20)), bytes(c.mem_read(param, 0x20)), \
                   bytes(c.mem_read(obj_addr, 0x40))
        suite = cases()
        for index, cfg in enumerate(suite):
            native, source = run(False, cfg), run(True, cfg)
            if native != source: raise AssertionError((index, cfg, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_OBJ_EVENT_STATE_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x43e442..0x43e63d", "cases": len(suite),
               "controlled_provider_count": len(addresses),
               "limits": ["Lower calls and scratch mutations are controlled; live drawing, style cascade, allocation and device behavior remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), len(addresses), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
