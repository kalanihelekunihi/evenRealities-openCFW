# openCFW nPMX snapshot

This is a byte-identical compact snapshot of Nordic Semiconductor's official
`npmx` repository at `e1aaec53f456887a7d7b80d82f684d1ac3cb08c8`, one commit
after tag `v1.0.1`. The stock G2 image selects this public state with two
adjacent-commit discriminators: the February 2025 ADC result-register rewrite
is present, while the April 2025 float-promotion fix is absent.

The snapshot contains every nPMX driver and public driver header, the generic
backend, root API headers, templates, license, and release metadata. The large
generated nPM1300 ADK is intentionally not part of this compact provenance
tranche. Production integration still needs a reviewed Apollo510 I2C backend,
the G2 nPM1300 configuration, interrupt wiring, and power-rail policy.

Run `python3 third_party/npmx/verify_snapshot.py` to authenticate the local
files and the two source-level version discriminators.
