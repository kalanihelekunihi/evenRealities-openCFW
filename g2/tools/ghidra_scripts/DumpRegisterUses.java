// Report every analyzed instruction that reads or writes a named register.
// @category openCFW

import ghidra.app.script.GhidraScript;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;

public class DumpRegisterUses extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 1) {
            throw new IllegalArgumentException("expected one register name");
        }

        String requested = arguments[0];
        int reads = 0;
        int writes = 0;
        int textual = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext() && !monitor.isCancelled()) {
            Instruction instruction = instructions.next();
            boolean read = containsRegister(instruction.getInputObjects(), requested);
            boolean write = containsRegister(instruction.getResultObjects(), requested);
            boolean text = instruction.toString().toLowerCase()
                .contains(requested.toLowerCase());
            if (!read && !write && !text) {
                continue;
            }

            Function function = getFunctionContaining(instruction.getAddress());
            println("OPENCFW_REGISTER_USE register=" + requested
                + " address=" + instruction.getAddress()
                + " read=" + read
                + " write=" + write
                + " textual=" + text
                + " function=" + (function == null ? "none" : function.getEntryPoint())
                + " instruction=" + instruction);
            if (read) {
                reads += 1;
            }
            if (write) {
                writes += 1;
            }
            if (text) {
                textual += 1;
            }
        }
        println("OPENCFW_REGISTER_USE_SUMMARY register=" + requested
            + " reads=" + reads + " writes=" + writes + " textual=" + textual);
    }

    private boolean containsRegister(Object[] objects, String requested) {
        for (Object object : objects) {
            if (object instanceof Register) {
                Register register = (Register)object;
                if (register.getName().equalsIgnoreCase(requested)
                    || register.getBaseRegister().getName().equalsIgnoreCase(requested)) {
                    return true;
                }
            }
        }
        return false;
    }
}
