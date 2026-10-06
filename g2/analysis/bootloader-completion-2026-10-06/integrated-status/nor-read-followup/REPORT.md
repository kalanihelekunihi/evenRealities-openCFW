# NOR transaction/read provider closure

The previous storage checkpoint intercepted NOR read at `420f70`. The follow-up links reconstructed read plus local transaction helpers and executes actual source blocking transfer/FIFO/polling in the reset→mount→DFU→handoff chain.

`nor_read/runtime_helpers.c` recovers mutex acquire/release (`41fe9c`, `41fed4`), transaction entry/exit (`41ff08`, `41ff1e`), latency state (`41ff34`), read configuration (`420e8c`), busy-bit reader (`42074e`), two-phase busy wait (`4207a2`) and fixed-count wait (`4207f4`). Transaction setup continues after mutex failure, matching the original. Mode flag `200271c5==1` suppresses power operations; otherwise setup resumes and teardown suspends. Latency changes byte5 of timing state `2000023c`, separately from the 24-byte read template at `20000224`.

The busy reader issues instruction5 and a one-byte status transfer. Transfer errors propagate; success returns status bit0. The wait first performs up to200 busy checks with delay(5) after each unsuccessful check; it then performs `count` checks, each preceded by task-delay(1) when kernel state==2 or raw-delay(1000) otherwise. Read's count is500. Exhaustion returns1. Values are provider arguments, not established wall-clock units. A nonzero status-transfer error is treated as busy by the wait, rather than returning that error immediately.

Read-mode setup copies six words from the RAM template and changes bytes0/4/5/8/15 to8/6c/0/10/1. Existing source `420e08` performs disable/device-configure/enable and device-mode publication. Failure logs and returns; success enables latency and issues control request18 with byte10. Logger comparison is severity/line only.

Validation:

- Local helpers: PASS177 cases /544 distinct original instruction bytes. Mutex failure/zero handle, mode flag variants, latency low-byte truncation, configuration/control errors, busy-bit/status errors and first/second-phase boundaries are compared.
- Source-read reset integration: PASS2 cases /24,896 distinct original bytes, covering both OTA flags. Original/source final synthetic NOR, application bytes, released file handle, task events, operation counts and architectural handoff agree. Normal case reads54 times; update case72.
- The broad Unicorn memory-read hook disturbed reset decompression in this fixture. Restricting the hook to MSPI port addresses restores the passing original/source comparison; the model is deliberately limited to those ports.

Reproduce:

```sh
make -C g2/components/bootloader/nor_read helpers-compatible
make -C g2/components/bootloader/thread_creation dfu-storage-read-compatible
```

Receipts are `g2/build/bootloader-completion/nor-read-helpers/comparison.json` and `g2/build/bootloader-completion/dfu-storage-read-compatible/comparison.json`. The latter consumes the source-created filesystem seed ELF. Source memory contains authenticated initializer/vector data, not stock executable code.

Still modeled: mutex provider/kernel state/delay, MSPI device configure/control/power and CQ callbacks, FIFO port delivery, NOR program/erase, application erase/program/read and physical timing/coherence. These are distinct from missing source implementations. The source-read profile is a follow-up to the earlier full aggregate checkpoint; the full aggregate has not yet been rerun with this new variant as a prerequisite. No hardware access, commit or byte-identical/full-source claim.

## Subsequent native-provider integration

The source NOR read/program/sector-erase profile passes 2 cases / 25,684 distinct original instruction bytes. The modeled port implements opcodes06/04/02/20/05/6c; native source emits those operations, performs page splits, polls, restores mode and releases transaction ownership. Programming verifies1→0 at the modeled cell boundary; this does not prove physical page atomicity.

Native MSPI power, power-domain enable/disable, clock release-all and device configuration/clockgen integration then passes 2 cases / 28,874 bytes in `dfu-storage-power-compatible/comparison.json`. This closes hardware-operation implementation bodies while retaining explicit physical-MMIO/delay models. Supporting direct comparisons: power-domain selectors and shared-domain release 960 / 966; clock release-all 2,560 / 96; read control requests 16 and 24: 436 / 606; NOR write/erase/WREN/WRDI 27 / 590; MSPI power 19 / 1,008; device configure 2,823 / 3,142. Counts overlap; all byte counts denote distinct original instruction bytes.

The full aggregate result in the parent directory predates these follow-up variants. New native integration is a passing focused profile; do not treat that earlier aggregate as a current all-provider source binding.
