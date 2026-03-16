# G2 Firmware v2.0.7.16 — Reverse Engineering Analysis

Firmware version: **2.0.7.16** (S200 / Ambiq Apollo510b)
Analysis date: 2026-03-07
Sessions: 29–39l (decompilation, naming, handler mapping)

## Directory Structure

```
v2.0.7.16/
├── ANALYSIS.md              Top-level overview (8641 functions, all HIGH confidence)
├── main_firmware/           Main S200 firmware (7233 functions)
│   ├── function_map.txt     7233 function names (tab-separated: addr, FUN_, name, module, confidence)
│   ├── data_map.txt         577 data symbol names (all semantic, zero generic)
│   ├── handler_map.txt      25 BLE service handlers + cross-cutting analysis (1623 lines)
│   ├── protobuf_schemas.txt Protobuf field tables per service
│   ├── protobuf_validation.txt Schema validation results
│   ├── module_architecture.txt Module dependency graph
│   ├── rtos_map.txt         FreeRTOS task/queue/timer map
│   ├── source_tree.txt      Reconstructed IAR EWARM source tree (330 paths)
│   ├── annotated_key_functions.c Key function annotations
│   └── manifest.json        Ghidra export metadata
├── bootloader/              S200 bootloader (796 functions)
├── box_mcu/                 Charging case MCU (414 functions)
├── touch/                   CY8C4046FNI touch controller (198 functions)
├── ble_em9305/              EM9305 BLE radio (ARC EM architecture)
├── codec/                   GX8002B audio codec
└── tools/                   Scripts and data used for analysis
    ├── *.py                 Python upgrade scripts (cordio, elog, lvgl/lib/freetype)
    ├── *.sh                 Shell scripts (elog upgrades, rtos sed commands)
    └── *.tsv                Tab-separated upgrade data (elog corrections, BLE, app, lib, LVGL)
```

## Key Files

| File | Entries | Description |
|------|---------|-------------|
| `function_map.txt` | 7233 | Every function named at HIGH confidence via elog `__FUNCTION__` strings |
| `data_map.txt` | 577 | All static data symbols with semantic names |
| `handler_map.txt` | 25 sections | Complete BLE protobuf service handler architecture |
| `protobuf_schemas.txt` | 20+ tables | Per-service protobuf field descriptor tables |

## Naming Sources

1. **EasyLogger `__FUNCTION__`**: ~2000 functions identified via `elog_output()` format strings
2. **Cordio BLE SDK**: ~800 functions matched against Cordio stack headers
3. **NemaGFX GPU SDK**: 7 functions matched via register addresses + context struct offsets
4. **LVGL v9.3**: ~300 functions matched against LVGL source
5. **FreeRTOS**: ~100 functions matched against kernel API
6. **Behavioral analysis**: Remaining functions named via call graph + data flow

## How to Apply Names to Decompiled Code

The function_map.txt and data_map.txt contain the renaming data. To apply:

```bash
# Generate sed script from function_map.txt
awk -F'\t' '{print "s/\\b" $2 "\\b/" $3 "/g"}' function_map.txt > rename_functions.sed

# Generate sed script from data_map.txt
awk -F'\t' '{print "s/\\b" $2 "\\b/" $3 "/g"}' data_map.txt > rename_data.sed

# Apply to decompiled.c
sed -f rename_functions.sed -f rename_data.sed decompiled.c > decompiled_named.c
```
