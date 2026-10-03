# Independent review 2317

**Result:** PASS_SCOPED.

Isolated replay regenerated all 576 fixtures. Source, body [0x6384,0x6462), and all candidate file hashes match. Every child and division path executes original code without function interception. For the zero-field configuration, 6352 returns 128 (category zero OR 0x80), 6294 returns 4, and 623C returns 10; the checker stores these returns and uses the original cached flags. In the low-flags-equal-one case, 128 masked with 0x7F supplies raw zero to 6262. Full parameter write/call ledger, early count-failure/status results and R4-R11/SP assertions pass.

**Limits:** The composition uses bounded zero-field and flag/validity/count patterns; broad leaf fields are covered in separate evidence. Pointer mutation, aliasing, physical meaning and whole firmware coverage remain unproven. No canonical admission.
