# Touch command handlers and deferred configuration write

New independent C reconstructs all nine command-table branches in `app_event.c`, plus deferred dispatch in `deferred.c`; `touch_commands.h` provides app-facing constants and a little-endian reader. The standalone ELF SHA is `078c318b087b7c65dc05081299b0f83898228d5b17093e9f41b01a37acbc877b`. It links public PDL IRQ/helper/critical code for comparison, not a stock producing-library attribution. No accepted firmware checkpoint or production payload was changed.

## Command behavior

Only write-complete0x20 without error0x40 dispatches commands, with the low8 RX-index value in1..16. Shared TX/RX buffers remain16 bytes and require serialization as established in ../touch-callback-ownership-2026-10-08/REPORT.md.

| Opcode / in-frame body | Observed behavior | App interpretation |
| --- | --- | --- |
| 0,3 /370e | Rearm RX; no command-specific TX change | No new response fields established |
| 1 /3746 | Set TX prefix02 02 00 01; retain other12 bytes; arm16 | Prefix only; version units not recovered |
| 2 /382c | Prefix02 00 17; arm16; mailbox20000000 byte0 then reset entry7e14 | ACK preparation precedes reset; delivery is not guaranteed |
| 4 /384c | Zero10 local bytes; collect widget1 u16 sensor values at offset0 and widget2 at offset8; copy10 to TX; arm16 | Little-endian values; remaining6 TX bytes retain old data |
| 5 /37a0 | Set200009cf=1; prefix05 00 17; arm16 | Requests later baseline work; immediate ACK is not completion |
| 6 /3766 | Config u16 at200009d4 -> first2 TX bytes; retain14; arm16 | Parse little-endian prefix only |
| 7 /37c8 | If RX count<=2 or payloadu16LE=0: prefix07 ff 17; otherwise write config200009d6 and active parameter200004e8, set flags200009ce/cd, prefix07 00 17; arm16 | Send at least3 bytes, nonzero u16LE. Physical units remain unknown |
| 8 /3780 | Clear TX16, write config200009d6 u16LE at offset0; arm16 | Remaining14 bytes are zero, unlike command6 |

Read-complete0x10 subsequently fills TX16 with5a, rearms and releases attention. Combined event flags preserve write-before-read ordering; therefore a write ACK can be overwritten by a simultaneous read-complete callback. No real host transaction timing is asserted.

Command4's stock sensor helper reads widget descriptor array through200004ec+12, stride0x90, sensor pointer+4, countu16+0x38; each sensor stride10 contributesu16+4. The bounded C and fixtures admit widget1<=4 and widget2<=1 so the10-byte local storage remains valid. Those maxima are test preconditions, **not a newly proven stock configuration**. Larger counts require independent configuration evidence and are not declared safe.

## Corrected storage interpretation

Following the dependency bodies exposed misleading historical names: `touch_config_load_from_eeprom`0x3a38, `touch_config_read_adapter`0x3568 and `Cy_Em_EEPROM_Read`0x8aac participate in a **write path**. The input-to-row-buffer transfer and subsequent row-helper call agree with public `Cy_Em_EEPROM_Write`/`WriteSimpleMode`, not reading configuration back into RAM. The true alternate read dispatcher is at0x8a78. Shared catalogues and sealed prior reports are preserved; ../touch-eeprom-dispatch-2026-10-08/REPORT.md records the correction and original-instruction direction evidence.

Deferred0x3a80 enters a critical section, snapshots flagsce/cd and activeu16, clears both flags, then restores saved PRIMASK. Flagce initializes gesture state at20000940 (80 bytes zeroed; firstu16 is snapshot or1000 when zero). Flagcd sets the `UNVE` sentinel at config200009d0 and passes8 configuration bytes to the storage write adapter. An uninitialized storage flag200008c4 prevents provider entry. Provider status0 or093e0004 maps to success; other statuses map to3. Logging is an actual return-zero leaf and gives no new host response.

Thus command7 ACK means the parameter was accepted and deferred work scheduled. It does **not** convey the later write result. This corrects the earlier provisional reload/overwrite interpretation: the observed direction is outward toward row programming. Actual persistent programming, power-loss durability, provider callback behavior and scheduling remain unproved.

## Fresh validation and boundaries

Final standalone source revision passes **13,440** command comparisons (events/counts/opcodes0..9, payload0/1/1234/ffff, synthetic sensor counts0/4 and0/1); **288** real IRQ/helper/registered-callback comparisons for commands1/5/6/7/8/invalid9 with no semantic child cuts; **192** deferred comparisons with an explicit EEPROM-entry data/status boundary. Full configuration, active parameter, buffers/guards, ordered callback/MMIO effects and relevant SP/PRIMASK compare. DFU cases stop before reset entry; their stack state is outside comparison because frames differ. Actual stock memcpy/memset/sensor/helper instructions run. Logger no-state effect is omitted in reconstructed C. Three command mutants (endianness, deferred flag, retained tail) are rejected.

The EEPROM test boundary retains input data and supplies status, rather than pretending to read it back. No EEPROM/flash/provider or physical reset body executes. Source-side reset loops and EEPROM sentinel bodies are explicit test boundaries, not deployable provider implementations. Synthetic counts/FIFO/W1C and mapped RAM remain distinct from hardware behavior. No byte-identical callback or whole-image completeness claim.

Remaining actionable dependencies: classify/validate actual provider vtable callbacks and simple/extended row operations; prove stock sensor counts; trace host/IRQ scheduling. These are independent of the completed command comparisons, so this is a bounded milestone rather than global exhaustion.
