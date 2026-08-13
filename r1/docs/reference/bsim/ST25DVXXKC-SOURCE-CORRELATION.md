# R1-to-ST25DVxxKC source correlation

This records a Ghidra BSim comparison between the SHA-pinned R1 application
`2.2.6.0009` and a symbol-bearing Cortex-M4 reference compiled from
STMicroelectronics' BSD-3-Clause ST25DVxxKC component at fp-sns-stbox1 commit
`e9a35449b777699b5e1dd0f1466de0ead554893a`. The reference is a correlation corpus,
not a claim that the R1 used this exact checkout or compiler command.

The run's raw artifacts -- the comparison CSV, the Ghidra logs, and the generated
hash record -- are regenerable tool output and are not tracked in this repository.
Their pinned hashes are reproduced below so a fresh run can be checked against
this one.

## Result

- application image: 646,408 bytes at `0x00027000...0x000c4d07`;
- signature-bearing R1 functions: 2,648;
- reference functions in `0x00100000...0x001023ff`: 231;
- candidates retained per R1 function: 12;
- raw comparison rows: 31,776;
- exact anchor: `0x00031D78` -> `ST25DVxxKC_ReadReg`, similarity `1.0`; and
- exact anchor: `0x00031F2C` -> `ST25DVxxKC_WriteReg`, similarity `1.0`.

The complete CSV is candidate evidence. The 27 admitted provider functions were reviewed
function-locally against ST's register constants, IO-table layout, status handling, chunking,
mailbox rules, and public API roles. Similarity alone does not admit a provider attribution.

## Input and output pins

| Artifact | SHA-256 |
| --- | --- |
| R1 application | `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a` |
| compiled ST reference ELF | `4037a523952269b102e7d5aefe72ee87649cbf9c49a1a23aad3023328706193b` |
| raw correlation CSV | `fd1692b73c5abdc2f8cadf2885ea77f48023097ec9d13dcee2bced7c5ea6cbe7` |

The source inputs, license, commit, archive, and file hashes are pinned in
[`../../../../third-party/fetched/manifest.json`](../../../../third-party/fetched/manifest.json).
After compiling a symbol-bearing Cortex-M4 ELF from the pinned `st25dvxxkc.c` and
`st25dvxxkc_reg.c`, reproduce the comparison with
`run_r1_application_source_correlation.sh` from the upstream research workspace
(see [Analysis tooling](../../README.md#analysis-tooling)), passing the ST reference
ELF and the `0x00100000...0x00102400` reference range.
