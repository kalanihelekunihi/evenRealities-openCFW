// Exhaustively seed every aligned ARCompact instruction in a bounded range.
// This is intended for small discovery gaps, not for indiscriminate whole-image use.
// @category openCFW

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;

public class DisassembleArcompactRange extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 2) {
            throw new IllegalArgumentException("expected start end-exclusive");
        }

        Address start = toAddr(arguments[0]);
        Address end = toAddr(arguments[1]);
        if ((start.getOffset() & 1) != 0 || (end.getOffset() & 1) != 0
            || start.compareTo(end) >= 0) {
            throw new IllegalArgumentException("range must be non-empty and halfword-aligned");
        }
        Memory memory = currentProgram.getMemory();
        if (!memory.contains(start) || !memory.contains(end.subtract(1))) {
            throw new IllegalArgumentException("range is not fully mapped");
        }

        int attempted = 0;
        int seeded = 0;
        for (Address cursor = start;
             cursor.compareTo(end) < 0 && !monitor.isCancelled();
             cursor = cursor.add(2)) {
            Instruction containing = currentProgram.getListing().getInstructionContaining(cursor);
            if (containing != null) {
                continue;
            }
            attempted += 1;
            if (disassemble(cursor)) {
                seeded += 1;
            }
        }
        println("OPENCFW_ARC_RANGE_SUMMARY start=" + start + " end=" + end
            + " attempted=" + attempted + " seeded=" + seeded);
    }
}
