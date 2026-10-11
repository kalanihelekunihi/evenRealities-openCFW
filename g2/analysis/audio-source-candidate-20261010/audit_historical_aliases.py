#!/usr/bin/env python3
"""Group the 64 historical linker aliases without treating names as proof."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
A = Path(__file__).resolve().parent
ARCHIVE = Path("/tmp/g2-audio-arm-inventory/libaudio-source-candidates.a")
aliases = json.loads((A / "local-source-alias-candidates.json").read_text())
bindings = json.loads((A / "import-address-map.json").read_text())
compile_rows = json.loads((A / "arm-compile-results.json").read_text())["rows"]
objects = {Path(row["object_path"]).name: row for row in compile_rows}
owners = {}
member = None
for line in subprocess.check_output(["arm-none-eabi-nm", "-g", "-P", str(ARCHIVE)], text=True).splitlines():
    if line.endswith(":"):
        member = line.split("[")[-1].rstrip("]: ")
        continue
    fields = line.split()
    if len(fields) >= 2 and fields[1].upper() in ("T", "D", "B", "R", "W", "V", "A"):
        owners[fields[0]] = member

selected = {
    "audio_resume_enter": ("stock_enter_critical", "0x4420d0"),
    "audio_timer_wait_enter": ("stock_enter_critical", "0x4420d0"),
    "audio_resume_exit": ("stock_exit_critical", "0x4420e8"),
    "audio_timer_wait_exit": ("stock_exit_critical", "0x4420e8"),
    "audio_resume_next_unblock": ("audio_queue_next_unblock", "0x455876"),
    "audio_block_remove": ("uxListRemove", "0x4560e8"),
    "audio_block_sorted_insert": ("audio_public_list_insert", "0x4560b2"),
    "callback_save_disable_irq": ("uart_save_irq", "0x473940"),
    "stock_pll_power_enabled": ("audio_pll_power_enabled", "0x4800e4"),
    "stock_hfrc_target": ("audio_hfrc_target", "0x4d3914"),
    "stock_hfrc2_ratio": ("audio_hfrc2_ratio", "0x4d38ea"),
    "stock_pll_generate": ("audio_pll_postdiv", "0x539794"),
    "stock_floorf": ("audio_floorf", "0x43a5a0"),
    "stock_roundf": ("audio_roundf", "0x577d08"),
    "stock_ceilf": ("audio_ceilf", "0x577d40"),
    "stock_fmodf": ("audio_fmodf", "0x577c3c"),
    "codec_hal_power": ("am_hal_uart_power_control", "0x58dbb8"),
    "codec_hal_configure": ("am_hal_uart_configure", "0x58e09e"),
    "stock_hfrc_force": ("audio_hfrc_force", "0x4d391e"),
    "stock_hfrc_disable": ("audio_hfrc_disable", "0x4d3944"),
    "audio_timer_wait_unlock": ("audio_public_queue_unlock", "0x441f88"),
    "stock_priority_disinherit": ("xTaskPriorityDisinherit", "0x45596e"),
    "stock_scheduler_resume": ("audio_resume_pending_ticks_selected", "0x454dcc"),
    "offline_notify": ("uart_notify_isr", "0x455dc0"),
    "stock_mcu_memory_config": ("audio_mcu_memory_config", "0x47f204"),
    "stock_sram_config": ("audio_sram_config", "0x47f46a"),
    "stock_pin_get": ("audio_gpio_pin_get", "0x480eee"),
    "stock_pin_set": ("audio_gpio_pin_set", "0x480f0c"),
    "stock_info_populate": ("audio_info1_populate", "0x47f954"),
    "stock_mcuctrl": ("audio_oscillator_control", "0x4809c4"),
    "stock_hfrc2_force": ("audio_hfrc2_force", "0x4d3952"),
    "stock_pll_power_enable": ("audio_pll_power_enable", "0x480058"),
    "stock_pll_power_disable": ("audio_pll_power_disable", "0x48009e"),
    "stock_pll_init": ("audio_pll_init", "0x5398e0"),
    "stock_pll_deinit": ("audio_pll_deinit", "0x539944"),
    "stock_pll_enable": ("audio_pll_enable", "0x539994"),
    "stock_pll_disable": ("audio_pll_disable", "0x539a10"),
    "stock_pll_config": ("audio_pll_configure", "0x539a40"),
    "stock_pll_wait": ("audio_pll_wait", "0x539b56"),
    "stock_ton_update": ("pcm_ton_dispatch", "0x4803c2"),
    "early_other": ("pcm_early_on", "0x59fbac"),
    "early_zero": ("pcm_early_off", "0x59fca2"),
    "middle_action0": ("pcm_sleep", "0x5a0204"),
    "middle_action2": ("pcm_temperature", "0x5a00fc"),
    "middle_other": ("pcm_middle_on", "0x5a0328"),
    "middle_zero": ("pcm_middle_off", "0x5a05e0"),
    "callback_plan": ("audio_platform_plan", "0x5a45d0"),
    "callback_change_state": ("audio_platform_change_state", "0x5a421c"),
    "callback_prepare_state": ("audio_platform_prepare_state", "0x5a410c"),
    "callback_apply": ("audio_platform_step", "0x5a44ba"),
    "stock_temperature_apply": ("pcm_hardware_temperature", "0x5a001c"),
    "stock_prepare": ("pcm21_prepare", "0x5a0c20"),
    "stock_change_state": ("pcm21_change_state", "0x5a0d44"),
    "stock_plan": ("pcm21_plan", "0x5a13e8"),
    "stock_apply": ("pcm21_apply", "0x5a0fc4"),
    "stock_timer_publish": ("pcm21_timer_publish", "0x5a0ae8"),
    "stock_timer_clear": ("pcm21_boost_remove", "0x5a0b54"),
    "stock_completion": ("pcm21_buck_complete", "0x5a0b9c"),
    "stock_ton": ("pcm21_ton", "0x5a0d9c"),
}
selected_receipts = {
    "audio_resume_enter": ("0x4420d1", "g2/analysis/audio-resume-ticks-closure-2026-10-08/reproduction-receipt.json"),
    "audio_resume_exit": ("0x4420e9", "g2/analysis/audio-resume-ticks-closure-2026-10-08/reproduction-receipt.json"),
    "audio_timer_wait_enter": ("0x4420d1", "g2/analysis/audio-timer-queue-wait-closure-2026-10-08/reproduction-receipt.json"),
    "audio_timer_wait_exit": ("0x4420e9", "g2/analysis/audio-timer-queue-wait-closure-2026-10-08/reproduction-receipt.json"),
    "audio_resume_next_unblock": ("0x455877", "g2/analysis/audio-resume-ticks-closure-2026-10-08/reproduction-receipt.json"),
    "audio_block_remove": ("0x4560e9", "g2/analysis/audio-delayed-block-closure-2026-10-08/reproduction-receipt.json"),
    "audio_block_sorted_insert": ("0x4560b3", "g2/analysis/audio-delayed-block-closure-2026-10-08/reproduction-receipt.json"),
    "callback_save_disable_irq": ("0x473941", "g2/analysis/audio-platform-callbacks-closure-2026-10-08/reproduction-receipt.json"),
    "stock_pll_power_enabled": ("0x4800e5", "g2/analysis/audio-clock-driver-config-2026-10-08/reproduction-receipt.json"),
    "stock_hfrc_target": ("0x4d3915", "g2/analysis/audio-xtal-request-closure-2026-10-08/reproduction-receipt.json"),
    "stock_hfrc2_ratio": ("0x4d38eb", "g2/analysis/audio-clock-driver-config-2026-10-08/reproduction-receipt.json"),
    "stock_pll_generate": ("0x539795", "g2/analysis/audio-clock-driver-config-2026-10-08/reproduction-receipt.json"),
    "stock_floorf": ("0x43a5a1", "g2/analysis/audio-syspll-generator-closure-2026-10-08/reproduction-receipt.json"),
    "stock_roundf": ("0x577d09", "g2/analysis/audio-syspll-generator-closure-2026-10-08/reproduction-receipt.json"),
    "stock_ceilf": ("0x577d41", "g2/analysis/audio-syspll-generator-closure-2026-10-08/reproduction-receipt.json"),
    "stock_fmodf": ("0x577c3d", "g2/analysis/audio-syspll-generator-closure-2026-10-08/reproduction-receipt.json"),
    "codec_hal_power": ("0x58DBB9", "g2/analysis/audio-codec-uart-lifecycle-2026-10-09/reproduction-receipt.json"),
    "codec_hal_configure": ("0x58E09F", "g2/analysis/audio-codec-uart-lifecycle-2026-10-09/reproduction-receipt.json"),
    "stock_hfrc_force": ("0x4d391f", "g2/analysis/audio-hfrc-syspll-closure-2026-10-08/reproduction-receipt.json"),
    "stock_hfrc_disable": ("0x4d3945", "g2/analysis/audio-xtal-request-closure-2026-10-08/reproduction-receipt.json"),
    "audio_timer_wait_unlock": ("0x441f89", "g2/analysis/audio-timer-queue-wait-closure-2026-10-08/reproduction-receipt.json"),
    "stock_priority_disinherit": ("0x45596f", "g2/analysis/audio-queue-cmsis-source-closure-2026-10-09/reproduction-receipt.json"),
    "stock_scheduler_resume": ("0x454dcd", "g2/analysis/audio-timer-daemon-order-closure-2026-10-08/reproduction-receipt.json"),
    "offline_notify": ("0x455DC1", "g2/analysis/audio-uart-rx-stream-ownership-2026-10-09/reproduction-receipt.json"),
    "stock_mcu_memory_config": ("0x47f205", "g2/analysis/audio-clock-reset-active-2026-10-08/reproduction-receipt.json"),
    "stock_sram_config": ("0x47f46b", "g2/analysis/audio-clock-reset-active-2026-10-08/reproduction-receipt.json"),
    "stock_pin_get": ("0x480eef", "g2/analysis/audio-clock-reset-active-2026-10-08/reproduction-receipt.json"),
    "stock_pin_set": ("0x480f0d", "g2/analysis/audio-clock-reset-active-2026-10-08/reproduction-receipt.json"),
    "stock_info_populate": ("0x47f955", "g2/analysis/audio-clock-reset-active-2026-10-08/reproduction-receipt.json"),
    "stock_mcuctrl": ("0x4809c5", "g2/analysis/audio-clock-reset-active-2026-10-08/reproduction-receipt.json"),
    "stock_hfrc2_force": ("0x4d3953", "g2/analysis/audio-hfrc-syspll-closure-2026-10-08/reproduction-receipt.json"),
    "stock_pll_power_enable": ("0x480059", "g2/analysis/audio-clock-driver-config-2026-10-08/reproduction-receipt.json"),
    "stock_pll_power_disable": ("0x48009f", "g2/analysis/audio-clock-driver-config-2026-10-08/reproduction-receipt.json"),
    "stock_pll_init": ("0x5398e1", "g2/analysis/audio-hfrc-syspll-closure-2026-10-08/reproduction-receipt.json"),
    "stock_pll_deinit": ("0x539945", "g2/analysis/audio-hfrc-syspll-closure-2026-10-08/reproduction-receipt.json"),
    "stock_pll_enable": ("0x539995", "g2/analysis/audio-hfrc-syspll-closure-2026-10-08/reproduction-receipt.json"),
    "stock_pll_disable": ("0x539a11", "g2/analysis/audio-hfrc-syspll-closure-2026-10-08/reproduction-receipt.json"),
    "stock_pll_config": ("0x539a41", "g2/analysis/audio-hfrc-syspll-closure-2026-10-08/reproduction-receipt.json"),
    "stock_pll_wait": ("0x539b57", "g2/analysis/audio-hfrc-syspll-closure-2026-10-08/reproduction-receipt.json"),
    "stock_ton_update": ("0x4803c3", "g2/analysis/audio-clock-reset-active-2026-10-08/reproduction-receipt.json"),
    "early_other": ("0x59fbad", "g2/analysis/audio-platform-callbacks-closure-2026-10-08/reproduction-receipt.json"),
    "early_zero": ("0x59fca3", "g2/analysis/audio-platform-callbacks-closure-2026-10-08/reproduction-receipt.json"),
    "middle_action0": ("0x5a0205", "g2/analysis/audio-platform-callbacks-closure-2026-10-08/reproduction-receipt.json"),
    "middle_action2": ("0x5a00fd", "g2/analysis/audio-platform-callbacks-closure-2026-10-08/reproduction-receipt.json"),
    "middle_other": ("0x5a0329", "g2/analysis/audio-platform-callbacks-closure-2026-10-08/reproduction-receipt.json"),
    "middle_zero": ("0x5a05e1", "g2/analysis/audio-platform-callbacks-closure-2026-10-08/reproduction-receipt.json"),
    "callback_plan": ("0x5A45D1", "g2/analysis/audio-uart-newer-callback-composition-2026-10-09/reproduction-receipt.json"),
    "callback_change_state": ("0x5A421D", "g2/analysis/audio-uart-newer-callback-composition-2026-10-09/reproduction-receipt.json"),
    "callback_prepare_state": ("0x5A410D", "g2/analysis/audio-uart-newer-callback-composition-2026-10-09/reproduction-receipt.json"),
    "callback_apply": ("0x5A44BB", "g2/analysis/audio-uart-newer-callback-composition-2026-10-09/reproduction-receipt.json"),
    "stock_temperature_apply": ("0x5a001d", "g2/analysis/audio-early-pcm-gpu-closure-2026-10-08/reproduction-receipt.json"),
    "stock_prepare": ("0x5a0c21", "g2/analysis/audio-pcm21-control-closure-2026-10-08/reproduction-receipt.json"),
    "stock_change_state": ("0x5a0d45", "g2/analysis/audio-pcm21-control-closure-2026-10-08/reproduction-receipt.json"),
    "stock_plan": ("0x5a13e9", "g2/analysis/audio-pcm21-control-closure-2026-10-08/reproduction-receipt.json"),
    "stock_apply": ("0x5a0fc5", "g2/analysis/audio-pcm21-control-closure-2026-10-08/reproduction-receipt.json"),
    "stock_timer_publish": ("0x5a0ae9", "g2/analysis/audio-pcm21-children-closure-2026-10-08/reproduction-receipt.json"),
    "stock_timer_clear": ("0x5a0b55", "g2/analysis/audio-pcm21-children-closure-2026-10-08/reproduction-receipt.json"),
    "stock_completion": ("0x5a0b9d", "g2/analysis/audio-pcm21-children-closure-2026-10-08/reproduction-receipt.json"),
    "stock_ton": ("0x5a0d9d", "g2/analysis/audio-pcm21-children-closure-2026-10-08/reproduction-receipt.json"),
}
rows = []
for alias, targets in sorted(aliases.items()):
    evidence = dict(bindings.get(alias, {}))
    if alias in selected_receipts:
        address, receipt = selected_receipts[alias]
        assert f"{alias} = {address}" in (ROOT / receipt).read_text()
        evidence[address] = [receipt]
    numeric = sorted(k for k in evidence if re.fullmatch(r"0x[0-9a-fA-F]+", k))
    for provider in targets:
        owner = owners.get(provider)
        assert owner and owner in objects, (alias, provider, owner)
        entry_leads = sorted({hex(int(x, 16) & ~1) for x in numeric})
        is_selected = alias in selected and bool(entry_leads) and selected[alias] == (provider, entry_leads[0])
        reason = ("same original entry, matched archive soft-float caller/provider ABI, independently compared against stock hard-float wrapper"
                  if is_selected and alias in ("stock_floorf", "stock_roundf", "stock_ceilf", "stock_fmodf") else
                  "same original entry, matching caller/provider ABI, identical rebuilt source text and original/source execution"
                  if is_selected else
                  "timing-sensitive delay wrapper would add a call/branch" if alias == "stock_delay" else
                  "two conflicting original numeric bindings" if alias == "pcm21_classify" else
                  "selected source entry and caller/provider ABI not jointly verified")
        rows.append({"alias": alias, "candidate_provider": provider,
                     "selected_archive_member": owner,
                     "selected_source": objects[owner]["source"],
                     "selected_source_sha256": objects[owner]["source_sha256"],
                     "selected_object_sha256": objects[owner]["object_sha256"],
                     "original_entry_leads": entry_leads,
                     "binding_receipts": evidence,
                     "abi_review": ("void(uint32_t) matched" if alias in ("stock_timer_publish", "stock_timer_clear") else "void(void) matched" if alias == "stock_completion" else "void(uint32_t,uint32_t) matched" if alias == "stock_ton" else "void(pcm21_power_request*) matched" if alias == "stock_prepare" else "void(uint32_t,uint32_t) matched" if alias == "stock_change_state" else "uint32_t(pcm21_power_request*,uint32_t*,uint32_t*) matched" if alias == "stock_plan" else "void(uint32_t,uint32_t,uint32_t,uint32_t) matched" if alias == "stock_apply" else "void(uint32_t) matched" if alias == "stock_temperature_apply" else "void(uint32_t,uint32_t,uint32_t,uint32_t) matched; original step entry" if alias == "callback_apply" else "void(power_request*) matched" if alias == "callback_prepare_state" else "uint32_t(power_request*,uint32_t*,uint32_t*) matched" if alias == "callback_plan" else "void(uint32_t,uint32_t) matched" if alias == "callback_change_state" else "uint32_t(uint32_t,uint32_t) matched; callers ignore return" if alias == "stock_ton_update" else "uint32_t(uint32_t) matched" if alias in ("early_other", "middle_other") else "uint32_t(void); caller R0 ignored" if alias in ("early_zero", "middle_zero") else "void(uint32_t) matched" if alias == "middle_action0" else "uint32_t(uint32_t*) matched" if alias == "middle_action2" else "uint32_t(ListItem_t*) matched" if alias == "audio_block_remove" else "int32_t(void*) matched" if alias == "stock_priority_disinherit" else "int32_t(void) matched" if alias == "stock_scheduler_resume" else "int32_t(void*,u32,u32,u32,u32*,i32*) matched" if alias == "offline_notify" else "uint32_t(config*) matched" if alias in ("stock_mcu_memory_config", "stock_sram_config") else "uint32_t(uint32_t,uint32_t*) matched" if alias == "stock_pin_get" else "uint32_t(uint32_t,uint32_t) matched" if alias == "stock_pin_set" else "uint32_t(uint32_t,const void*) matched" if alias in ("stock_mcuctrl", "stock_pll_config") else "uint32_t(uint32_t,uint32_t*) matched" if alias == "stock_pll_init" else "uint32_t(uint32_t) matched" if alias in ("stock_pll_deinit", "stock_pll_enable", "stock_pll_disable", "stock_pll_wait") else "void(void), return ignored" if alias == "stock_info_populate" else "void(List_t*,ListItem_t*) matched" if alias == "audio_block_sorted_insert" else "void(Queue_t*) matched" if alias == "audio_timer_wait_unlock" else "uint32_t(void) matched" if alias in ("callback_save_disable_irq", "stock_hfrc_disable", "stock_pll_power_enable", "stock_pll_power_disable") else "uint32_t(uint8_t*) matched" if alias == "stock_pll_power_enabled" else "uint32_t(uint32_t,uint32_t,uint32_t*) matched" if alias == "stock_hfrc_target" else "uint32_t(uint32_t,uint32_t,uint32_t*) matched" if alias == "stock_hfrc2_ratio" else "uint32_t(config*,uint32_t,uint32_t) matched" if alias == "stock_pll_generate" else "archive soft-float R0/R1 matched; stock S0/S1 oracle" if alias in ("stock_floorf", "stock_roundf", "stock_ceilf", "stock_fmodf") else "uint32_t(void*,uint32_t,bool) matched; caller passes 0/2 and 1" if alias == "codec_hal_power" else "uint32_t(void*,const config*) matched" if alias == "codec_hal_configure" else "uint32_t(uint32_t) matched" if alias in ("stock_hfrc_force", "stock_hfrc2_force") else "void(void) matched") if is_selected else "pending",
                     "status": "admitted_same_object_alias" if is_selected else "deferred",
                     "reason": reason})
assert len(aliases) == 64 and len(rows) == 64
groups = {}
for row in rows:
    for entry in row["original_entry_leads"] or ["no numeric lead"]:
        key = (entry, row["selected_archive_member"], row["candidate_provider"], row["abi_review"])
        groups.setdefault(key, []).append(row["alias"])
group_rows = [{"original_entry_lead": e, "selected_archive_member": m,
               "candidate_provider": p, "abi_review": abi,
               "aliases": sorted(names)} for (e, m, p, abi), names in sorted(groups.items())]
result = {"historical_alias_names": len(aliases), "candidate_pairs": len(rows),
          "admitted_now": sum(r["status"] == "admitted_same_object_alias" for r in rows),
          "deferred": sum(r["status"] == "deferred" for r in rows),
          "groups": group_rows, "aliases": rows,
          "limits": "Numeric receipt binding and source symbol ownership are leads. Only the fifty-one selected same-entry aliases have a joint original/body/ABI proof; other names remain unresolved."}
(A / "historical-alias-groups.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"{len(aliases)} historical names grouped: {result['admitted_now']} admitted, {result['deferred']} deferred")
