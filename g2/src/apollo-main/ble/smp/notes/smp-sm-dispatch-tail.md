# SMP state-machine transition tail

`dispatch_tail.c` reconstructs the transition-table portion at 0x56f0ec..0x56f144 within `smpSmExecute`. It reads the CCB connection and state bytes at +61/+62, classifies the connection role through an explicit provider, selects one of two transition groups through global base 0x20070aec +228/+232, searches three-byte event/next-state/action triples, falls back to the four-triple default table and calls the selected indirect action. It preserves stock behavior for no match and zero event sentinel cases.

This is an **88-byte tail subcontract**, not the complete 738-byte `smpSmExecute` body. It begins after the logging cascade. The connection role provider and indirect action callbacks remain explicit boundaries, and initialized transition/action tables are not supplied. The original-byte comparison and full-body frontier are in `pre-consolidation:g2/analysis/smp-sm-dispatch-tail-20261010/REPORT.md`.
