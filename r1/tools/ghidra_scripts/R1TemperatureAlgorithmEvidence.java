// Recover stock algorithm-temperature callback and dual-sensor result evidence.
// @category Firmware

import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1TemperatureAlgorithmEvidence extends GhidraScript {
    private static final long[] DATA_ADDRESSES = {
        0x4b9f0, // [RING]algo temp once result: temp:%d
        0x4ba20, // same, short log form
        0xc07e4, // dual-sensor result log
        0xc0830, // same, short log form
        0xbf668, // factory dual-sensor output with explicit 0.001C unit
        0x6f59c, // GXT310 ID probe result
        0x6f6b8, // GXT310 mode-switch failure
        0x6f798  // GXT310 one-shot trigger failure
    };

    private static final long[] FUNCTION_ENTRIES = {
        0x4b4b0, // five-sample temperature reducer/publisher
        0x4b5b0, // sleep-session temperature-history robust reducer
        0x4b560, // temperature range gate
        0x4b598, // temperature result-validity gate
        0x4b718, // algorithm temperature mode transition
        0x4b920, // one-shot temperature callback
        0x4bad0, // sleep-status subscriber/history lifecycle
        0x50ecc, // dual-ID probe lifecycle
        0x50f9c, // enable both GXT310 channels
        0x510d8, // two-channel ID response builder
        0x51108, // ten-sample trimmed/calibrated result builder
        0x51260, // immediate two-channel sample builder
        0x6f53c, // shared ID-register read
        0x6f600, // shared signed-temperature conversion
        0x6f648, // shared continuous/shutdown config write
        0x6f738, // shared one-shot trigger write
        0x6f818, // X0 one-shot wrapper
        0x6f832  // X2 one-shot wrapper
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();

        for (long raw : DATA_ADDRESSES) {
            Address target = toAddr(raw);
            println("DATA " + target);
            FunctionIterator precedingFunctions = functions.getFunctions(target, false);
            Function preceding = precedingFunctions.hasNext() ? precedingFunctions.next() : null;
            println("  PRECEDING_FUNCTION=" + describe(preceding));
            if (preceding != null) {
                queue.add(preceding);
            }
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
                addCallers(functions, function, queue);
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

    private void addCallers(
            FunctionManager functions,
            Function function,
            Set<Function> queue) {
        ReferenceIterator callers = currentProgram.getReferenceManager()
            .getReferencesTo(function.getEntryPoint());
        while (callers.hasNext()) {
            Reference reference = callers.next();
            Function caller = functions.getFunctionContaining(reference.getFromAddress());
            println("  CALLER " + reference.getFromAddress() + " " + reference.getReferenceType()
                + " FUNCTION=" + describe(caller));
            if (caller != null) {
                queue.add(caller);
            }
        }
    }
}
