# P2-9031 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 176 mapped Thumb instruction bytes across the three ranges match the pinned image; all listed literal words match their source addresses.
- The category dispatcher rereads packet+2 for ordered thresholds 128, 96, 64, 32, then uses the corresponding callback/table slot; only the >=128 callback path checks null and reloads the callback before BLX. Callback return is discarded through saved-entry R7.
- The registration path stores the event id and performs ordered external registration calls; the callback installer stores global+88, obtains candidate through 530D4C, truncates to low16 then subtracts four, compares signed against the fresh threshold, and calls reporter only on the less-than branch. The setter at 51C8 stores global+92 and returns with R0 unchanged.

Limitations:

- Meaning of external helpers and callback arguments is not established by this map. Table entries other than explicitly guarded callbacks are dereferenced without null checks.
- Private partial evidence only; no concurrency, physical behavior, or whole-firmware completeness/admission claim.
