// Decompile every discovered function whose entry falls in an inclusive address range.
// Usage: -postScript R1FunctionRangeEvidence.java 0x4f000 0x4f800
// @category Firmware

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

public class R1FunctionRangeEvidence extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 2) {
            printerr("Expected inclusive start and end addresses");
            return;
        }
        Address start = toAddr(Long.decode(arguments[0]));
        Address end = toAddr(Long.decode(arguments[1]));
        if (start.compareTo(end) > 0 || !currentProgram.getMemory().contains(start)
                || !currentProgram.getMemory().contains(end)) {
            printerr("Invalid or unmapped range " + start + "..." + end);
            return;
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }

        FunctionIterator iterator = currentProgram.getFunctionManager().getFunctions(start, true);
        int count = 0;
        while (iterator.hasNext()) {
            Function function = iterator.next();
            if (function.getEntryPoint().compareTo(end) > 0) {
                break;
            }
            count++;
            println("\n--- " + function.getName() + "@" + function.getEntryPoint() + " ---");
            DecompileResults results = decompiler.decompileFunction(function, 90, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        println("\nFUNCTION_COUNT " + count);
        decompiler.dispose();
    }
}
