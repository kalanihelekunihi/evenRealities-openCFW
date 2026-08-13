// Recover the production firmware's hidden stress mode, service, and aggregation surfaces.
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

public class R1StressEvidence extends GhidraScript {
    private static final long[] DATA_ADDRESSES = {
        0x42318, 0x4233c, // set stress mode
        0x424cc, 0x424f8, // stress measurement control
        0x429cc, 0x429f4, // service stress point
        0x4b3f8, 0x4b414, // algorithm stress mode unchanged
        0x4b434, 0x4b464, // algorithm stress timer creation
        0x5bdcb, 0x5bdfc, 0x5be20, 0xc58e8 // latest/aggregate stress
    };

    private static final long[] FUNCTION_ENTRIES = {
        0x422c8, // service set-stress-mode wrapper
        0x42474, // service stress-measurement control
        0x42974, // point-result service
        0x49410, // hourly stress timer callback target
        0x4b348, // algorithm stress mode transition
        0x4b48c, // stress mode setter
        0x5bcec  // stress storage/aggregation
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();
        for (long raw : DATA_ADDRESSES) {
            Address target = toAddr(raw);
            println("DATA " + target);
            ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(target);
            while (references.hasNext()) {
                Reference reference = references.next();
                Function function = functions.getFunctionContaining(reference.getFromAddress());
                println("  REF " + reference.getFromAddress() + " " + reference.getReferenceType()
                    + " FUNCTION=" + describe(function));
                if (function != null) {
                    queue.add(function);
                }
            }
        }
        for (long raw : FUNCTION_ENTRIES) {
            Function function = functions.getFunctionAt(toAddr(raw));
            if (function == null) {
                disassemble(toAddr(raw));
                function = createFunction(toAddr(raw), null);
            }
            println("FUNCTION " + toAddr(raw) + " " + describe(function));
            if (function != null) {
                queue.add(function);
                ReferenceIterator references = currentProgram.getReferenceManager()
                    .getReferencesTo(function.getEntryPoint());
                while (references.hasNext()) {
                    Reference reference = references.next();
                    Function caller = functions.getFunctionContaining(reference.getFromAddress());
                    println("  CALLER " + reference.getFromAddress() + " "
                        + reference.getReferenceType() + " FUNCTION=" + describe(caller));
                    if (caller != null) {
                        queue.add(caller);
                    }
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
        for (Function function : queue) {
            println("\n--- " + describe(function) + " ---");
            DecompileResults results = decompiler.decompileFunction(function, 90, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        decompiler.dispose();
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
