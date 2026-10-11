# SMP database service candidate

`db_service.c` reconstructs the complete bounded SmpDbService body at 0x542960..0x5429f2. It walks exactly ten 24-byte records at 0x200708ec. The in-use predicate is the stock helper's `active || remaining || count`. Each serviced row saturates three 32-bit counters by 1000, divides its 16-bit count by the configured 16-bit divisor when interval reaches zero, reloads interval from configuration if the reduced count remains nonzero, clears active when expiry reaches zero, and starts a one-shot 1000-unit service timer if the row remains in use and timer state is inactive.

The configuration pointer cell is 0x200004b8. The timer object and active byte are at 0x200709dc and 0x200709e9. `g2_smp_candidate_db_service(void*)` matches the SMP handler callback signature; its context supplies only the lower timer-start provider. The source preserves the stock ARM divide-by-zero result of zero through an explicit divisor check. It does not implement timer scheduling, database initialization or elapsed wall-clock time.

See `g2/analysis/smp-db-candidate-20261010/REPORT.md` for original-byte comparison and limits.
