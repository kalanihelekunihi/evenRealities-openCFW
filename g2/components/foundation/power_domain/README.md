# Power-domain descriptor lookup

Reconstructed source maps the locked Apollo firmware's34 power-domain records to a16-byte `opencfw_power_domain_descriptor_t`. `opencfw_power_domain_descriptor` returns6 for null output or domain>=34, otherwise0 with the copied record. `opencfw_iom_domain_descriptor` applies the actual `(uint8_t)(module+3)` selection before lookup. It does not power down or validate a hardware module.

Build `make -C g2 power-domain-simulator`; run `verify.py --elf <ELF> --output <new JSON>` with the installed native Unicorn environment. [Analysis, scope and evidence](../../../analysis/power-domain-descriptor-2026-10-06/REPORT.md) distinguish the fully returning stock lookup from the live-frame consumer cut. The isolated O2 semantic build is not a production image or byte-match claim.
