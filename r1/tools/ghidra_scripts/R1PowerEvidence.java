// Recover battery, charge-state, and charging-dock evidence.
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

public class R1PowerEvidence extends GhidraScript {
    private static final long[] FUNCTION_ENTRIES = {
        0x8345c, 0x83896, 0x7ba24, 0x7bac4, 0x7bb44, 0x7bb7c, 0x7bb94,
        0x7bbbc, 0x7bbc0, 0x91270, 0x91290,
        // PMIC/charge state, current-sense, power-off, raw register and event-facing helpers.
        0x35268, 0x35272, 0x3529a, 0x3530c, 0x3540c, 0x3541c, 0x3543c,
        0x35508, 0x355bc, 0x35760,
        0x4ee18, 0x4f4a4, 0x4f4d4, 0x4f524,
        0x50614, 0x5061c, 0x506a4, 0x50708, 0x50748, 0x5074c, 0x50750, 0x50758,
        0x50778, 0x5079c, 0x507cc, 0x50804,
        // Scatter-loaded logical state-command operations table immediately before the GPIO
        // descriptor, plus the current-sense ADC operations table used for comparison.
        0x55204, 0x55230, 0x55254, 0x55390, 0x553e4, 0x554e4, 0x55518,
        0x5574c, 0x558f8, 0x55988, 0x55a94, 0x55ad2, 0x55b68, 0x55b94,
        0x55c50, 0x55c98, 0x55ec4, 0x55f5c, 0x56040, 0x5608e, 0x560dc, 0x56202,
        0x5c0fa,
        0x56568, 0x5657c, 0x56590, 0x5660c,
        0x547f4, 0x54864, 0x548f0, 0x5493c,
        0x54af0,
        // Scatter-loaded device_stacmd driver vtable callbacks (Thumb pointers at record
        // 0x200075c4). These have no flash xrefs until the startup image is decompressed.
        0x7902c, 0x790aa, 0x7910c, 0x791e4, 0x79408, 0x794ac, 0x7a6fc,
        0x79e00, 0x79e10, 0x79e24, 0x79e34,
        0x7aeac, 0x7af38, 0x7af7c, 0x7b090, 0x7b150,
        0x85d58,
        0x77ce4, 0x77cfc, 0x77d14
    };

    private static final String[] TARGETS = {
        "proto report battery status", "battery:%d, voltage:%d, status:%d, type:%d",
        "PMIC_CHARGED_NOT", "NFC_CHARGE_EVENT_NOT_CHARGING",
        "NFC_CHARGE_EVENT_CHARGING_BATTERY_UPDATA", "nfc_charge",
        "charging dock version", "charging dock hw", "pmic_isns_voltage",
        "at_pmic_power_off", "pmic_register_read", "PMIC ID", "ship_mode_en",
        "touch_ldo_en", "pmic_irq", "device_stacmd", "YHM2710"
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
                        && data.getAddress().subtract(preceding.getEntryPoint()) <= 0x1800) {
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
