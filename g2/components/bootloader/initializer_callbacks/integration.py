"""Shared-image support for executing the reconstructed initializer table."""
from __future__ import annotations

import importlib.util
import struct
from unicorn import UC_HOOK_MEM_READ
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "initializer_callback_profile", HERE / "verify_initializer_callbacks.py")
_profile = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_profile)

TABLE_ADDRESS = 0x433440
TABLE_SIZE = 32
SCRATCH_ADDRESS = 0x20022E00
ADC_READY_ADDRESS = 0x40038038

# Table records are reconstructed data; source callback pointers are linker
# relocations to the source functions, not references to original code.
CALLBACKS = (
    ("opencfw_boot_init_callback_platform_sequence", 0x4301D6, 1),
    ("opencfw_boot_init_callback_services", 0x43194C, 1),
    ("opencfw_boot_init_callback_redirect", 0x415590, 25),
    ("opencfw_boot_allocator_init", 0x41FD70, 26),
)

# Native bodies whose original instructions and source counterparts are both
# expected to execute. No start-table callback is replaced by a return stub.
NATIVE_ENTRIES = {
    "opencfw_boot_init_table_default": 0x41F9F8,
    "opencfw_boot_init_sort": 0x423D08,
    "opencfw_boot_init_priority_compare": 0x423A48,
    "opencfw_boot_init_callback_platform_sequence": 0x4301D6,
    "opencfw_boot_init_callback_services": 0x43194C,
    "opencfw_boot_init_callback_redirect": 0x415590,
    "opencfw_boot_allocator_init": 0x41FD70,
    "opencfw_bl_mode_register_update": 0x41D9AA,
    "opencfw_bl_power_register_update": 0x41D92C,
    "opencfw_bl_platform_bringup": 0x430000,
    "opencfw_bl_post_bringup_setup": 0x41F612,
    "opencfw_bl_platform_finish": 0x430502,
}

ADC_SAMPLE_ENTRIES={"opencfw_bl_adc_activate":0x42ED60,"opencfw_bl_adc_enable":0x42EBAA,"opencfw_bl_adc_disable":0x42EBE2,"opencfw_bl_adc_command":0x42EFF4,"opencfw_bl_adc_normalize":0x42EDA0,"opencfw_bl_adc_enumerate":0x42EE70,"opencfw_boot_adc_correct_sample":0x42EE00}
NATIVE_ADC_ORIGINAL={"opencfw_bl_adc_context_initialize":0x42E8D0,"opencfw_bl_adc_reset":0x42EA32}

IOM_CHILD_ENTRIES = {
    "opencfw_boot_context_configure":0x42CC34,
    "opencfw_boot_context_enable":0x42C538,
    "opencfw_boot_context_retry":0x43048E,
    "opencfw_boot_iom_select_interface":0x42C034,
    "opencfw_boot_iom_clock_config":0x42C26A,
    "opencfw_boot_iom_frequency":0x42C222,
    "opencfw_boot_iom_onebit":0x42C256,
    "opencfw_boot_iom_cq_initialize":0x42C3E2,
    "opencfw_boot_iom_cq_enable":0x42C420,
    "opencfw_boot_iom_cq_disable":0x42C44E,
}

