// Recover production BLE PHY, connection-parameter, advertising, and factory radio controls.
// @category Firmware

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
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

public class R1RadioEvidence extends GhidraScript {
    // Thumb entry points recovered independently from the BLE event dispatch and advertising
    // library. Ghidra did not identify these functions automatically because the image contains
    // inline ADR-addressed strings and several tail calls. Creating them makes the evidence
    // reproducible instead of relying on string presence alone.
    private static final long[] FUNCTION_ENTRIES = {
        0x4cc60, // authenticated target-glasses connected TX power: +6 dBm
        0x4d2f4, // validated SoftDevice PHY-update wrapper
        0x4e150, // reduced/boosted phone, glasses, and advertising TX-power policy
        0x51aa0, // connection-parameter event handler
        0x52b9c, // GAP event handler, including PHY request/update and role selection
        0x72b80, // fast connection classifier: max interval < 50 BLE units
        0x7cbc8  // advertising event handler: mode 3 fast, mode 4 slow
    };

    private static final String[] TARGETS = {
        "Using local preferred PHY",
        "Successfully switched to Coded PHY",
        "PHY update succeeded but not using Coded PHY",
        "Glasses PHY update request",
        "APP PHY update request",
        "request PHY update",
        "Requesting PHY update",
        "glasses_tx_power_set success",
        "phone conn_params update",
        "glasses conn_params update",
        "Fast advertising.",
        "Slow advertising.",
        "AT^BFAST",
        "AT^BSLOW",
        "AT^FASTADV",
        "AT^SLOWADV",
        "AT^STOPADV",
        "AT^BLE_KEEPCONNECT"
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();

        for (long entry : FUNCTION_ENTRIES) {
            Address address = toAddr(entry);
            Function function = functions.getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
            }
            println("EXPLICIT_FUNCTION " + address + " " + describe(function));
            enqueueWithCallers(queue, function, functions);
        }

        for (String target : TARGETS) {
            List<Data> matches = findStrings(target);
            println("\n=== TARGET: " + target + " (" + matches.size() + ") ===");
            for (Data data : matches) {
                String value = StringDataInstance.getStringDataInstance(data).getStringValue();
                println("STRING " + data.getAddress() + " " + sanitize(value));
                ReferenceIterator refs = currentProgram.getReferenceManager()
                    .getReferencesTo(data.getAddress());
                while (refs.hasNext()) {
                    Reference ref = refs.next();
                    Function function = functions.getFunctionContaining(ref.getFromAddress());
                    println("  XREF " + ref.getFromAddress() + " " + ref.getReferenceType()
                        + " FUNCTION=" + describe(function));
                    enqueueWithCallers(queue, function, functions);
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

    private void enqueueWithCallers(
            Set<Function> queue,
            Function function,
            FunctionManager functions) {
        if (function == null || !queue.add(function)) {
            return;
        }
        ReferenceIterator callers = currentProgram.getReferenceManager()
            .getReferencesTo(function.getEntryPoint());
        while (callers.hasNext()) {
            Reference ref = callers.next();
            Function caller = functions.getFunctionContaining(ref.getFromAddress());
            println("    CALLER " + ref.getFromAddress() + " " + ref.getReferenceType()
                + " FUNCTION=" + describe(caller));
            if (caller != null) {
                queue.add(caller);
            }
        }
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
