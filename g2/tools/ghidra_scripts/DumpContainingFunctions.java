// SPDX-License-Identifier: MIT
//
// Emit bounds, inbound references, and decompilation for every function
// containing one of the supplied addresses.
// Usage:
//   -postScript DumpContainingFunctions.java 0x00444F50 0x0046DCF4

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import java.util.HashSet;
import java.util.Set;

public class DumpContainingFunctions extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException(
                "expected one or more contained addresses"
            );
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException(
                "could not open current program in decompiler"
            );
        }

        Set<Address> emitted = new HashSet<Address>();
        try {
            for (String argument : arguments) {
                Address contained = toAddr(argument);
                Function function = getFunctionContaining(contained);
                if (function == null) {
                    println("NO_FUNCTION " + contained);
                    continue;
                }
                if (!emitted.add(function.getEntryPoint())) {
                    continue;
                }

                println(
                    "FUNCTION " + function.getEntryPoint() +
                    " " + function.getBody().getMinAddress() +
                    " " + function.getBody().getMaxAddress() +
                    " " + function.getName()
                );

                ReferenceIterator references =
                    currentProgram.getReferenceManager().getReferencesTo(
                        function.getEntryPoint()
                    );
                while (references.hasNext()) {
                    Reference reference = references.next();
                    println(
                        "REFERENCE " + reference.getFromAddress() +
                        " " + reference.getReferenceType()
                    );
                }

                DecompileResults result = decompiler.decompileFunction(
                    function,
                    60,
                    monitor
                );
                if (!result.decompileCompleted()) {
                    println("DECOMPILE_ERROR " + result.getErrorMessage());
                    continue;
                }
                println("DECOMPILE_BEGIN");
                println(result.getDecompiledFunction().getC());
                println("DECOMPILE_END");
            }
        }
        finally {
            decompiler.dispose();
        }
    }
}
