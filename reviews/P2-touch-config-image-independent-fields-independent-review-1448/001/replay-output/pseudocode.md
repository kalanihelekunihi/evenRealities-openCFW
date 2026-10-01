# Configuration builder independent-field checks

This extends packet 1445 with 128 reproducible independently varied context and configuration byte arrays. Every output word is computed from its exact source offsets using a separate explicit arithmetic map retained in replay.py and the fixture records. All 112 output bytes, including unwritten word +52, exact downstream call arguments, final status and frame restoration are checked against original 5378 instructions with original scratch clear A9D4.

52BC and 50E4 remain controlled. These seeded cases supplement the zero/default cases in 1445 and do not exhaust all input combinations. Physical field meanings and downstream effects remain unresolved. No canonical admission or C implementation.
