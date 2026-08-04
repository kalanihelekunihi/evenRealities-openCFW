// SPDX-License-Identifier: GPL-3.0-only
//
// Create missing Thumb functions at reviewed addresses, then emit
// reproducible bounds, inbound references, and decompilation evidence.
// Usage:
//   -postScript CreateAndDumpFunctions.java 0x00475290 0x00475308

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class CreateAndDumpFunctions extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException(
                "expected one or more function entry addresses"
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

        try {
            for (String argument : arguments) {
                Address entry = toAddr(argument);
                Function function = getFunctionAt(entry);
                if (function == null) {
                    disassemble(entry);
                    function = createFunction(entry, null);
                }
                if (function == null) {
                    println("CREATE_ERROR " + entry);
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
