// Decompile the last few discovered functions before each exact address.
// Useful when Thumb ADR references to an inline string are not represented as data xrefs.
// Usage: -postScript R1NearbyFunctionEvidence.java 0x94f98 0x7025c
// @category Firmware

import java.util.ArrayList;
import java.util.List;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;

public class R1NearbyFunctionEvidence extends GhidraScript {
    private static final long SEARCH_BYTES = 0x800;
    private static final int FUNCTION_LIMIT = 6;

    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            printerr("Expected at least one address");
            return;
        }
        FunctionManager manager = currentProgram.getFunctionManager();
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }
        for (String argument : arguments) {
            Address target = toAddr(Long.decode(argument));
            Address start = target.subtract(Math.min(SEARCH_BYTES, target.getOffset()));
            List<Function> candidates = new ArrayList<>();
            FunctionIterator iterator = manager.getFunctions(start, true);
            while (iterator.hasNext()) {
                Function function = iterator.next();
                if (function.getEntryPoint().compareTo(target) >= 0) {
                    break;
                }
                candidates.add(function);
            }
            int first = Math.max(0, candidates.size() - FUNCTION_LIMIT);
            println("\n=== FUNCTIONS_BEFORE " + target + " ===");
            for (int index = first; index < candidates.size(); index++) {
                Function function = candidates.get(index);
                println("\n--- " + function.getName() + "@" + function.getEntryPoint() + " ---");
                DecompileResults results = decompiler.decompileFunction(function, 90, monitor);
                if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                    println(results.getDecompiledFunction().getC());
                } else {
                    println("DECOMPILE_FAILED: " + results.getErrorMessage());
                }
            }
        }
        decompiler.dispose();
    }
}
