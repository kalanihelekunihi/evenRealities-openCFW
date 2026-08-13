// Find and decompile R1 phone/glasses authentication and pairing evidence.
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

public class R1AuthEvidence extends GhidraScript {
    private static final long[] FUNCTION_ENTRIES = {
        0x33850, // BLE-thread message allocator/queue helper
        0x45184, // BLE-thread event consumer, including pairAuth and advStart
        0x4da28, // phone-role connection-handle assignment
        0x83d04, // system/advStart handler
        0x842ec  // system/pairAuth handler
    };

    private static final String[] TARGETS = {
        "AUTH_DEVICE_PHONE",
        "AUTH_DEVICE_GLASSES",
        "encrypted auth success",
        "encrypted get sec auth flag",
        "encrypted not get sec auth flag",
        "Phone connected, wait glasses auth",
        "CMD_SYSTEM_PAIR_AUTH",
        "ADV_START",
        "glasses BLE pair authentication command",
        "New Bond",
        "whitelist",
        "PM_EVT_CONN_SEC_CONFIG_REQ",
        "EUS notification not enabled"
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();
        for (long raw : FUNCTION_ENTRIES) {
            Address address = toAddr(raw);
            Function function = functions.getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
            }
            println("EXPLICIT_FUNCTION " + address + " " + describe(function));
            if (function != null) {
                queue.add(function);
            }
        }
        for (String target : TARGETS) {
            List<Data> matches = findStrings(target);
            println("\n=== TARGET " + target + " (" + matches.size() + ") ===");
            for (Data data : matches) {
                String value = StringDataInstance.getStringDataInstance(data).getStringValue();
                println("STRING " + data.getAddress() + " " + sanitize(value));
                ReferenceIterator refs = currentProgram.getReferenceManager()
                    .getReferencesTo(data.getAddress());
                while (refs.hasNext()) {
                    Reference ref = refs.next();
                    Function function = functions.getFunctionContaining(ref.getFromAddress());
                    println("REF " + ref.getFromAddress() + " " + ref.getReferenceType()
                        + " CALLER=" + describe(function));
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
