# ILO measurement, compensation and timer refresh

**1,489 fresh three-way original/independent/public cases PASS**: 48 start/stop, 1,200 measurement, 240 full compensation and one null-context case. The fresh run uses the recorded ELF hash, not inherited inventory counts. Independent source is [ilo.c](../../components/touch/ilo_compensation_offline/ilo.c); verbatim public bodies are extracted from pinned PDL35f1714 and CapSense247a9a0 with explicit ARM32 environment. No function-entry stubs. Public CapSense uses the original timer-calculator peer5d71; independent source uses its previously validated native implementation.

## Recovered software interface

| Function | Stock address | Behavior |
| --- | --- | --- |
|Start measurement|0x9d90|If prevention byte20000f1d is zero, sets measuring byte20000f1e and routes clocks via SRSS registers40030034/40030018|
|Stop measurement|0x9ddc|If not prevented, clears measuring and clock routing; does not clear running byte20000f1c|
|Measure/compensate desired interval|0x9e18|Accepts100..2000000 microseconds and a nonnull output; first call starts counter reference, later calls poll completion and convert counter result|
|CapSense compensation|0x5dd8|Starts measurement, polls with desired500 microseconds, reads counter, stops measurement, updates compensation and both timer caches, then updates live timer|

The measurement returns0x4a0001 for invalid desired range/null output, 0x4a0003 for wrong full control register/selection or zero completed count, 0x490004 while starting/waiting, and0 on completion. The first valid call programs COUNTER1 at4003001c to SystemCoreClock(20000878)>>10 and sets running. Later calls require its bit31 and a nonzero COUNTER2 at40030020. Invalid state/unfinished counter retains output/running; success writes output and clears running. Supported offline arithmetic contract is stable coherent globals with SystemCoreClock>=1024; divide-by-zero behavior is not recovered.

For desired interval d, rounded=d*100+1250 and counts=floor(rounded/2500), with uint32 arithmetic. ratio=(COUNTER2*SystemCoreClock)/(SystemCoreClock>>10), with wrapping product. If COUNTER2*counts>=0x400000 after uint32 wrapping, result=(ratio/40)*(rounded/2500000); otherwise result=(ratio*counts)/40000. See source and original disassembly for rounding and wrap semantics.

The outer routine returns1 immediately for null context. Otherwise it retries **every nonzero measurement status**, with no explicit timeout or error cleanup in the selected function. Tests stop before a sixth measurement body in noncompleting scenarios; that is a bounded observation, not proof of a hardware deadlock. On success it reads COUNTER2, stops, and sets internal+44 factor to ((counter<<24) mod2^32)/1000000. It recomputes active cache+32 from desired+28 and LP/WOT cache+40 from desired+36 via the closed calculator. It selects LP cache iff common status0x20 is set, otherwise active cache, then updates live AOS_CTL low16 even when neither scan flag is set. Upper16 is preserved.

## Implications and limits

Timer values are requested software intervals and encoded register caches; supplied COUNTER2 values are synthetic. No measured physical frequency, scan cadence, readiness latency, concurrent exclusion or hardware fault is established. Counter40 yields factor671; counter256 yields0 because of 32-bit shift, an abnormal synthetic boundary case, not an observed oscillator result. The SDK interpretation of factor is frequency*2^14/1000000. Existing initial factor655 is nominal, not a measured result.

For CFW changes, retain both timer caches and the live-selection rule when recalibrating. Adding a timeout requires a defined restoration policy: measurement start, running and measuring flags are distinct, and Stop does not reset running. The prevention lock's PM callback is covered separately in ../touch-ilo-pm-closure-2026-10-08/REPORT.md. Full callback registration/startup, physical counter completion and hardware frequency remain outside this batch. No exact-byte or full-source-completeness claim.

Reproduce with extract_public.py --pdl <pinned cy_sysclk.c> --capsense <pinned cy_capsense_sensing_lp.c> --output <scratch/public>, then build_offline.py --gcc <ArmGNU13.3 gcc> --public-object <pinned public.o from MSCLP attribution> --public-ilo-source <scratch/public/public-ilo.c> --output <scratch>, and verify.py <scratch/ilo.elf>. The venv Python supplies Unicorn/Capstone/pyelftools. Reproduction receipt binds sources, compiler, flags, public object and ELF. No production firmware/index/commit/device changes.
