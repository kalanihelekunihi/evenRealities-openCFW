// Trace all Ghidra references to one or more runtime-state addresses and decompile their owners.
// Usage: -postScript R1StateReferenceEvidence.java 0x20006ed4 0x2001e454
// @category Firmware

import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1StateReferenceEvidence extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            printerr("Expected at least one runtime-state address");
            return;
        }

        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> owners = new LinkedHashSet<>();
        for (String argument : arguments) {
            Address target = toAddr(Long.decode(argument));
            println("\n=== STATE " + target + " ===");
            ReferenceIterator references =
                currentProgram.getReferenceManager().getReferencesTo(target);
            while (references.hasNext()) {
                Reference reference = references.next();
                Function owner =
                    functions.getFunctionContaining(reference.getFromAddress());
                println(
                    "REF " + reference.getFromAddress() + " "
                        + reference.getReferenceType() + " OWNER=" + describe(owner)
                );
                if (owner != null) {
                    owners.add(owner);
                }
            }
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }
        for (Function function : owners) {
            println("\n--- " + describe(function) + " ---");
            DecompileResults results =
                decompiler.decompileFunction(function, 90, monitor);
            if (results.decompileCompleted()
                    && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        decompiler.dispose();
    }

    private String describe(Function function) {
        return function == null
            ? "<none>"
            : function.getName() + "@" + function.getEntryPoint();
    }
}
