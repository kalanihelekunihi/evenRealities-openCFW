// SPDX-License-Identifier: GPL-3.0-only
//
// Headless Ghidra helper for reproducible openCFW function-boundary evidence.
// Usage:
//   -postScript DumpFunctionRange.java 0x004751C8 0x00475230

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class DumpFunctionRange extends GhidraScript {
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
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException(
                "could not open current program in decompiler"
            );
        }

        try {
            FunctionIterator functions =
                currentProgram.getFunctionManager().getFunctions(start, true);
            while (functions.hasNext()) {
                Function function = functions.next();
                if (function.getEntryPoint().compareTo(end) >= 0) {
                    break;
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
