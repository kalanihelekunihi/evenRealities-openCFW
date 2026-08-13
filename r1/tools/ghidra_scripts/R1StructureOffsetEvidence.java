// Report instructions whose rendered operands contain one of the requested
// structure displacements, together with their containing/preceding function.
// This is intentionally a triage aid: ARM/Thumb structure accesses may use a
// pre-adjusted substructure pointer, so absence is not proof of no access.
// Usage: -postScript R1StructureOffsetEvidence.java 0x180 0x2de 0x308
// @category Firmware

import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;

public class R1StructureOffsetEvidence extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            printerr("Expected at least one hexadecimal displacement");
            return;
        }

        Listing listing = currentProgram.getListing();
        FunctionManager functions = currentProgram.getFunctionManager();
        for (String argument : arguments) {
            long value = Long.decode(argument);
            Set<String> needles = new LinkedHashSet<>();
            needles.add("#0x" + Long.toHexString(value));
            needles.add("#" + Long.toString(value));

            println("OFFSET 0x" + Long.toHexString(value));
            int count = 0;
            InstructionIterator iterator = listing.getInstructions(true);
            while (iterator.hasNext() && !monitor.isCancelled()) {
                Instruction instruction = iterator.next();
                boolean match = false;
                for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
                    String rendered = instruction.getDefaultOperandRepresentation(operand).toLowerCase();
                    for (String needle : needles) {
                        if (rendered.equals(needle) || rendered.contains("[" + needle)
                            || rendered.contains("," + needle)
                            || rendered.contains(", " + needle)) {
                            match = true;
                            break;
                        }
                    }
                    if (match) {
                        break;
                    }
                }
                if (!match) {
                    continue;
                }

                Address address = instruction.getAddress();
                Function containing = functions.getFunctionContaining(address);
                FunctionIterator previous = functions.getFunctions(address, false);
                Function preceding = previous.hasNext() ? previous.next() : null;
                println("  " + address + " " + instruction + " CONTAINING="
                    + describe(containing) + " PRECEDING=" + describe(preceding));
                count++;
            }
            println("COUNT " + count);
        }
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
