// Recover native touch-event construction and slider metadata evidence.
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

public class R1TouchEvidence extends GhidraScript {
    private static final long[] FUNCTION_ENTRIES = {
        0x3e938, 0x59aac, 0x8e6a0, 0x92cbc, 0x93424
    };

    // Every little-endian occurrence of the production touch-state pointer 0x20016a60 in the
    // application image. Literal pools are not functions, so use only their preceding function.
    private static final long[] TOUCH_STATE_POINTER_LITERALS = {
        0x3ebec, 0x59b9c, 0x8ea04, 0x92cb8, 0x930d8, 0x934d8
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();

        // These addresses contain the literal pointer bytes, never function prologues. Removing a
        // scratch-project misdefinition makes repeated evidence runs deterministic.
        for (long raw : TOUCH_STATE_POINTER_LITERALS) {
            if (functions.getFunctionAt(toAddr(raw)) != null) {
                functions.removeFunction(toAddr(raw));
            }
        }

        for (long raw : FUNCTION_ENTRIES) {
            Function function = functions.getFunctionAt(toAddr(raw));
            if (function == null) {
                disassemble(toAddr(raw));
                function = createFunction(toAddr(raw), null);
            }
            println("FUNCTION_ENTRY " + toAddr(raw) + " " + describe(function));
            if (function != null) {
                queue.add(function);
                addCallers(functions, function, queue);
            }
        }

        for (long raw : TOUCH_STATE_POINTER_LITERALS) {
            // Start one byte before the literal so an accidental function definition on data in a
            // scratch project cannot hide the real preceding code function.
            FunctionIterator precedingFunctions = functions.getFunctions(toAddr(raw).subtract(1), false);
            Function preceding = precedingFunctions.hasNext() ? precedingFunctions.next() : null;
            println("POINTER_LITERAL " + toAddr(raw) + " PRECEDING=" + describe(preceding));
            if (preceding != null && toAddr(raw).subtract(preceding.getEntryPoint()) <= 0x1000) {
                queue.add(preceding);
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

    private void addCallers(
        FunctionManager functions,
        Function function,
        Set<Function> queue
    ) {
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

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
