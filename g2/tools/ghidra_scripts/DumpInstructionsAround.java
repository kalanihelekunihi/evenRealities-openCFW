// Dump analyzed instructions in a bounded byte window around fixed addresses.
// @category openCFW

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;

public class DumpInstructionsAround extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length < 2) {
            throw new IllegalArgumentException("expected context-bytes address [address ...]");
        }
        long context = Long.decode(arguments[0]);
        if (context < 0) {
            throw new IllegalArgumentException("context must be non-negative");
        }

        for (int index = 1; index < arguments.length; ++index) {
            Address target = toAddr(arguments[index]);
            Address start = target.subtract(context);
            Address end = target.add(context);
            println("OPENCFW_INSTRUCTION_WINDOW_BEGIN target=" + target
                + " start=" + start + " end=" + end);
            InstructionIterator instructions = currentProgram.getListing()
                .getInstructions(new AddressSet(start, end), true);
            int count = 0;
            while (instructions.hasNext()) {
                Instruction instruction = instructions.next();
                println("OPENCFW_INSTRUCTION address=" + instruction.getAddress()
                    + " length=" + instruction.getLength()
                    + " text=" + instruction);
                count += 1;
            }
            println("OPENCFW_INSTRUCTION_WINDOW_END target=" + target
                + " count=" + count);
        }
    }
}