# External child dependencies, as instruction PCs. The service-enable and
# service-configure addresses are intentionally excluded from the cut adapter:
# those are native stock helpers on stock branches; source invalid-argument
# fallbacks remain a distinct unclosed edge.
CHILD_CUTS = {
    "descriptor-register": 0x430280,
    "adc-context-initialize": 0x42E8D0,
    "adc-configure": 0x42EC0C,
    "adc-profile-transfer": 0x42F020,
    "adc-context-configure": 0x42EB74,
    "adc-apply-profile": 0x42EA68,
    "adc-configure-channel": 0x42EAF6,
    "adc-activate": 0x42ED60,
    "adc-enable": 0x42EBAA,
    "adc-command": 0x42EFF4,
    "adc-enumerate": 0x42EE70,
    "adc-disable": 0x42EBE2,
    "adc-normalize": 0x42EDA0,
    "adc-reset": 0x42EA32,
    "generic-log": 0x415FAE,
    "post-register-mode": 0x41F530,
    "post-context-register": 0x422AD4,
    "post-configure": 0x422BA8,
    "post-validate": 0x42308E,
    "post-activate": 0x422DC6,
    "post-enable": 0x41F512,
    "post-precommit": 0x41F4F4,
    "post-finish": 0x4236CE,
    "post-record-initialized": 0x41F8BA,
    "platform-context-claim": 0x42C4C6,
    "platform-config-transaction": 0x42C988,
    "platform-instance-configure": 0x42CC34,
    "platform-context-enable": 0x42C538,
    "platform-config-retry": 0x43048E,
    "platform-interrupt-enable": 0x42C63A,
    "platform-nvic-enable": 0x430470,
    "platform-semaphore-create": 0x416762,
    "service-guard": 0x41A684,
    "service-commit": 0x4175B4,
    "service-wake": 0x41A69A,
    "service-sleep": 0x41A6A2,
    "invalid-pin-configure": 0x4174A6,
    "mutex-create": 0x416610,
    "logger-output": 0x4176CE,
}

# Small authenticated read-only scalar/config data used by callback bodies.
# No executable bytes are copied into the source machine.
READONLY_FIXTURES = ((0x43419C, 4), (0x434170, 4), (0x434174, 4),
                     (0x431AB8, 4), (0x43402C, 8))
SOURCE_CONFIG_COMPARISONS = ((0x433D58, 16), (0x433D68, 16),
                             (0x433D78, 16), (0x433D88, 16),
                             (0x433D98, 16), (0x433DA8, 16),
                             (0x433DB8, 16))

def seed_readonly_fixtures(machine, blob: bytes, image_base: int) -> None:
    for address, size in READONLY_FIXTURES:
        start = address - image_base
        if start < 0 or start + size > len(blob):
            raise ValueError(f"fixture outside pinned input: {address:#x}")
        machine.cpu.mem_write(address, blob[start:start + size])


def verify_source_config_data(machine, blob: bytes, image_base: int) -> None:
    """Compare source-owned post-config data; never seed/overwrite these bytes."""
    for address, size in SOURCE_CONFIG_COMPARISONS:
        start = address - image_base
        if start < 0 or start + size > len(blob):
            raise ValueError(f"comparison data outside pinned input: {address:#x}")
        expected = blob[start:start + size]
        actual = bytes(machine.cpu.mem_read(address, size))
        assert actual == expected, ("source readonly config differs from pinned data",
                                    hex(address), actual.hex(), expected.hex())


SERVICE_ENTRIES = {'opencfw_provider_416610': 0x416610, 'opencfw_bl_service_guard': 4302468, 'opencfw_bl_service_commit': 4289972, 'opencfw_bl_service_wake': 4302490, 'opencfw_bl_service_sleep': 4302498, 'opencfw_boot_service_mutex_initialize': 4302408, 'opencfw_boot_service_mutex_acquire': 4302428, 'opencfw_boot_service_mutex_release': 4302450}

UART_ENTRIES = {'opencfw_bl_post_context_register': 4336340, 'opencfw_bl_post_configure': 4336552, 'opencfw_bl_post_validate': 4337806, 'opencfw_bl_post_activate': 4337094, 'opencfw_bl_post_enable': 4322578, 'opencfw_bl_post_precommit': 4322548, 'opencfw_bl_post_finish': 4339406, 'opencfw_bl_post_record_initialized': 4323514, 'opencfw_bl_register_mode': 4322608, 'opencfw_boot_uart_interrupt_clear': 4339456, 'opencfw_boot_uart_ring_initialize': 4355562, 'opencfw_boot_uart_baud': 4337192}

