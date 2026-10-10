from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent;repo=root.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=['g2/build/pseudocode-first/20260930T190500Z/identity.json','g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl','g2/build/pseudocode-first/20260930T190500Z/receipts/G1-target-and-inventory-107/receipt.json','third-party/upstream/nationalchip-lvp-kws/lib/libdriver_release_v1.0.6.a','third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/spl/spl.c','third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/spl/spl_clk.c','third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/spl/spl_uart.c','third-party/upstream/nationalchip-lvp-kws/arch/cpu/csky/ck804/spl_start.S','third-party/upstream/nationalchip-lvp-kws/boards/nationalchip/grus_gx8002b_dev_1v/boot_board.c','third-party/upstream/nationalchip-lvp-kws/boards/nationalchip/grus_gx8002b_aiot_1v/clock_board.c','third-party/upstream/nationalchip-lvp-kws/include/driver/gx_pmu_ctrl.h','third-party/upstream/nationalchip-lvp-kws/lvp/main.c','third-party/upstream/nationalchip-lvp-kws/lvp/lvp_mode.h']
bodies=json.loads((root/'bodies.json').read_text());assert len(bodies)==10 and all(x['decompile_completed'] for x in bodies)
assert all(x['equal_outside_named_relocations'] for x in json.loads((root/'provider-matches.json').read_text()))
archive=json.loads((root/'archive-receipt.json').read_text());assert archive['wakeup_source_exact_match'] and archive['analog_update_exact_match'] and archive['start_mode_body_equal_except_call_relocation']
inputs += [str((root.parent/'private-install/Ghidra/Processors/CSKY/data/languages'/x).relative_to(repo)) for x in ['32b_priv.sinc','32b_data.sinc','csky_v2.sla']]
receipt={'schema_version':1,'campaign_id':'20260930T190500Z','target_sha256':'f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa','status':'partial_ready_for_independent_review','ten_body_instruction_bytes':sum(x['total_bytes'] for x in bodies),'input_hashes':{p:sha(repo/p) for p in inputs},'remaining_scope':'transitive helper and XIP lifecycle semantics, MMIO hardware behavior, independent review, canonical mapping correction','changed_canonical_ledger_or_gate':False}
(root/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
manifest={p.name:sha(p) for p in sorted(root.iterdir()) if p.is_file() and p.suffix in ['.txt','.json','.py','.java','.md','.bin','.o'] and p.name!='SHA256MANIFEST.json'}
(root/'SHA256MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('validated 10 bodies, provider provenance, and manifest',len(manifest),'files')
