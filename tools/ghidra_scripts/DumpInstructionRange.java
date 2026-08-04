// SPDX-License-Identifier: GPL-3.0-only
//
// Emit exact instruction bytes and decoded text for a reviewed address range.
// Usage:
//   -postScript DumpInstructionRange.java 0x00475C1A 0x00475D5E

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;

public class DumpInstructionRange extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 2) {
            throw new IllegalArgumentException(
                "expected inclusive start and exclusive end addresses"
            );
        }

        Address start = toAddr(arguments[0]);
        Address end = toAddr(arguments[1]);
        InstructionIterator instructions =
            currentProgram.getListing().getInstructions(start, true);

        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            if (instruction.getAddress().compareTo(end) >= 0) {
                break;
            }

            byte[] bytes = instruction.getBytes();
            StringBuilder encoded = new StringBuilder();
            for (byte value : bytes) {
                encoded.append(String.format("%02x", value & 0xff));
            }
            println(
                instruction.getAddress() + " " +
                encoded + " " +
                instruction
            );
        }
    }
}
