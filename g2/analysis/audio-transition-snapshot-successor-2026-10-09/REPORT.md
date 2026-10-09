# Conditional timer-register access successor

**40 original/source comparisons PASS with complete ordered MMIO read/write traces up to their recorded boundary.** The prior sealed 32-case report and source remain unchanged. [Results](results.json), [native ELF and source hashes](reproduction-receipt.json), [additive C](../../components/audio/transition_snapshot_offline/producers.c).

Stock sequence0 at 0x5A1F04 first reads 0x400083E0. If inactive, it skips both cancellation and the second timer read. If active and requested profile equals 0x200002A4, it adjusts TON, writes the core field, stops the timer and publishes byte26. If active but not cancelling, it rereads timer-active before polling completion status 0x40008064. This conditional second read is essential: a universal cached snapshot would remove a real stock read in the active branch.

The initial cached-only successor matched the previous 32 inactive-timer compositions but failed two additional active/non-cancel prefixes. Those debug results were superseded before sealing by the conditional-read implementation; the final 40-case result binds the final ELF. Eight direct fixtures cross active0/1, cancel profile0/4 and PRIMASK0/1 with next4/old0/TON6. Inactive paths stop before delay50, active non-cancel paths before delay1, cancellation paths complete. The original 32 enclosing fixtures retain eight complete paths and24 delay50 cuts. Therefore12 of40 complete;28 stop before real providers. No provider return, physical settling or delivered scheduling is fabricated.

This resolves the eight prior extra-read discrepancies for the executed stable-register fixtures. Dynamic peripheral values/side effects, active completion after real polling, all other transition paths and production patch safety remain outside this result. No new opaque function family is falsely counted: prior transition source is reused.

Codec response lead: 0x57C442 calls blocking reader0x57C1FC, publishes returned length through uint16 output and returns0 on success; it does not validate CRC in that wrapper. Framing/CRC validation must be followed downstream rather than inferred from UART admission. Scheduler handover remains distinct from ready/pending-ready list mutation. These remain next bounded source leads.

[Preservation](preservation.json) checks all prior dictionary seals,110 inputs,four checkpoints and observed index. No Git mutations, production changes, device writes or shared campaign edits.
