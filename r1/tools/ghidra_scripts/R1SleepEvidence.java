// Recover sleep-session construction, storage, and reporting evidence.
// @category Firmware

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.StringDataInstance;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1SleepEvidence extends GhidraScript {
    private static final long[] FUNCTION_ENTRIES = {
        0x8acfc, 0x8ada4, 0x8adb4, 0x8da24, 0x8dc94, 0x8dd90,
        0x8f728, 0x8f954, 0x8fa3c
    };

    private static final String[] TARGETS = {
        "sleep %d-%d", "wake_ratio", "wake_time", "sleep time is small",
        "report sleep data", "sleep sync", "sleep data storage", "sleep force awake",
        "gomore sleep force wake"
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
            if (function != null) {
                queue.add(function);
            }
        }

        for (String target : TARGETS) {
            List<Data> matches = findStrings(target);
            println("\n=== TARGET: " + target + " (" + matches.size() + ") ===");
            for (Data data : matches) {
                String value = StringDataInstance.getStringDataInstance(data).getStringValue();
                println("STRING " + data.getAddress() + " " + sanitize(value));
                FunctionIterator precedingFunctions = functions.getFunctions(data.getAddress(), false);
                Function preceding = precedingFunctions.hasNext() ? precedingFunctions.next() : null;
                println("  PRECEDING_FUNCTION=" + describe(preceding));
                if (preceding != null
                        && data.getAddress().subtract(preceding.getEntryPoint()) <= 0x1000) {
                    queue.add(preceding);
                }
                ReferenceIterator refs = currentProgram.getReferenceManager()
                    .getReferencesTo(data.getAddress());
                while (refs.hasNext()) {
                    Reference ref = refs.next();
                    Function function = functions.getFunctionContaining(ref.getFromAddress());
                    println("  XREF " + ref.getFromAddress() + " " + ref.getReferenceType()
                        + " FUNCTION=" + describe(function));
                    if (function != null) {
                        queue.add(function);
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

    private List<Data> findStrings(String needle) {
        List<Data> matches = new ArrayList<>();
        for (Data data : currentProgram.getListing().getDefinedData(true)) {
            if (!data.hasStringValue()) {
                continue;
            }
            String value = StringDataInstance.getStringDataInstance(data).getStringValue();
            if (value != null && value.toLowerCase().contains(needle.toLowerCase())) {
                matches.add(data);
            }
        }
        return matches;
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }

    private String sanitize(String value) {
        return value.replace("\r", "\\r").replace("\n", "\\n");
    }
}