def configure(machine, source: bool, native_irq: bool = False,
              native_context: bool = False,
              native_children: bool = False, native_nvic: bool = False, native_semaphore: bool = False, native_gpio: bool = False, native_adc: bool = False, native_adc_control: bool = False, native_adc_configuration: bool = False, native_adc_samples: bool = False, native_adc_profile: bool = False, native_uart: bool = False, native_service: bool = False) -> dict[str, object]:
    """Install entry maps/fixtures on the shared machine, without stubbing callbacks."""
    assert bool(machine.source) == bool(source)
    entries: dict[str, int] = {}
    for name, stock_pc in NATIVE_ENTRIES.items():
        if source:
            if name not in machine.symbols:
                continue
            pc = machine.symbols[name] & ~1
            assert any(lo <= pc < hi for lo, hi in machine.exec_ranges), (
                "native source entry outside ELF", name, hex(pc))
        else:
            pc = stock_pc
        entries[name] = pc
        machine.actual_read.add(pc)

    # Close this child only when the shared source ELF supplies its native body.
    if native_irq:
        irq_pc = (machine.symbols["opencfw_boot_context_interrupt_enable"] & ~1
                  if source else 0x42C63A)
        entries["opencfw_boot_context_interrupt_enable"] = irq_pc
        machine.actual_read.add(irq_pc)
    if native_context:
        for name, original in (("opencfw_boot_context_claim",0x42C4C6),
                               ("opencfw_boot_context_transaction",0x42C988)):
            pc = machine.symbols[name]&~1 if source else original
            entries[name] = pc
            machine.actual_read.add(pc)
    if native_children:
        for name,original in IOM_CHILD_ENTRIES.items():
            pc=machine.symbols[name]&~1 if source else original
            entries[name]=pc
            machine.actual_read.add(pc)
    if native_nvic:
        name="opencfw_boot_context_nvic_enable"
        entries[name]=(machine.symbols[name]&~1) if source else 0x430470
        machine.actual_read.add(entries[name])
    if native_semaphore:
        name="opencfw_boot_semaphore_create"
        entries[name]=(machine.symbols[name]&~1) if source else 0x416762
        machine.actual_read.add(entries[name])
    if native_gpio:
        gpio_entries={"opencfw_bl_descriptor_register":0x430280,"opencfw_boot_gpio_mask_status":0x41DCCA,"opencfw_boot_gpio_mask_clear":0x41DE3C,"opencfw_boot_gpio_callback_register":0x41E000,"opencfw_boot_gpio_interrupt_control":0x41DA84,"opencfw_boot_gpio_priority":0x43025C}
        for name,original in gpio_entries.items():
            entries[name]=machine.symbols[name]&~1 if source else original
            machine.actual_read.add(entries[name])
        if not source:machine.actual_read.update({0x41D8F8,0x430240})
    if native_adc:
        adc_entries={"opencfw_bl_adc_context_initialize":0x42E8D0,"opencfw_bl_adc_reset":0x42EA32,"opencfw_boot_device_mode_wait":0x421548,"opencfw_boot_info_read_dispatch":0x4213E6,"opencfw_boot_info_rom_read":0x41D28A}
        for name,original in adc_entries.items():
            entries[name]=machine.symbols[name]&~1 if source else original
            machine.actual_read.add(entries[name])
    if native_adc_control:
        name="opencfw_bl_adc_configure"
        entries[name]=machine.symbols[name]&~1 if source else 0x42EC0C
        machine.actual_read.add(entries[name])
    if native_adc_configuration:
        for name,original in {"opencfw_bl_adc_context_configure":0x42EB74,"opencfw_bl_adc_configure_channel":0x42EAF6}.items():
            entries[name]=machine.symbols[name]&~1 if source else original
            machine.actual_read.add(entries[name])
    if native_adc_samples:
        for name,original in ADC_SAMPLE_ENTRIES.items():
            entries[name]=machine.symbols[name]&~1 if source else original
            machine.actual_read.add(entries[name])
    if native_adc_profile:
        for name,original in {"opencfw_bl_adc_profile_transfer":0x42F020,"opencfw_bl_adc_apply_profile":0x42EA68}.items():
            entries[name]=machine.symbols[name]&~1 if source else original
            machine.actual_read.add(entries[name])
    if native_uart:
        for name,original in UART_ENTRIES.items():
            entries[name]=machine.symbols[name]&~1 if source else original
            machine.actual_read.add(entries[name])
    if native_service:
        for name,original in SERVICE_ENTRIES.items():
            entries[name]=machine.symbols[name]&~1 if source else original
            machine.actual_read.add(entries[name])
    machine.initializer_native_service=native_service
    machine.initializer_native_uart=native_uart
    machine.initializer_native_adc_profile=native_adc_profile
    machine.initializer_native_adc_samples=native_adc_samples
    machine.initializer_native_adc_configuration=native_adc_configuration
    machine.initializer_native_adc_control=native_adc_control
    machine.initializer_native_adc=native_adc
    machine.initializer_native_gpio=native_gpio
    machine.initializer_native_semaphore=native_semaphore
    machine.initializer_native_nvic=native_nvic
    machine.initializer_native_children = native_children
    machine.initializer_native_context = native_context
    machine.initializer_native_irq = native_irq
    machine.initializer_native_entries = entries
    machine.initializer_child_cuts = dict(CHILD_CUTS)
    if native_service:
        for label in ("service-guard","service-commit","service-wake","service-sleep","mutex-create"):machine.initializer_child_cuts.pop(label)
    if native_uart:
        for label in ("post-context-register","post-configure","post-validate","post-activate","post-enable","post-precommit","post-finish","post-record-initialized","post-register-mode"):
            machine.initializer_child_cuts.pop(label)
    if native_adc_profile:
        for label in ("adc-profile-transfer","adc-apply-profile"):machine.initializer_child_cuts.pop(label)
    if native_adc_samples:
        for label in ("adc-activate","adc-enable","adc-disable","adc-command","adc-normalize","adc-enumerate"):machine.initializer_child_cuts.pop(label)
    if native_adc_configuration:
        machine.initializer_child_cuts.pop("adc-context-configure")
        machine.initializer_child_cuts.pop("adc-configure-channel")
    if native_adc_control:
        machine.initializer_child_cuts.pop("adc-configure")
    if native_adc:
        machine.initializer_child_cuts.pop("adc-context-initialize")
        machine.initializer_child_cuts.pop("adc-reset")
    if native_gpio:
        machine.initializer_child_cuts.pop("descriptor-register")
    if native_semaphore:
        machine.initializer_child_cuts.pop("platform-semaphore-create")
    if native_nvic:
        machine.initializer_child_cuts.pop("platform-nvic-enable")
    if native_irq:
        machine.initializer_child_cuts.pop("platform-interrupt-enable")
    if native_context:
        machine.initializer_child_cuts.pop("platform-context-claim")
        machine.initializer_child_cuts.pop("platform-config-transaction")
        machine.initializer_child_cuts.update({"iom-cq-enable":0x42C420,
                                             "iom-cq-disable":0x42C44E})
    if native_children:
        for label in ("platform-instance-configure","platform-context-enable",
                      "platform-config-retry","iom-cq-enable","iom-cq-disable"):
            machine.initializer_child_cuts.pop(label,None)
    machine.initializer_table_address = TABLE_ADDRESS
    machine.initializer_scratch_address = SCRATCH_ADDRESS
    machine.initializer_events = []
    # Reuse exactly the separately tested provider semantics; not callback
    # entry returns. The shared verifier calls handle_code before own cuts.
    # Up to eight platform rows can create mutexes before redirect creates its
    # own two; deterministic addresses preserve stock/source lock call order.
    machine.mutex_returns = [0x2002A000 + 0x100 * i for i in range(16)]
    machine.mutex_index = 0
    machine.service_guard_return = 0
    machine.provider_returns = {"platform-semaphore-create": 0x2002B000}
    machine.adc_samples = [0, 0, 3200]
    machine.adc_sample_index = 0
    if native_adc_samples:
        def fifo_read(uc,access,address,size,value,user):
            assert address==0x4003803c and size==4
            index=machine.adc_sample_index
            assert index<len(machine.adc_samples),"unexpected ADC FIFO read beyond explicit fixture"
            word=(machine.adc_samples[index]<<6)|(1<<20)
            uc.mem_write(address,struct.pack("<I",word))
            machine.adc_sample_index+=1
            machine.initializer_events.append(["adc-fifo-word-fixture",index,word])
        machine.cpu.hook_add(UC_HOOK_MEM_READ,fifo_read,begin=0x4003803c,end=0x4003803f)
    machine.fp_d0 = 0
    machine.initializer_native_visits = {name: 0 for name in entries}
    machine.initializer_child_visits = {hex(pc): 0 for pc in CHILD_CUTS.values()}
    machine.initializer_fp_effect_visits = {hex(pc): 0 for pc in _FP_SLOTS}
    if not hasattr(machine, "trace"):
        machine.trace = {}

    # Ensure minimal MMIO ranges exist without replacing larger machine maps.
    for base in (0x40010000, 0x40038000, 0xE000E000):
        if not any(lo <= base <= hi for lo, hi, *_ in machine.cpu.mem_regions()):
            machine.cpu.mem_map(base, 0x1000)
    machine.cpu.mem_write(ADC_READY_ADDRESS, struct.pack("<I", 1 << 20))
    machine.cpu.reg_write(_profile.v.a.UC_ARM_REG_FPEXC, 0x40000000)
    machine.cpu.mem_write(0xE000ED88, struct.pack("<I", 0x00F00000))

    if native_children:
        # Explicit synthetic interface topology and idle acknowledgement.
        # This is neither a silicon reset-value assertion nor queue progress.
        for module in range(8):
            base=0x40050000+module*0x1000
            if not any(lo<=base and base+0xfff<=hi for lo,hi,_ in machine.cpu.mem_regions()):
                machine.cpu.mem_map(base,0x1000)
            machine.cpu.mem_write(0x4005011C+module*0x1000,struct.pack("<I",0x20))
            machine.cpu.mem_write(0x40050248+module*0x1000,struct.pack("<I",4))
    if native_uart:
        for base in (0x40039000,0x4003a000,0x4003b000,0x4003c000):
            if not any(lo<=base and base+0xfff<=hi for lo,hi,_ in machine.cpu.mem_regions()):machine.cpu.mem_map(base,0x1000)
    if source:
        blob = _profile.v.BLOB.read_bytes()
        seed_readonly_fixtures(machine, blob, _profile.v.BASE)
        verify_source_config_data(machine, blob, _profile.v.BASE)
        assert machine.symbols.get("opencfw_boot_context_config_records") == 0x433D58
        assert machine.symbols.get("opencfw_boot_initializer_callback_records") == TABLE_ADDRESS
        expected = []
        for name, _, priority in CALLBACKS:
            assert name in machine.symbols, f"missing source callback {name}"
            expected.extend((machine.symbols[name] & 0xFFFFFFFF, priority))
        table = struct.unpack("<8I", machine.cpu.mem_read(TABLE_ADDRESS,
                                                            TABLE_SIZE))
        assert table == tuple(expected), ("relocated table mismatch", table,
                                          tuple(expected))
    else:
        table = struct.unpack("<8I", machine.cpu.mem_read(TABLE_ADDRESS,
                                                            TABLE_SIZE))
        assert table[1::2] == tuple(row[2] for row in CALLBACKS)
        install_stock_fp_instruction_shims(machine)

    return {
        "native_entries": entries,
        "child_cuts": dict(machine.initializer_child_cuts),
        "callback_records": list(CALLBACKS),
        "callback_table_words": list(table),
        "readonly_fixtures": [
            {"address": hex(address), "size": size,
             "sha256": __import__("hashlib").sha256(
                 _profile.v.BLOB.read_bytes()[address - _profile.v.BASE:
                                               address - _profile.v.BASE + size]
             ).hexdigest(),
             "provenance": "locked image readonly scalar fixture"}
            for address, size in READONLY_FIXTURES] if source else [],
        "source_config_data_comparisons": [
            {"address": hex(address), "size": size,
             "sha256": __import__("hashlib").sha256(
                 _profile.v.BLOB.read_bytes()[address - _profile.v.BASE:
                                               address - _profile.v.BASE + size]
             ).hexdigest(),
             "provenance": "source ELF readonly configuration compared to pinned bytes"}
            for address, size in SOURCE_CONFIG_COMPARISONS] if source else [],
        "synthetic_adc_ready": [hex(ADC_READY_ADDRESS), hex(1 << 20)],
        "callback_success_stubs": False,
        "conditional_invalid_argument_children": {
            "service-enable": "0x417438",
            "service-configure": "0x417510",
        },
        "unsupported_stock_fp_slots": [hex(x) for x in sorted(_FP_SLOTS)],
    }


