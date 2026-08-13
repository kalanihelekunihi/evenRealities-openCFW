// Ghidra headless helper for the R1 2.2.6.0009 application image.
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
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1Evidence extends GhidraScript {
    private static final String[] TARGETS = {
        "LONG_RELEASE", "DOUBLE_CLICK", "SINGLE_CLICK", "SLIDER_DOWN", "SLIDER_UP",
        "LONG_PRESS", "touch five click", "touch_long_pre_time", "SLIDER_EVENT_ERROR",
        "CMD_SYSTEM_TOUCH_SWITCH", "LIS2DOC", "BMA456", "QMA6100", "IMU ID",
        "PPG ID", "GH3X2X", "Gh3x2xDemo", "raw_ppg", "RMSSD", "RMSSD result",
        "avg_hrv", "last_hrv", "GH_HRV_pre", "algo hrv timing", "health disabled, skip hrv",
        "GXT310",
        "sleep %d-%d", "wake_ratio", "wake_time", "sleep time is small",
        "report sleep data", "gomore sleep force wake",
        "proto report battery status", "battery:%d, voltage:%d, status:%d, type:%d",
        "TEMP1 ID", "TEMP2 ID", "unit: 0.001C", "TOUCH ID", "NFC ID", "PMIC ID",
        "st25dv", "AT^INFO", "AT^DFU", "AT^ACC_OPEN", "AT^HR_OPEN",
        "AT^SPO2_OPEN", "AT^TEMP_OPEN", "AT^HRV_OPEN", "AT^ACTIVITY_READ",
        "factory test", "factory_test", "eAT", "at_system.c", "ble proto rx",
        "EUS", "glasses notification", "phone notification", "vibration", "haptic",
        "motor", "microphone", "audio"
    };

    @Override
    protected void run() throws Exception {
        Listing listing = currentProgram.getListing();
        FunctionManager functions = currentProgram.getFunctionManager();
        Memory memory = currentProgram.getMemory();
        println("PROGRAM=" + currentProgram.getName());
        println("LANGUAGE=" + currentProgram.getLanguageID());
        println("IMAGE_MIN=" + memory.getMinAddress() + " IMAGE_MAX=" + memory.getMaxAddress());
        println("FUNCTION_COUNT=" + functions.getFunctionCount());
        printVector("INITIAL_SP", 0x27000);
        printVector("RESET_VECTOR", 0x27004);

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }

        Set<Function> decompileQueue = new LinkedHashSet<>();
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
                    if (function != null) {
                        decompileQueue.add(function);
                    }
                }
            }
        }

        println("\n=== DECOMPILED REFERENCERS ===");
        for (Function function : decompileQueue) {
            println("\n--- " + describe(function) + " ---");
            DecompileResults results = decompiler.decompileFunction(function, 60, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
                printInstructions(function, listing);
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

    private void printVector(String label, long offset) throws Exception {
        Address address = toAddr(offset);
        long value = Integer.toUnsignedLong(currentProgram.getMemory().getInt(address));
        println(label + "=" + String.format("0x%08x", value));
    }

    private String describe(Function function) {
        if (function == null) {
            return "<none>";
        }
        return function.getName() + "@" + function.getEntryPoint();
    }

    private String sanitize(String value) {
        return value.replace("\r", "\\r").replace("\n", "\\n");
    }

    private void printInstructions(Function function, Listing listing) {
        for (Instruction instruction : listing.getInstructions(function.getBody(), true)) {
            println("  " + instruction.getAddress() + "  " + instruction);
        }
    }
}
