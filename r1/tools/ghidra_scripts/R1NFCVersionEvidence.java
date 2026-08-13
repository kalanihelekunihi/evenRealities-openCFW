// Locate and decompile the NFC mailbox path from strings and optional known function entries.
// Usage: -postScript R1NFCVersionEvidence.java 0x78404
// @category Firmware

import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.StringDataInstance;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1NFCVersionEvidence extends GhidraScript {
    private static final String[] TARGETS = {
        "nfc_st25dvxxkc_init failed",
        "mailbox free or empty",
        "nfc_protocol_control_dock_adv"
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();

        for (String argument : getScriptArgs()) {
            Address address = toAddr(Long.decode(argument));
            Function function = functions.getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
            }
            println("SEED address=" + address + " caller=" + describe(function));
            if (function != null) {
                addWithCallers(queue, function, functions);
            }
        }

        for (Data data : currentProgram.getListing().getDefinedData(true)) {
            String value = StringDataInstance.getStringDataInstance(data).getStringValue();
            if (value == null || !containsTarget(value)) {
                continue;
            }
            println("STRING address=" + data.getAddress() + " value=" + sanitize(value));
            ReferenceIterator refs = currentProgram.getReferenceManager()
                .getReferencesTo(data.getAddress());
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function function = functions.getFunctionContaining(ref.getFromAddress());
                println("  REF from=" + ref.getFromAddress() + " caller=" + describe(function));
                if (function != null) {
                    addWithCallers(queue, function, functions);
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
            println("\n=== FUNCTION " + describe(function) + " ===");
            DecompileResults results = decompiler.decompileFunction(function, 90, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        decompiler.dispose();
    }

    private boolean containsTarget(String value) {
        for (String target : TARGETS) {
            if (value.contains(target)) {
                return true;
            }
        }
        return false;
    }

    private void addWithCallers(Set<Function> queue, Function function, FunctionManager functions) {
        if (!queue.add(function)) {
            return;
        }
        ReferenceIterator refs = currentProgram.getReferenceManager()
            .getReferencesTo(function.getEntryPoint());
        while (refs.hasNext()) {
            Function caller = functions.getFunctionContaining(refs.next().getFromAddress());
            if (caller != null) {
                queue.add(caller);
            }
        }
    }

    private String sanitize(String value) {
        return value.replace("\n", "\\n").replace("\r", "\\r");
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
