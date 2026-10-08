# GPIO provider closure and clock-request ownership

Four complete stock functions now have readable [GPIO C](../../components/audio/gpio_providers_offline/gpio.c), [clock-request C](../../components/audio/gpio_providers_offline/clock_requests.c) and [GPIO layout/interface](../../components/audio/gpio_providers_offline/gpio.h). Final exact ELF **94dcf55b752a13525e9c00ae781c01446f8efbfdc6ad7681b83d28ef2c220492** passes **2,432 native/original comparisons**, plus10 original-only platform-continuation assertions. [Exact validation](exact-build-validation.json), [build](build_offline.py), [addresses/data hashes](function-bindings.json), [caller chain](caller-chain.json).

## GPIO configuration and errors

Getter0x480EEE..0x480F0C validates pin<224 before NULL output. Invalid pin returns5 even with NULL; valid pin/NULL returns6; success copies the entire word from0x40010000+4*pin and returns0.

Setter0x480F0C..0x480F8A rejects pin>=224 with5. On ordinary pads, normal drive bits[11:10]>=2 require the corresponding drive-capable mask bit; otherwise return7. On extended-drive pads, pull bits[15:13] must be0/1/6, otherwise7. Both seven-word validation matrices match locked OTA data and pinned source. The normal drive check ignores bit12 (overloaded slew/drive extension). Rejection occurs before IRQ masking or PADKEY writes.

Accepted setters save/disable IRQs through actual0x473940, write PADKEY0x40010400=0x73, write **all32 configuration bits unchanged**, lock PADKEY=0 and restore PRIMASK. There is no mask that sanitizes incoming upper configuration bits. Direct1,360 comparisons cover every pin's drive validation, every pull encoding on extended pads, boundary/null cases, PRIMASK0/1 and raw-word preservation.

## GPIO15 incoming-register behavior and caller errors

Clock recovery changes only incoming R5 low nibble to function10 before calling this setter. For pin15, drive encodings2/3 return7 with no pin write. The120 integrated clock comparisons record60 setter7 results and140 setter0 results (including restores), while recovery continues and clears retained requests. Getter always returns0 for its fixed valid pin/output in these fixtures.

The40 complete-common-initializer comparisons distinguish fresh and stored capture. Fresh capture sets R5=0x20074284, making temporary config0x2007428A accepted. With stored capture, supplied R5 values with drive2/3 orallones are rejected. Twelve GPIO-set7 results occur in the stored fixtures, yet all40 common initializers return0. These are explicitly supplied scratch/calibration states; actual runtime R5 reachability and electrical outcomes are not established.

Locally confirmed direct chain: application-init0x5CDD2C→platform wrapper0x4C2AE8→common initializer0x47FAE8→clock recovery0x44B158. The visible wrappers do not assign R5 before common initialization. Transitive board-init and outer-caller register values remain unproved; the scan is not an exhaustive indirect/cross-image call graph.

The common initializer propagates INFO1 read error9, as established previously, but its **platform wrapper discards that status**. Ten original-only continuation tests inject0/1/4/9/allones at0x4C2AF4, execute the actual buck-already-active power-control provider, and confirm unconditional call(0,0). This validates the eight-byte continuation, not the entire board/platform wrapper or physical startup. Recovering a failure at one API layer therefore does not establish system-level failure propagation.

## Clock-request lifetime

Reference update0x44B0B6 narrows its argument to a byte and copies bit0 into retained0x40008858 bit6 under saved PRIMASK. Clock-request update0x44B0D6 narrows index/source to bytes, writes0x200740EC+index, ORs the first six cached bytes and publishes low-five source bits into retained bits1..5 through five ordered writes. It preserves AUDADC-off bit0, reference bit6 and signature. The source enum names slots CG_AUDADC, LL_AUDADC, LL_PDM, LL_I2S0, LL_I2S1 and LL_USB; bitmap bits name HFRC_DED/HFRC2/XTAL/EXTCLK/PLL.

There is **no index<6 validation** in this function: malformed indices6/255 write beyond the six-byte cache; wide values256/257 narrow to0/1. High source bits remain cached but do not contribute to these five flags. These are deliberate malformed-input instruction tests, not naturally reachable corruption claims.

The912 request comparisons include gated and **active** reset sequences. Set EXTCLK in slot4 and HFRC2 in slot2; reset clears the retained word but leaves the cached request bytes. Clear only slot2 afterward and EXTCLK reappears as retained0x5AF00010. Active sequence tests run actual original recovery providers with native GPIO on the reconstruction side and declared readiness responses. Reset consumes retained work without releasing each mux's logical clock need: a feature releases its own request by updating its slot, rather than relying on retained-word reset. Store traces compare effective data width; STRB truncation is reflected rather than mistaking Unicorn's untruncated callback value for stored byte data.

## Preservation and remaining providers

All **1395 prior sealed entries**,110 audit inputs,four checkpoint images and staging were hash-verified before additive sealing. Original sources/tests/manifests remain unchanged. No commits, production edits or device writes.

Synthetic GPIO/PADKEY, INFO1/calibration, peripheral readiness and direct PRIMASK/function entry do not establish electrical mux behavior, physical recovery, actual boot scratch values, full M55 exception support or live scheduling. Full source-built firmware and byte equality remain unproved. No new download was required; pinned source matched these concrete providers. Source exhaustion is not reached.

Next concrete source-backed providers: **INFO1 population0x47F954**, **MCU memory configuration0x47F204**, **SRAM configuration0x47F46A**, and **oscillator/microcontroller control0x4809C4**. Their error handling and side effects remain original-code dependencies in the composed initializer/recovery test image. [Updated dependency index](INDEX.md).