_FP_SLOTS = {0x430048, 0x43004C, 0x430054, 0x430058, 0x43019E, 0x4301A2}
_CUT_HOOKS = {pc & ~1 for pc in _profile.CUTS
              if (pc & ~1) not in {0x417438, 0x417510}}


def install_stock_fp_instruction_shims(machine) -> None:
    """Patch only Unicorn-unsupported FP64 instructions in the stock mapping."""
    for address in sorted(_FP_SLOTS):
        machine.cpu.mem_write(address, b"\x00\xbf\x00\xbf")


def handle_code(machine, uc, pc: int, size: int, user) -> bool:
    """Handle the existing narrow leaf cuts and FP instruction effects only."""
    for name, entry in machine.initializer_native_entries.items():
        if pc == entry:
            machine.initializer_native_visits[name] += 1
    if not machine.source and pc in _FP_SLOTS:
        machine.initializer_fp_effect_visits[hex(pc)] += 1
        _delegate_leaf(machine, uc, pc, size, user)
        return True
    if machine.initializer_native_children:
        for name,original,label,arity in (
            ("opencfw_boot_context_configure",0x42CC34,"platform-instance-configure",2),
            ("opencfw_boot_context_enable",0x42C538,"platform-context-enable-native",1),
            ("opencfw_boot_context_retry",0x43048E,"platform-config-retry",1)):
            entry=machine.initializer_native_entries[name]
            if pc==entry:machine.initializer_events.append([label,*machine.args()[:arity]])
            if pc==entry or pc==original:return False
        if pc in machine.initializer_native_entries.values() and pc in {machine.initializer_native_entries[n] for n in IOM_CHILD_ENTRIES}:
            return False
    if machine.initializer_native_context:
        for name,original,label,arity in (
            ("opencfw_boot_context_claim",0x42C4C6,"platform-context-claim",2),
            ("opencfw_boot_context_transaction",0x42C988,"platform-config-transaction",3)):
            entry=machine.initializer_native_entries[name]
            if pc==entry:
                machine.initializer_events.append([label,*machine.args()[:arity]])
            if pc==original or pc==entry:
                return False
        if not machine.initializer_native_children and pc in (0x42C420,0x42C44E):
            machine.initializer_events.append(["iom-cq-enable" if pc==0x42C420 else "iom-cq-disable",machine.args()[0]])
            machine.ret();return True
    if machine.initializer_native_irq:
        irq_pc = machine.initializer_native_entries["opencfw_boot_context_interrupt_enable"]
        if pc == irq_pc:
            machine.initializer_events.append(
                ["platform-interrupt-enable", *machine.args()[:2]])
        if pc == 0x42C63A or pc == irq_pc:
            return False  # execute the locked/source instructions; no success return
    if machine.initializer_native_semaphore:
        entry=machine.initializer_native_entries["opencfw_boot_semaphore_create"]
        if pc==entry:machine.initializer_events.append(["platform-semaphore-create-native",*machine.args()[:3]])
        if pc==entry or pc==0x416762:return False
    if machine.initializer_native_nvic:
        entry=machine.initializer_native_entries["opencfw_boot_context_nvic_enable"]
        if pc==entry:machine.initializer_events.append(["platform-nvic-enable",machine.args()[0]])
        if pc==entry or pc==0x430470:return False
    if machine.initializer_native_adc:
        for name,label,arity in (("opencfw_bl_adc_context_initialize","adc-context-initialize-native",1),("opencfw_bl_adc_reset","adc-reset-native",1)):
            entry=machine.initializer_native_entries[name]
            if pc==entry:machine.initializer_events.append([label,*machine.args()[:arity]])
            if pc==entry or pc==NATIVE_ADC_ORIGINAL[name]:return False
    if machine.initializer_native_adc_profile:
        for name,original in {"opencfw_bl_adc_profile_transfer":0x42F020,"opencfw_bl_adc_apply_profile":0x42EA68}.items():
            entry=machine.initializer_native_entries[name]
            if pc==entry:
                args=machine.args()
                event=[name+"-native",args[0]]
                if name=="opencfw_bl_adc_profile_transfer":event.extend(args[1:3])
                else:event.append(bytes(uc.mem_read(args[1],7)).hex() if args[1] else None)
                machine.initializer_events.append(event)
            if pc==entry or pc==original:return False
    if machine.initializer_native_adc_samples:
        for name,original in ADC_SAMPLE_ENTRIES.items():
            entry=machine.initializer_native_entries[name]
            if pc==entry and name!="opencfw_boot_adc_correct_sample":
                args=machine.args()
                event=[name+"-native",args[0]]
                if name=="opencfw_bl_adc_enumerate":event.extend([args[1],bool(args[2]),machine.u(args[3])])
                machine.initializer_events.append(event)
            if pc==entry or pc==original:return False
    if machine.initializer_native_adc_configuration:
        for name,original,label,channel in (("opencfw_bl_adc_context_configure",0x42EB74,"adc-context-configure-native",False),("opencfw_bl_adc_configure_channel",0x42EAF6,"adc-configure-channel-native",True)):
            entry=machine.initializer_native_entries[name]
            if pc==entry:
                ctx,arg,ptr=machine.args()[:3]
                pointer=ptr if channel else arg
                machine.initializer_events.append([label,ctx,arg if channel else None,bytes(uc.mem_read(pointer,12 if channel else 8)).hex() if pointer else None])
            if pc==entry or pc==original:return False
    if machine.initializer_native_adc_control:
        entry=machine.initializer_native_entries["opencfw_bl_adc_configure"]
        if pc==entry:
            ctx,request,ptr=machine.args()[:3]
            machine.initializer_events.append(["adc-configure-native",ctx,request,bytes(uc.mem_read(ptr,16)).hex() if ptr else None])
        if pc==entry or pc==0x42EC0C:return False
    if machine.initializer_native_gpio:
        entry=machine.initializer_native_entries["opencfw_bl_descriptor_register"]
        if pc==entry:machine.initializer_events.append(["descriptor-register",*machine.args()[:2]])
        if pc==entry or pc==0x430280:return False
    if machine.initializer_native_uart:
        for name,original in UART_ENTRIES.items():
            entry=machine.initializer_native_entries[name]
            if pc==entry:
                args=machine.args()
                arity={"opencfw_bl_post_context_register":2,"opencfw_bl_post_configure":3,"opencfw_bl_post_validate":2,"opencfw_bl_post_activate":4,"opencfw_bl_post_enable":1,"opencfw_bl_post_precommit":1,"opencfw_bl_post_finish":2,"opencfw_bl_post_record_initialized":1,"opencfw_bl_register_mode":2,"opencfw_boot_uart_interrupt_clear":2,"opencfw_boot_uart_ring_initialize":4,"opencfw_boot_uart_baud":3}[name]
                event=[name+"-native",*args[:arity]]
                if name=="opencfw_bl_post_activate":event.append(machine.u(uc.reg_read(_profile.v.a.UC_ARM_REG_SP)))
                machine.initializer_events.append(event)
            if pc==entry or pc==original:return False
    if machine.initializer_native_service:
        for name,original in SERVICE_ENTRIES.items():
            entry=machine.initializer_native_entries[name]
            if pc==entry:
                event=[name+"-native"]
                if name=="opencfw_provider_416610":
                    pointer=machine.args()[0];event.extend([pointer,bytes(uc.mem_read(pointer,16)).hex() if pointer else None])
                machine.initializer_events.append(event)
            if pc==entry or pc==original:return False
    if pc in _CUT_HOOKS or (machine.source and pc == 0x4174A6):
        machine.initializer_child_visits[hex(pc)] = (
            machine.initializer_child_visits.get(hex(pc), 0) + 1)
        if pc == 0x42EE70:
            _adc_enumerate(machine, uc)
        else:
            _delegate_leaf(machine, uc, pc, size, user)
        return True
    return False


