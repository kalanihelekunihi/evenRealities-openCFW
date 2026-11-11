/* QP module-name strings passed as the first argument of opencfw_em9305_assert().
 * Stock firmware_ble_em9305.bin (g2-2.2.6.10) holds them in the rodata tail as NUL-terminated
 * ASCII, each followed by 0xff pad: 0x33451c "qk", 0x334520 "qf_dyn", 0x334538 "qf_actq",
 * 0x334540 "qf_mem" (the neighbours 0x334528 "qf_act", 0x334530 "qep_hsm", 0x334548 "WsfOs" are
 * not referenced by any reconstructed unit). The callers used the raw stock addresses; they
 * now reference these symbols so the image layout may shift (wave 25 absolute-address audit,
 * g2/docs/em9305-abs-address-audit.md). The callback in SRAM 0x80fe1c receives the pointer. */
const char opencfw_em9305_qp_module_qk[] = "qk";
const char opencfw_em9305_qp_module_qf_dyn[] = "qf_dyn";
const char opencfw_em9305_qp_module_qf_act[] = "qf_act";   /* stock 0x334528; now referenced by the QP/C 6.5.1 qf_act unit */
const char opencfw_em9305_qp_module_qep_hsm[] = "qep_hsm"; /* stock 0x334530; now referenced by the QP/C 6.5.1 qep_hsm unit */
const char opencfw_em9305_qp_module_qf_actq[] = "qf_actq";
const char opencfw_em9305_qp_module_qf_mem[] = "qf_mem";
