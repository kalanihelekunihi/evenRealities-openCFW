// Deterministic headless Ghidra function decompilation helper for openCFW.
// @category openCFW

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class DumpFunctionDecomp extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException("expected at least one function address");
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        decompiler.setSimplificationStyle("decompile");
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException("could not open program in decompiler");
        }
        try {
            for (String argument : arguments) {
                Address entry = toAddr(argument);
                Function function = getFunctionAt(entry);
                if (function == null) {
                    disassemble(entry);
                    function = createFunction(entry, "open_cfw_target_" + argument);
                }
                if (function == null) {
                    throw new IllegalStateException("could not create function at " + entry);
                }

                DecompileResults results = decompiler.decompileFunction(function, 60, monitor);
                if (!results.decompileCompleted()) {
                    throw new IllegalStateException(results.getErrorMessage());
                }
                println("OPENCFW_DECOMPILE_BEGIN " + entry);
                println(results.getDecompiledFunction().getC());
                println("OPENCFW_DECOMPILE_END " + entry);
            }
        }
        finally {
            decompiler.dispose();
        }
    }
}