def normalize_initializer_event(event: list[object]) -> list[object]:
    """Drop only values proven to be outside the child's observed ABI.

    The descriptor registrar at 0x430280 copies r0/r1 at entry and uses those
    saved values; r2/r3 are caller-saved residue. The service guard is a
    zero-argument helper; only its return value is part of that call contract.
    Every other event, especially the two context-interrupt arguments, is kept
    byte-for-byte because those values affect downstream behavior.
    """
    if not event:
        raise ValueError("empty initializer event")
    name = event[0]
    if name == "descriptor-register":
        if len(event) < 3:
            raise ValueError(("descriptor-register event lacks r0/r1", event))
        return [name, event[1], event[2]]
    if name == "service-guard":
        if len(event) < 2:
            raise ValueError(("service-guard event lacks result", event))
        return [name, event[-1]]
    return list(event)


def normalize_initializer_events(events: list[list[object]]) -> list[list[object]]:
    """Normalize initializer events by the proven leaf-call contracts."""
    return [normalize_initializer_event(event) for event in events]


def split_initializer_native_visits(
        visits: dict[str, int]) -> tuple[dict[str, int], dict[str, int]]:
    """Separate comparator count from semantic native-entry visit equality.

    Sorting and normalized callback-table equality are checked independently;
    stock and source sorting algorithms may make different numbers of
    comparator calls. The returned second mapping is diagnostic only and
    should be checked for nonzero visitation on both machines, not equality.
    """
    diagnostic = {}
    comparable = dict(visits)
    for name in ("opencfw_boot_init_priority_compare",):
        if name in comparable:
            diagnostic[name] = comparable.pop(name)
    return comparable, diagnostic


