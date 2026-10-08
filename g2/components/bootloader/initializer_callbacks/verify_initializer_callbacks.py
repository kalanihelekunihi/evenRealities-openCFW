#!/usr/bin/env python3
"""Differentially exercise source bodies for three locked init callbacks."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location(
    "bootv", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

RAM_CALLBACKS = {}
CUTS = {
    0x430280: "descriptor-register",
    0x42E8D0: "adc-context-initialize",
    0x42EC0C: "adc-configure",
    0x42F020: "adc-profile-transfer",
    0x42EB74: "adc-context-configure",
    0x42EA68: "adc-apply-profile",
    0x42EAF6: "adc-configure-channel",
    0x42ED60: "adc-activate",
    0x42EBAA: "adc-enable",
    0x42EFF4: "adc-command",
    0x42EE70: "adc-enumerate",
    0x42EBE2: "adc-disable",
    0x42EDA0: "adc-normalize",
    0x42EA32: "adc-reset",
    0x415FAE: "generic-log",
    0x41F530: "post-register-mode",
    0x422AD4: "post-context-register",
    0x422BA8: "post-configure",
    0x42308E: "post-validate",
    0x422DC6: "post-activate",
    0x41F512: "post-enable",
    0x41F4F4: "post-precommit",
    0x4236CE: "post-finish",
    0x41F8BA: "post-record-initialized",
    0x42C4C6: "platform-context-claim",
    0x42C988: "platform-config-transaction",
    0x42CC34: "platform-instance-configure",
    0x42C538: "platform-context-enable",
    0x43048E: "platform-config-retry",
    0x42C63A: "platform-interrupt-enable",
    0x430470: "platform-nvic-enable",
    0x416762: "platform-semaphore-create",
    0x41A684: "service-guard",
    0x4175B4: "service-commit",
    0x41A69A: "service-wake",
    0x41A6A2: "service-sleep",
    0x417439: "invalid-service-enable",
    0x417511: "invalid-service-configure",
    0x416610: "mutex-create",
    0x4176CE: "logger-output",
}


class CallbackMachine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None,
                 mutex_returns=(0x2002A000, 0x2002A100),
                 service_guard_return=0, provider_returns=None,
                 adc_samples=(0, 0, 3200)):
        self.events = []
        self.mutex_returns = list(mutex_returns)
        self.mutex_index = 0
        self.service_guard_return = service_guard_return
        self.provider_returns = {"platform-semaphore-create": 0x2002B000}
        self.adc_samples = list(adc_samples)
        self.adc_sample_index = 0
        if provider_returns:
            self.provider_returns.update(provider_returns)
        self.finished = False
        self.trace = {}
        super().__init__(source, segments, symbols)
        self.cpu.mem_map(0x40010000, 0x1000)
        self.cpu.mem_map(0x40038000, 0x1000)
        self.cpu.mem_write(0x40038038, struct.pack("<I", 1 << 20))
        self.cpu.mem_write(0xe000ed88, struct.pack("<I", 0x00f00000))
        self.cpu.reg_write(v.a.UC_ARM_REG_FPEXC, 0x40000000)
        if source:
            # One fixed scalar consumed by the index-2 branch; this is read-only
            # data fixture only, not copied stock executable code.
            raw = v.BLOB.read_bytes()
            for address, size in ((0x43419c, 4), (0x434170, 4),
                                  (0x434174, 4), (0x431ab8, 4),
                                  (0x43402c, 8)):
                self.cpu.mem_write(address, raw[address - v.BASE:
                                                address - v.BASE + size])
        else:
            # Unicorn's ARM M-profile models do not implement the stock
            # VCVT.F64.F32 / VSTR D0 / VMOV D0 instructions. Replace only
            # these fixed instructions with NOPs and emulate their defined
            # register/memory effects in the code hook below; original bytes
            # remain recorded from the locked blob.
            for address in (0x430048, 0x43004C, 0x430054,
                            0x430058, 0x43019E, 0x4301A2):
                self.cpu.mem_write(address, b"\x00\xbf\x00\xbf")

    def code(self, uc, pc, size, _):
        if pc == v.STOP:
            self.finished = True
            uc.emu_stop()
            return
        if not self.source and pc in {0x430048, 0x43004C, 0x430054,
                                       0x430058, 0x43019E, 0x4301A2}:
            raw = v.BLOB.read_bytes()[pc - v.BASE:pc - v.BASE + 4]
            self.trace[hex(pc)] = raw.hex()
            if pc in {0x430048, 0x430054, 0x43019E}:
                single_bits = uc.reg_read(v.a.UC_ARM_REG_S0)
                single = struct.unpack("<f", struct.pack("<I", single_bits))[0]
                self.fp_d0 = int.from_bytes(struct.pack("<d", single), "little")
            elif pc == 0x43004C:
                sp = uc.reg_read(v.a.UC_ARM_REG_SP)
                uc.mem_write(sp, self.fp_d0.to_bytes(8, "little"))
            elif pc in {0x430058, 0x4301A2}:
                uc.reg_write(v.a.UC_ARM_REG_R2, self.fp_d0 & 0xffffffff)
                uc.reg_write(v.a.UC_ARM_REG_R3, self.fp_d0 >> 32)
            return
        if self.source and pc == 0x4174A6:
            self.events.append(["invalid-pin-configure", *self.args()])
            self.ret()
            return
        if pc in CUTS:
            name = CUTS[pc]
            args = self.args()
            if name == "mutex-create":
                value = self.mutex_returns[self.mutex_index]
                self.mutex_index += 1
                self.events.append([name, args[0], value])
                self.ret(value)
            elif name == "logger-output":
                sp = uc.reg_read(v.a.UC_ARM_REG_SP)
                line = self.u(sp)
                message = self.u(sp + 4)
                self.events.append([name, *args, line, message])
                self.ret()
            elif name in {"platform-bringup", "post-bringup-setup"}:
                # These callees have no ABI arguments; their entry R0-R3 are
                # caller-saved residue. 430000 overwrites R0/R1 immediately;
                # 41f612 initializes its working registers before use.
                self.events.append([name])
                self.ret()
            elif name == "service-guard":
                self.events.append([name, *args, self.service_guard_return])
                self.ret(self.service_guard_return)
            elif name == "service-commit":
                # The no-argument stock helper clears its working registers
                # before using them; entry R0-R3 are caller-saved residue.
                self.events.append([name])
                self.ret()
            elif name in {"service-wake", "service-sleep"}:
                # The stock wrappers immediately call their own no-argument
                # helper; incoming R0-R3 are not consumed.
                self.events.append([name])
                self.ret()
            elif name == "platform-semaphore-create":
                value = self.provider_returns[name]
                self.events.append([name, *args[:3], value])
                self.ret(value)
            elif name == "adc-context-initialize":
                value = self.provider_returns.get(name, 0)
                context = self.provider_returns.get("adc-context", 0x20002000)
                self.w(args[1], context)
                self.events.append([name, args[0], context, value])
                self.ret(value)
            elif name == "adc-configure":
                self.events.append([name, args[0], args[1],
                                    bytes(uc.mem_read(args[2], 16)).hex()])
                self.ret()
            elif name == "adc-context-configure":
                self.events.append([name, args[0],
                                    bytes(uc.mem_read(args[1], 8)).hex()])
                self.ret()
            elif name == "adc-apply-profile":
                self.events.append([name, args[0],
                                    bytes(uc.mem_read(args[1], 7)).hex(),
                                    self.provider_returns.get(name, 0)])
                self.ret(self.provider_returns.get(name, 0))
            elif name == "adc-configure-channel":
                self.events.append([name, args[0], args[1],
                                    bytes(uc.mem_read(args[2], 12)).hex(),
                                    self.provider_returns.get(name, 0)])
                self.ret(self.provider_returns.get(name, 0))
            elif name in {"adc-profile-transfer", "adc-activate"}:
                value = self.provider_returns.get(name, 0)
                self.events.append([name, *args[:3 if name == "adc-profile-transfer" else 1], value])
                self.ret(value)
            elif name == "adc-enumerate":
                output_ready = args[3]
                output_samples = self.u(uc.reg_read(v.a.UC_ARM_REG_SP))
                assert 0x2002ef00 <= output_ready < 0x2002f100
                assert 0x2002ef00 <= output_samples < 0x2002f100
                sample = self.adc_samples[self.adc_sample_index]
                self.adc_sample_index += 1
                self.w(output_ready, 1)
                self.cpu.mem_write(output_samples,
                                   struct.pack("<2I", sample, 0))
                self.events.append([name, *args[:3], 1, sample])
                self.ret()
            elif name in {"adc-enable", "adc-command", "adc-disable",
                          "adc-normalize", "adc-reset"}:
                self.events.append([name, args[0]])
                self.ret()
            elif name == "generic-log":
                if args[0] == 0x4325F8:
                    sp = uc.reg_read(v.a.UC_ARM_REG_SP)
                    self.events.append([name, args[0], args[2], args[3],
                                        self.u(sp), self.u(sp + 4)])
                elif args[0] == 0x431AB8:
                    self.events.append([name, args[0], *args[1:4]])
                else:
                    self.events.append([name, args[0]])
                self.ret()
            elif name == "platform-context-enable":
                value = self.provider_returns.get(name, 0)
                self.events.append([name, args[0], value])
                self.ret(value)
            elif name == "platform-context-claim":
                self.events.append([name, *args[:2]])
                self.ret()
            elif name == "platform-config-transaction":
                self.events.append([name, *args[:3]])
                self.ret()
            elif name == "platform-instance-configure":
                self.events.append([name, *args[:2]])
                self.ret()
            elif name == "platform-config-retry":
                self.events.append([name, args[0]])
                self.ret()
            elif name == "platform-interrupt-enable":
                self.events.append([name, *args[:2]])
                self.ret()
            elif name == "platform-nvic-enable":
                self.events.append([name, args[0]])
                self.ret()
            elif name in {"post-context-register", "post-configure",
                          "post-validate", "post-activate", "post-finish"}:
                value = self.provider_returns.get(name, 0)
                arity = {"post-context-register": 2, "post-configure": 3,
                         "post-validate": 2, "post-activate": 5,
                         "post-finish": 2}[name]
                observed_args = args[:min(arity, 4)]
                if arity == 5:
                    observed_args.append(self.u(uc.reg_read(v.a.UC_ARM_REG_SP)))
                self.events.append([name, *observed_args, value])
                self.ret(value)
            elif name in {"post-register-mode", "post-enable",
                          "post-precommit", "post-record-initialized"}:
                arity = 2 if name == "post-register-mode" else 1
                self.events.append([name, *args[:arity]])
                self.ret(self.provider_returns.get(name, 0))
            else:
                self.events.append([name, *args])
                self.ret()
            return
        if self.source:
            assert any(lo <= pc < hi for lo, hi in self.exec_ranges), (
                "source execution escaped its ELF into unbound code", hex(pc))
        else:
            self.trace[hex(pc)] = bytes(uc.mem_read(pc, size)).hex()

    def run_entry(self, entry, args=(), r7=0x12345678):
        self.finished = False
        self.events = []
        self.mutex_index = 0
        self.adc_sample_index = 0
        regs = [v.a.UC_ARM_REG_R0, v.a.UC_ARM_REG_R1,
                v.a.UC_ARM_REG_R2, v.a.UC_ARM_REG_R3]
        for reg, value in zip(regs, list(args) + [0] * 4):
            self.cpu.reg_write(reg, value)
        self.cpu.reg_write(v.a.UC_ARM_REG_R7, r7)
        self.cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
        self.cpu.reg_write(v.a.UC_ARM_REG_LR, v.STOP | 1)
        self.cpu.emu_start(entry | 1, v.STOP + 2, count=500000)
        assert self.finished, ("execution budget", hex(entry),
                               hex(self.cpu.reg_read(v.a.UC_ARM_REG_PC)))
        return self.cpu.reg_read(v.a.UC_ARM_REG_R0)


def callback_result(entry, source_name, segments, symbols, mutex_returns=(),
                    service_guard_return=0, service_state=0,
                    service_f3=0, service_f4=0, provider_returns=None,
                    adc_samples=(0, 0, 3200)):
    original = CallbackMachine(mutex_returns=mutex_returns or
                               (0x2002A000, 0x2002A100),
                               service_guard_return=service_guard_return,
                               provider_returns=provider_returns,
                               adc_samples=adc_samples)
    source = CallbackMachine(True, segments, symbols,
        mutex_returns=mutex_returns or (0x2002A000, 0x2002A100),
        service_guard_return=service_guard_return,
        provider_returns=provider_returns,
        adc_samples=adc_samples)
    for machine in (original, source):
        machine.cpu.mem_write(0x20026700, b"\0" * 0x100)
        machine.cpu.mem_write(0x200267f0, bytes([service_state & 0xff]))
        machine.cpu.mem_write(0x200267f3, bytes([service_f3 & 0xff]))
        machine.cpu.mem_write(0x200267f4, bytes([service_f4 & 0xff]))
    original_result = original.run_entry(entry)
    source_result = source.run_entry(symbols[source_name])
    original_observation = {
        "return": original_result,
        "events": original.events,
        "redirect_globals": [original.u(0x2002712C), original.u(0x20027130)],
        "service_state": list(original.cpu.mem_read(0x200267f0, 5)),
        "platform_registers": bytes(original.cpu.mem_read(0x40010000, 0x520)).hex(),
        "primask": original.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),
        "platform_context_handles": [original.u(0x20026ed8 + 4 * i)
                                      for i in range(8)],
        "platform_semaphore": original.u(0x20027104),
        "adc_result": bytes(original.cpu.mem_read(0x20027018, 8)).hex(),
        "fpscr": original.cpu.reg_read(v.a.UC_ARM_REG_FPSCR),
    }
    source_observation = {
        "return": source_result,
        "events": source.events,
        "redirect_globals": [source.u(0x2002712C), source.u(0x20027130)],
        "service_state": list(source.cpu.mem_read(0x200267f0, 5)),
        "platform_registers": bytes(source.cpu.mem_read(0x40010000, 0x520)).hex(),
        "primask": source.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),
        "platform_context_handles": [source.u(0x20026ed8 + 4 * i)
                                      for i in range(8)],
        "platform_semaphore": source.u(0x20027104),
        "adc_result": bytes(source.cpu.mem_read(0x20027018, 8)).hex(),
        "fpscr": source.cpu.reg_read(v.a.UC_ARM_REG_FPSCR),
    }
    assert original_observation == source_observation, (
        hex(entry), original_observation, source_observation)
    return original_observation, original.trace


def platform_finish_result(segments, symbols, active_index=None,
                           existing_handle=0, mutex_returns=(0x2002A000,),
                           provider_returns=None, register_failure=False,
                           irq_transfer=0, irq_instance=0):
    original = CallbackMachine(mutex_returns=mutex_returns,
                               provider_returns=provider_returns)
    source = CallbackMachine(True, segments, symbols,
                             mutex_returns=mutex_returns,
                             provider_returns=provider_returns)
    row_index = 0 if active_index is None else active_index
    config_address = 0x20001000
    for machine in (original, source):
        machine.cpu.mem_write(0x20000374, b"\0" * 0x80)
        machine.cpu.mem_write(0x20026ed8, b"\0" * 32)
        machine.w(0x20027104, 0)
        # Stock's final IRQ call loads row 4 at table+0x44 (transfer, +4).
        # Keep the neighboring instance field deliberately distinct so a
        # source regression to +12 is observable even when the row is skipped
        # by the earlier configuration loop.
        irq_row = 0x20000374 + 4 * 16
        machine.w(irq_row + 4, irq_transfer)
        machine.w(irq_row + 12, irq_instance)
        if active_index is not None:
            row = 0x20000374 + row_index * 16
            machine.w(row, 0x20001010)
            machine.w(row + 4, 0x20001020)
            machine.w(row + 8, config_address)
            machine.w(row + 12, 0x20001030)
            machine.cpu.mem_write(config_address,
                                  struct.pack("<4I",
                                      0xe0 if register_failure else 0x31,
                                      0x32, 0x41, 0x42))
            machine.w(0x20026ed8 + row_index * 4, existing_handle)
    original_result = original.run_entry(0x430502)
    source_result = source.run_entry(symbols["opencfw_bl_platform_finish"])
    original_observation = {
        "return": original_result,
        "events": original.events,
        "context_handles": [original.u(0x20026ed8 + 4 * i) for i in range(8)],
        "semaphore": original.u(0x20027104),
    }
    source_observation = {
        "return": source_result,
        "events": source.events,
        "context_handles": [source.u(0x20026ed8 + 4 * i) for i in range(8)],
        "semaphore": source.u(0x20027104),
    }
    assert original_observation == source_observation, (
        active_index, existing_handle, provider_returns,
        original_observation, source_observation)
    return original_observation, original.trace


def post_bringup_result(segments, symbols, active_rows=(), provider_returns=None):
    original = CallbackMachine(provider_returns=provider_returns)
    source = CallbackMachine(True, segments, symbols,
                             provider_returns=provider_returns)
    table = 0x20000454
    table_size = 4 * 28
    for machine in (original, source):
        machine.cpu.mem_write(table, b"\0" * table_size)
        for index in active_rows:
            row = table + index * 28
            config = 0x20001000 + index * 0x40
            extended = config + 0x20
            kind = (0x7ff0 + index * 0x18) & 0xffffffff
            machine.w(row, kind)
            machine.w(row + 4, 0x20003000 + index * 0x100)
            machine.w(row + 8, config)
            machine.w(row + 12, 0x20003020 + index * 0x100)
            machine.w(row + 16, extended)
            machine.w(row + 20, 0x20003040 + index * 0x100)
            machine.cpu.mem_write(config, struct.pack(
                "<4I", 0x110 + index, 0x120 + index,
                0x210 + index, 0x220 + index))
            machine.cpu.mem_write(extended, struct.pack(
                "<2I", 0x310 + index, 0x320 + index))
    original_result = original.run_entry(0x41F612)
    source_result = source.run_entry(symbols["opencfw_bl_post_bringup_setup"])
    original_observation = {
        "return": original_result,
        "events": original.events,
        "table": bytes(original.cpu.mem_read(table, table_size)).hex(),
    }
    source_observation = {
        "return": source_result,
        "events": source.events,
        "table": bytes(source.cpu.mem_read(table, table_size)).hex(),
    }
    assert original_observation == source_observation, (
        active_rows, provider_returns, original_observation, source_observation)
    return original_observation, original.trace


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    names = {
        "opencfw_boot_init_callback_platform_sequence",
        "opencfw_boot_init_callback_services",
        "opencfw_boot_init_callback_redirect",
        "opencfw_bl_mode_register_update",
        "opencfw_bl_platform_finish",
        "opencfw_bl_post_bringup_setup",
    }
    assert names <= symbols.keys(), ("missing source callback", names - symbols.keys())

    cases = []
    trace = {}
    mode_cases = []
    for mode in range(8):
        for identifier in (0, 31, 32, 0x81, 0xff, 0x100):
            masks = (0, 1) if mode in (2, 5) else (0,)
            for mask in masks:
                original = CallbackMachine()
                source = CallbackMachine(True, segments, symbols)
                initial = bytes((index * 29 + 7) & 0xff for index in range(0x520))
                for machine in (original, source):
                    machine.cpu.mem_write(0x40010000, initial)
                    machine.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK, mask)
                old = original.run_entry(0x41D9AA,
                                         (identifier, mode, 0xdecafbad))
                new = source.run_entry(symbols["opencfw_bl_mode_register_update"],
                                       (identifier, mode, 0xdecafbad))
                old_state = bytes(original.cpu.mem_read(0x40010000, 0x520))
                new_state = bytes(source.cpu.mem_read(0x40010000, 0x520))
                old_mask = original.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK)
                new_mask = source.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK)
                assert (old, old_state, old_mask) == (new, new_state, new_mask), (
                    identifier, mode, mask, old, new, old_mask, new_mask)
                mode_cases.append({"identifier": identifier, "mode": mode,
                                   "initial_primask": mask, "return": old,
                                   "final_primask": old_mask,
                                   "register_window_sha256": hashlib.sha256(old_state).hexdigest()})
                trace.update(original.trace)
    direct = [
        (0x4301D6, "opencfw_boot_init_callback_platform_sequence", "platform-sequence"),
        (0x43194C, "opencfw_boot_init_callback_services", "services"),
    ]
    for entry, symbol, label in direct:
        result, seen = callback_result(entry, symbol, segments, symbols)
        cases.append({"name": label, "original_entry": hex(entry), "result": result})
        trace.update(seen)

    for label, samples, provider_returns in [
            ("adc-below-threshold", (0, 0, 3000), None),
            ("adc-between-thresholds", (0, 0, 3200), None),
            ("adc-above-threshold", (0, 0, 4000), None),
            ("adc-context-init-error-continues", (0, 0, 3200),
             {"adc-context-initialize": 1}),
            ("adc-transfer-error-continues", (0, 0, 3200),
             {"adc-profile-transfer": 1}),
            ("adc-profile-apply-error-continues", (0, 0, 3200),
             {"adc-apply-profile": 1}),
            ("adc-channel-config-error-continues", (0, 0, 3200),
             {"adc-configure-channel": 1}),
            ("adc-activation-error-continues", (0, 0, 3200),
             {"adc-activate": 1}),
    ]:
        result, seen = callback_result(
            0x4301D6, "opencfw_boot_init_callback_platform_sequence",
            segments, symbols, provider_returns=provider_returns,
            adc_samples=samples)
        cases.append({"name": label, "original_entry": "0x4301d6",
                      "adc_samples": samples,
                      "provider_returns": provider_returns, "result": result})
        trace.update(seen)

    for label, active_index, existing_handle, mutex_returns, provider_returns, register_failure in [
            ("platform-finish-empty-table", None, 0,
             (0x2002A000,), None, False),
            ("platform-finish-one-context", 2, 0,
             (0x2002A000,), None, False),
            ("platform-finish-existing-context-handle", 0, 0x2002A080,
             (0x2002A000,), None, False),
            ("platform-finish-create-fails", 0, 0,
             (0,), None, False),
            ("platform-finish-register-update-fails", 0, 0,
             (0x2002A000,), None, True),
            ("platform-finish-context-enable-status", 1, 0,
             (0x2002A000,), {"platform-context-enable": 7}, False),
            ("platform-finish-semaphore-fails", None, 0,
             (0x2002A000,), {"platform-semaphore-create": 0}, False),
    ]:
        result, seen = platform_finish_result(
            segments, symbols, active_index, existing_handle,
            mutex_returns, provider_returns, register_failure)
        cases.append({"name": label, "original_entry": "0x430502",
                      "active_index": active_index,
                      "existing_handle": existing_handle,
                      "provider_returns": provider_returns,
                      "result": result})
        trace.update(seen)

    for label, transfer, instance in [
            ("platform-finish-row4-transfer-distinct-from-instance",
             0x20001020, 0x20001030),
            ("platform-finish-row4-null-transfer-nonnull-instance",
             0, 0x20001030),
    ]:
        result, seen = platform_finish_result(
            segments, symbols, irq_transfer=transfer, irq_instance=instance)
        expected_irq = ["platform-interrupt-enable", transfer, 0xff]
        assert expected_irq in result["events"], (label, result["events"])
        cases.append({"name": label, "original_entry": "0x430502",
                      "row4_transfer": transfer,
                      "row4_instance": instance,
                      "result": result})
        trace.update(seen)

    for label, active_rows, provider_returns in [
            ("post-setup-empty-table", (), None),
            ("post-setup-row-zero", (0,), None),
            ("post-setup-rows-one-and-two", (1, 2), None),
            ("post-setup-row-three", (3,), None),
            ("post-setup-status-folding", (0, 2),
             {"post-context-register": 4, "post-finish": 2}),
    ]:
        result, seen = post_bringup_result(segments, symbols,
                                           active_rows, provider_returns)
        cases.append({"name": label, "original_entry": "0x41f612",
                      "active_rows": list(active_rows),
                      "provider_returns": provider_returns,
                      "result": result})
        trace.update(seen)

    for label, guard_return, initial_state in [
            ("service-init-normal", 0, 0),
            ("service-init-guard-failure", 3, 0),
            ("service-init-already-active", 0, 1),
    ]:
        result, seen = callback_result(0x43194C,
            "opencfw_boot_init_callback_services", segments, symbols,
            service_guard_return=guard_return, service_state=initial_state)
        cases.append({"name": label, "original_entry": "0x43194c",
                      "guard_return": guard_return,
                      "initial_active": initial_state, "result": result})
        trace.update(seen)

    for label, initial_f3, initial_f4 in [
            ("service-reset-wake-branch", 1, 0),
            ("service-reset-sleep-branch", 0, 1),
    ]:
        result, seen = callback_result(0x43194C,
            "opencfw_boot_init_callback_services", segments, symbols,
            service_f3=initial_f3, service_f4=initial_f4)
        cases.append({"name": label, "original_entry": "0x43194c",
                      "initial_f3": initial_f3, "initial_f4": initial_f4,
                      "result": result})
        trace.update(seen)

    for label, returned in [
            ("both-mutexes-created", (0x2002A000, 0x2002A100)),
            ("both-create-calls-fail", (0, 0)),
            ("second-mutex-fails", (0x2002A000, 0)),
            ("first-mutex-fails", (0, 0x2002A100)),
    ]:
        result, seen = callback_result(0x415590,
            "opencfw_boot_init_callback_redirect", segments, symbols, returned)
        cases.append({"name": label, "original_entry": "0x415590",
                      "mutex_returns": returned, "result": result})
        trace.update(seen)

    used = {int(pc, 0) + i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    source_files = [p for p in HERE.iterdir()
                    if p.is_file() and (p.suffix in {".c", ".h", ".S", ".ld", ".py"}
                                        or p.name == "Makefile")]
    source_files += [ROOT / "g2/components/bootloader/clock_manager/clock_class_providers.c",
                     ROOT / "g2/components/bootloader/clock_manager/clock_class_providers.h"]
    report = {
        "status": "PASS",
        "cases": len(cases),
        "original_sha256": v.SHA,
        "elf_sha256": v.sha(args.elf),
        "source_sha256": {str(p.relative_to(ROOT)): v.sha(p)
                          for p in source_files},
        "distinct_original_trace_bytes": len(used),
        "original_trace": trace,
        "comparisons": cases,
        "mode_register_cases": mode_cases,
        "limits": [
            "Stock callback entries 0x4301d6, 0x43194c and 0x415590 execute directly. Source implements their wrappers, 0x41d9aa, 0x41f612, 0x430000, 0x430502, and the exercised service helpers.",
            "0x430000 tests use a simulated ready field at 0x40038038 and three supplied ADC sample values; they cover below/between/above threshold outcomes and continuation after five API errors. No ADC timing or real peripheral behavior is established.",
            "Unicorn does not support the stock VCVT.F64.F32/VSTR D0/VMOV D0 instructions. Only those six fixed instruction slots in the emulator's original-image mapping are replaced by NOPs and their register/store effects emulated; original bytes are preserved in the trace. Other stock instructions execute normally.",
            "0x41d92c power-register updates execute source from clock_class_providers.c and stock instructions; peripheral registers are simulated. Named child providers remain at descriptor registration 0x430280; 0x430502 HAL dependencies 0x42c4c6, 0x42c988, 0x42cc34, 0x42c538, 0x43048e, 0x42c63a, 0x430470, and semaphore create 0x416762; ADC APIs 0x42e8d0, 0x42ec0c, 0x42f020, 0x42eb74, 0x42ea68, 0x42eaf6, 0x42ed60, 0x42ebaa, 0x42eff4, 0x42ee70, 0x42ebe2, 0x42eda0, and 0x42ea32; post-bringup APIs 0x41f530, 0x422ad4, 0x422ba8, 0x42308e, 0x422dc6, 0x41f512, 0x41f4f4, 0x4236ce, and 0x41f8ba; plus service guard/commit/wake/sleep, mutex creation, and logger.",
            "The fixed-table runner separately tests table entry and qsort; this profile does not invoke all table rows end-to-end. Its post-bringup four-row tables and platform-finish eight-row RAM table are explicit fixtures. Physical peripheral timing, logger formatting, scheduler delivery, full startup, and byte identity are outside this evidence.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": report["cases"],
                      "mode_register_cases": len(mode_cases),
                      "distinct_original_trace_bytes": len(used)}, indent=2))


if __name__ == "__main__":
    main()
