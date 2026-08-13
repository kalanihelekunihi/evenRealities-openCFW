// List every call/jump reference to one or more exact function addresses.
// Usage: -postScript R1MultiCallsiteEvidence.java 0x60990 0x8245c
// @category Firmware

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1MultiCallsiteEvidence extends GhidraScript {
    @Override
    protected void run() throws Exception {
        if (getScriptArgs().length == 0) {
            printerr("Expected at least one target function address");
            return;
        }
        FunctionManager functions = currentProgram.getFunctionManager();
        for (String argument : getScriptArgs()) {
            Address target = toAddr(Long.decode(argument));
            ReferenceIterator references = currentProgram.getReferenceManager()
                .getReferencesTo(target);
            int count = 0;
            println("\nTARGET " + target);
            while (references.hasNext()) {
                Reference reference = references.next();
                if (!reference.getReferenceType().isCall()
                        && !reference.getReferenceType().isJump()) {
                    continue;
                }
                Function caller = functions.getFunctionContaining(reference.getFromAddress());
                println("CALLSITE " + reference.getFromAddress() + " "
                    + reference.getReferenceType() + " FUNCTION=" + describe(caller));
                count++;
            }
            println("CALLSITE_COUNT " + count);
        }
    }

    private String describe(Function function) {
        return function == null ? "<none>"
            : function.getName() + "@" + function.getEntryPoint();
    }
}
