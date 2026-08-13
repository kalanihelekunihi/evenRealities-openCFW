# Apollo embedded source-path recovery audit

The official image and authenticated 64-shard corpus were read only. The
fail-closed replay is `tools/recover_apollo_embedded_source_paths.py`.

The 43 paths previously reported without Ghidra function correlation have 46
path-pointer cells and 273 halfword-aligned PC-relative Thumb/Thumb-2 `LDR`
decode sites that resolve exactly to those cells. No path is confirmed as
`path_only_data`; 41 remain missed-code candidates and two have independent
entry evidence. Only eight call/table-backed entries are promoted as recovered
functions. This distinction prevents a plausible raw instruction decode from
silently becoming a function-boundary or reachability claim.

## Per-path states

Two paths are `recovered_function`:

- `app\gui\AgingTest\aging_test.c` (path cell `0x0043C760`): recovered
  `0x0043C400`, `0x0043C496`, `0x0043C5F6`, and `0x0043C6CE`. The first two
  have stored Thumb-pointer witnesses; the latter two have direct callers.
  The valid adjacent body at `0x0043C450` is deliberately not promoted.
- `third_party\cordio\wsf\sources\port\freertos\wsf_timer.c` (path cell
  `0x0052A630`): recovered directly called functions `0x0052A474`,
  `0x0052A51A`, `0x0052A542`, and `0x0052A574` (`WsfTimerInit`,
  `WsfTimerNextExpiration`, `WsfTimerServiceExpired`, and
  `WsfTimerUpdateTicks`). The [focused timer audit](cordio-wsf-timer-source-recovery.md)
  closes their ABI, source lineage, globals, locks, and dispatcher callers.

The following 41 paths are individually `missed_code_candidate`; their exact
pointer cells and literal-reference sites are emitted in the tool's `paths`
records:

```text
app\gui\EvenAI\even_ai.c
app\gui\MessageNotify\message_notify.c
app\gui\MessageNotify\msg_notif_timer.c
app\gui\PdtGrayScreen\pdt_gray_screen.c
app\gui\ProductionTest\production_test.c
app\gui\SystemAlert\systemAlert.c
app\gui\anim\bounce_anim.c
app\gui\anim\expand_anim.c
app\gui\navigation\navigation.c
app\gui\setting\setting.c
app\gui\system\system_monitor.c
app\gui\terminal\terminal_query_panel_ui.c
app\gui\terminal\terminal_timer.c
app\gui\translate\translate_data.c
app\ux\ux_production\ux_production.c
app\ux\ux_settings\ux_settings.c
driver\pdm\drv_pdm.c
driver\pdm\drv_pdm_production.c
driver\wdt\watchdog.c
kernel\FreeRTOS-Plus-CLI\prvCommand\prvCommand_filesystem.c
platform\device_mgr\box_uart_mgr.c
platform\input\service_gesture_processor.c
platform\product_test\product_common.c
platform\service\callback_mgr\cb_charge.c
platform\service\callback_mgr\cb_msg_notif.c
platform\service\callback_mgr\cb_ring_battery.c
platform\service\eAT\at_buzzer.c
platform\service\eAT\at_codec.c
platform\service\eAT\at_fs.c
platform\service\eAT\at_tp.c
platform\service\flashDB\NV\service_nvdb_buzzer.c
product\s200\app\config\board_config.c
product\s200\app\config\main.c
third_party\cordio\ble-host\sources\stack\l2c\l2c_main.c
third_party\cordio\ble-host\sources\stack\l2c\l2c_master.c
third_party\cordio\ble-host\sources\stack\smp\smpr_act.c
third_party\lvgl_v9.3\LVGL\src\font\lv_font_fmt_txt.c
third_party\lvgl_v9.3\LVGL\src\widgets\arc\lv_arc.c
third_party\lvgl_v9.3\LVGL\src\widgets\keyboard\lv_keyboard.c
third_party\lvgl_v9.3\LVGL\src\widgets\spinbox\lv_spinbox.c
third_party\tlsf\tlsf_init.c
```

For each candidate, the dense exact-cell LDR evidence strongly supports
compiled-code use and translation-unit provenance, but independent entry,
complete inbound topology, reachability, and exact bounds are not all closed.
Stored odd words near several pools remain leads, not automatic seeds. The
Ghidra baseline stays 7,370; eight reviewed recoveries give a separately
reported effective count of 7,378.

A production-excluded clean-room candidate now records the three WSF helpers;
the focused audit closes their private structure ABI, lock contract, and
caller behavior. Exact vendor source/compiler identity and production
placement remain unresolved. No production overlay or official blob was
changed.
