// Recover the production HRV/RMSSD acquisition, filtering, publication, and aggregation path.
// @category Firmware

import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1HRVEvidence extends GhidraScript {
    private static final long[] FUNCTION_ENTRIES = {
        0x49e00, 0x49e5c, 0x49ef4, 0x49f0c, 0x4a24c, 0x4a8bc, 0x4c634,
        0x575d8, 0x5af60, 0x6df60, 0x8a83e
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();

        for (long raw : FUNCTION_ENTRIES) {
            Function function = functions.getFunctionAt(toAddr(raw));
            if (function == null) {
                disassemble(toAddr(raw));
                function = createFunction(toAddr(raw), null);
            }
            println("FUNCTION_ENTRY " + toAddr(raw) + " " + describe(function));
            if (function == null) {
                continue;
            }
            queue.add(function);
            ReferenceIterator callers = currentProgram.getReferenceManager()
                .getReferencesTo(function.getEntryPoint());
            while (callers.hasNext()) {
                Reference ref = callers.next();
                Function caller = functions.getFunctionContaining(ref.getFromAddress());
                println("  CALLER " + ref.getFromAddress() + " " + ref.getReferenceType()
                    + " FUNCTION=" + describe(caller));
                if (caller != null) {
                    queue.add(caller);
                }
            }
        }

        // Scheduling helpers and their literal pools occupy this compact HRV-specific region.
        // Queue every real function boundary so optimization-hidden string references do not make
        // the evidence depend on Ghidra having materialized a particular PARAM xref.
        FunctionIterator scheduling = functions.getFunctions(toAddr(0x49e00), true);
        while (scheduling.hasNext()) {
            Function function = scheduling.next();
            if (function.getEntryPoint().compareTo(toAddr(0x4a24c)) >= 0) {
                break;
            }
            println("SCHEDULING_FUNCTION " + describe(function));
            queue.add(function);
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
