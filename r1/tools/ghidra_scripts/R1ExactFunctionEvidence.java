// Decompile the function containing each exact address, or the function whose entry matches it.
// Usage: -postScript R1ExactFunctionEvidence.java 0x4a8c8 0x6c294
// @category Firmware

import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;

public class R1ExactFunctionEvidence extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            printerr("Expected at least one function or interior address");
            return;
        }

        FunctionManager manager = currentProgram.getFunctionManager();
        Set<Function> functions = new LinkedHashSet<>();
        for (String argument : arguments) {
            Address address = toAddr(Long.decode(argument));
            Function function = manager.getFunctionAt(address);
            if (function == null) {
                function = manager.getFunctionContaining(address);
            }
            if (function == null) {
                println("NO_FUNCTION " + address);
            } else {
                functions.add(function);
            }
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }
        for (Function function : functions) {
            println("\n--- " + function.getName() + "@" + function.getEntryPoint() + " ---");
            println(
                "BODY " + function.getBody().getMinAddress() + ".."
                    + function.getBody().getMaxAddress() + " SIZE="
                    + function.getBody().getNumAddresses()
            );
            DecompileResults results = decompiler.decompileFunction(function, 90, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        decompiler.dispose();
    }
}
