// Report direct Ghidra references and containing functions for fixed targets.
// @category openCFW

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.LinkedHashSet;
import java.util.Set;

public class DumpReferencesTo extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException("expected at least one target address");
        }

        Set<Function> functions = new LinkedHashSet<>();
        for (String argument : arguments) {
            Address target = toAddr(argument);
            int count = 0;
            ReferenceIterator references = currentProgram.getReferenceManager()
                .getReferencesTo(target);
            while (references.hasNext()) {
                Reference reference = references.next();
                Function function = getFunctionContaining(reference.getFromAddress());
                println("OPENCFW_REFERENCE target=" + target
                    + " from=" + reference.getFromAddress()
                    + " type=" + reference.getReferenceType()
                    + " function=" + (function == null ? "none" : function.getEntryPoint()));
                if (function != null) {
                    functions.add(function);
                }
                count += 1;
            }
            println("OPENCFW_REFERENCE_SUMMARY target=" + target + " count=" + count);
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        decompiler.setSimplificationStyle("decompile");
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException("could not open program in decompiler");
        }
        try {
            for (Function function : functions) {
                DecompileResults results = decompiler.decompileFunction(function, 60, monitor);
                if (!results.decompileCompleted()) {
                    throw new IllegalStateException(results.getErrorMessage());
                }
                println("OPENCFW_REFERENCE_DECOMPILE_BEGIN " + function.getEntryPoint());
                println(results.getDecompiledFunction().getC());
                println("OPENCFW_REFERENCE_DECOMPILE_END " + function.getEntryPoint());
            }
        }
        finally {
            decompiler.dispose();
        }
    }
}
