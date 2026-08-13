// Decompile analyzed functions by exact symbol name.
// @category openCFW

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

public class DumpNamedFunctionDecomp extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException("expected at least one exact function name");
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        decompiler.setSimplificationStyle("decompile");
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException("could not open program in decompiler");
        }
        try {
            for (String wanted : arguments) {
                Function match = null;
                FunctionIterator functions =
                    currentProgram.getFunctionManager().getFunctions(true);
                while (functions.hasNext()) {
                    Function candidate = functions.next();
                    if (candidate.getName().equals(wanted)) {
                        if (match != null) {
                            throw new IllegalStateException(
                                "function name is not unique: " + wanted
                            );
                        }
                        match = candidate;
                    }
                }
                if (match == null) {
                    throw new IllegalStateException("function is missing: " + wanted);
                }
                DecompileResults result = decompiler.decompileFunction(match, 120, monitor);
                if (!result.decompileCompleted()) {
                    throw new IllegalStateException(result.getErrorMessage());
                }
                println(
                    "OPENCFW_NAMED_DECOMPILE_BEGIN name=" + wanted +
                    " entry=" + match.getEntryPoint()
                );
                println(result.getDecompiledFunction().getC());
                println("OPENCFW_NAMED_DECOMPILE_END name=" + wanted);
            }
        }
        finally {
            decompiler.dispose();
        }
    }
}
