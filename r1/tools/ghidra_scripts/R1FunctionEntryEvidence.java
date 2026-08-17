// Create if necessary and decompile exact function-entry addresses.
// Usage: -postScript R1FunctionEntryEvidence.java 0x55181 0x55279
// @category Firmware

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1FunctionEntryEvidence extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            printerr("Expected at least one function-entry address");
            return;
        }
        FunctionManager functions = currentProgram.getFunctionManager();
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }
        for (String argument : arguments) {
            Address address = toAddr(Long.decode(argument));
            Function function = functions.getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
            }
            println("\n--- " + (function == null ? "<none>" :
                function.getName() + "@" + function.getEntryPoint()) + " ---");
            printReferences(functions, address, "REF");
            printReferences(functions, address.add(1), "THUMB_REF");
            if (function == null) {
                continue;
            }
            println("BODY min=" + function.getBody().getMinAddress()
                + " max=" + function.getBody().getMaxAddress()
                + " bytes=" + function.getBody().getNumAddresses()
                + " ranges=" + function.getBody().getNumAddressRanges());
            DecompileResults results = decompiler.decompileFunction(function, 90, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        decompiler.dispose();
    }

    private void printReferences(FunctionManager functions, Address address, String label) {
        ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(address);
        while (references.hasNext()) {
            Reference reference = references.next();
            Function caller = functions.getFunctionContaining(reference.getFromAddress());
            println(label + " " + reference.getFromAddress() + " "
                + reference.getReferenceType() + " CALLER="
                + (caller == null ? "<none>" : caller.getName() + "@" + caller.getEntryPoint()));
        }
    }
}
