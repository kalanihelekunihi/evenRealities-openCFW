# Predeclared unchanged-source GPIO family comparison

Select known inferred PDL targets before compilation: SetHSIOM0x8E28/52B,
Write0x8E64/32B, SetDrivemode0x8E84/58B, SetInterruptEdge0x8EBE/36B,
Pin_Init0x8EE4/174B. These are previously identified attribution candidates,
not new discovered functions. No explicit overlapping task address was found in
the bounded current contract search; no shared campaign reservation is made.

Use unchanged pinned cy_gpio.c hash
`0ece9d664b46e02b6ec1cf7a32bde31c037318b048f01ff586188b74f7aa438f`,
the authenticated GNU14.2.1 compiler and identical source/header/flag environment
from the prior SCB/MSCLP controls. Record missing sections, complete lengths,
differences and relocations without retuning flags or changing selection.
Raw relocation-bearing Pin_Init cannot be called exact until linked target
resolution is accounted for; no linker fitting is authorized by this experiment.

P2-SOURCE-CANDIDATES.md supplies separate C-SKY leads, which require C-SKY
instruction recovery/compiler evidence rather than this GNU Arm candidate.
This task does not conflate those architectures.
