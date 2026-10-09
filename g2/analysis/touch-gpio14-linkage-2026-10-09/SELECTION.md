# Predeclared original-instruction linkage constraints

Preserve the prior raw-object mismatch in gpio14-family. Link that unchanged
authenticated object only at addresses proven by four original Thumb BLs:

| Object relocation offset in Pin_Init | Stock BL address | Stock target / section |
| --- | --- | --- |
| 76 | 0x8F30 | Write0x8E64 |
| 86 | 0x8F3A | SetDrivemode0x8E84 |
| 96 | 0x8F44 | SetHSIOM0x8E28 |
| 106 | 0x8F4E | SetInterruptEdge0x8EBE |

Pin_Init starts0x8EE4. All four ELF relocations are R_ARM_THM_CALL(type10)
against these named sections, not guessed addresses. SetHSIOM LDR at0x8E38
references literal0x8E5C, and LDR0x8E3E references0x8E60, proving its8-byte
literal pool within60-byte section extent. Pin_Init PC-relative loads reference
0x8F94/0x8F98/0x8F9C, placing its pool after code endpoint0x8F92 and ending
at0x8FA0. These original instruction references motivate full section
accounting, rather than expanding bounds merely to achieve equality.

Compare the five linked sections against exact original bytes. No instruction,
source, compiler option or relocation addend is manually edited. If linking
differs, preserve the result; no address search or fitting. Existing symbol
records and raw relocatable outcomes remain untouched.
