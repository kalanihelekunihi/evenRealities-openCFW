// Print every reference to one or more exact addresses and its containing function.
// Usage: -postScript R1ReferenceEvidence.java 0x8e7ac 0x20006808
// @category Firmware

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1ReferenceEvidence extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            printerr("Expected at least one address");
            return;
        }
        FunctionManager functions = currentProgram.getFunctionManager();
        for (String argument : arguments) {
            Address target = toAddr(Long.decode(argument));
            println("REFERENCES_TO " + target);
            ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(target);
            int count = 0;
            while (references.hasNext()) {
                Reference reference = references.next();
                Function function = functions.getFunctionContaining(reference.getFromAddress());
                println("  " + reference.getFromAddress() + " " + reference.getReferenceType()
                    + " FUNCTION=" + (function == null ? "<none>" :
                        function.getName() + "@" + function.getEntryPoint()));
                count++;
            }
            println("REFERENCE_COUNT " + count);
        }
    }
}
