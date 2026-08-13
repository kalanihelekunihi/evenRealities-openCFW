// Print bounded instruction context for every call/jump reference to an exact function address.
// Usage: -postScript R1CallsiteEvidence.java 0x49410
// @category Firmware

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1CallsiteEvidence extends GhidraScript {
    private static final int PRECEDING_INSTRUCTION_COUNT = 10;

    @Override
    protected void run() throws Exception {
        if (getScriptArgs().length != 1) {
            printerr("Expected one target function address");
            return;
        }
        Address target = toAddr(Long.decode(getScriptArgs()[0]));
        FunctionManager functions = currentProgram.getFunctionManager();
        ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(target);
        int count = 0;
        while (references.hasNext()) {
            Reference reference = references.next();
            Address callAddress = reference.getFromAddress();
            Function function = functions.getFunctionContaining(callAddress);
            println("\nCALLSITE " + callAddress + " " + reference.getReferenceType()
                + " FUNCTION=" + describe(function));

            List<Instruction> context = new ArrayList<>();
            Instruction instruction = currentProgram.getListing().getInstructionAt(callAddress);
            Instruction cursor = instruction;
            for (int index = 0; index < PRECEDING_INSTRUCTION_COUNT && cursor != null; index++) {
                context.add(cursor);
                cursor = cursor.getPrevious();
            }
            Collections.reverse(context);
            for (Instruction item : context) {
                println("  " + item.getAddress() + "  " + item.toString());
            }
            count++;
        }
        println("\nCALLSITE_COUNT " + count);
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
