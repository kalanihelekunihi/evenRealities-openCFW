# WsfTrace wrapper for SMP fallback calls

`trace.c` reconstructs WsfTrace at 0x52a63c..0x52a672 for the SMP handler's three register varargs. It allocates a 1024-byte stack buffer, passes format and argument words to an explicit formatting provider, passes the result to an explicit printing provider, asserts when the first print reports at least 1024, and prints the stock newline literal. `g2_smp_candidate_log_fallback` has the handler's callback signature.

The formatter at 0x473036, print/output function at 0x4733ee and WsfAssert at 0x569a44 remain provider boundaries. This source owns the wrapper's control flow and arguments, not printf formatting, output routing or the assertion's effects. Its `context` is a `g2_wsf_trace_providers` struct and needs integration with other SMP provider contexts.

See `g2/analysis/wsf-trace-candidate-20261010/REPORT.md` for comparison results.