def _delegate_leaf(machine, uc, pc: int, size: int, user) -> None:
    """Call the independently-tested cut semantics without clobbering events."""
    prior_events = getattr(machine, "events", None)
    machine.events = machine.initializer_events
    try:
        _profile.CallbackMachine.code(machine, uc, pc, size, user)
    finally:
        if prior_events is None:
            del machine.events
        else:
            machine.events = prior_events


def _adc_enumerate(machine, uc) -> None:
    """Fixture ADC sample write with stack pointers validated as mapped SRAM."""
    args = machine.args()
    output_ready = args[3]
    output_samples = machine.u(uc.reg_read(_profile.v.a.UC_ARM_REG_SP))
    regions = [(lo, hi) for lo, hi, *_ in uc.mem_regions()]
    for pointer, width in ((output_ready, 4), (output_samples, 8)):
        assert 0x20000000 <= pointer and pointer + width <= 0x20100000
        assert any(lo <= pointer and pointer + width - 1 <= hi
                   for lo, hi in regions), ("ADC output is not mapped SRAM",
                                             hex(pointer), width)
    index = machine.adc_sample_index
    sample = machine.adc_samples[index]
    machine.adc_sample_index += 1
    machine.w(output_ready, 1)
    uc.mem_write(output_samples, struct.pack("<2I", sample, 0))
    machine.initializer_events.append(
        ["adc-enumerate", *args[:3], 1, sample])
    machine.ret()
