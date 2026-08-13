// Print decoded instructions in a half-open address range.
// Usage: -postScript R1InstructionRangeEvidence.java 0x46650 0x46908
// @category Firmware

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;

public class R1InstructionRangeEvidence extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 2) {
            printerr("Expected start and end-exclusive addresses");
            return;
        }
        Address start = toAddr(Long.decode(arguments[0]));
        Address end = toAddr(Long.decode(arguments[1]));
        if (start.compareTo(end) >= 0 || !currentProgram.getMemory().contains(start)
                || !currentProgram.getMemory().contains(end.subtract(1))) {
            printerr("Invalid or unmapped range " + start + "..." + end);
            return;
        }
        disassemble(start);
        println("INSTRUCTIONS " + start + "..." + end);
        InstructionIterator iterator = currentProgram.getListing().getInstructions(start, true);
        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();
            if (instruction.getAddress().compareTo(end) >= 0) {
                break;
            }
            println(instruction.getAddress() + "  " + instruction);
        }
    }
}
