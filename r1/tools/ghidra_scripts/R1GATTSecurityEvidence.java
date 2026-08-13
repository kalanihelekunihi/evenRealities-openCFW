// Recover the production custom-service registration and Peer Manager security policy.
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
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1GATTSecurityEvidence extends GhidraScript {
    private static final long CUSTOM_SERVICE_BASE_UUID = 0x991a0;
    private static final long[] FUNCTION_ENTRIES = {
        // Custom service registration, characteristic_add wrapper and PM security initialization.
        0x529bc, 0x579a8, 0x4e4b4,
        // Peer Manager event and initialization callbacks recovered around the embedded log pool.
        0x7f2b0, 0x7fa5c,
        // Custom notification helper and app-facing pair-auth handler.
        0x526cc, 0x842ec
    };
    private static final String[] TARGETS = {
        "PM_EVT_CONN_SEC_CONFIG_REQ",
        "New Bond, add the peer to the whitelist",
        "This is a new device connecting for the first time",
        "encrypted get sec auth flag",
        "encrypted not get sec auth flag",
        "EUS notification not enabled",
        "BLE_GAP_SEC_STATUS",
        "passkey",
        "bonding"
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();

        println("CUSTOM_SERVICE_BASE_UUID " + toAddr(CUSTOM_SERVICE_BASE_UUID)
            + " RAW_LE=" + readHex(CUSTOM_SERVICE_BASE_UUID, 16));
        // Ghidra treats the SoftDevice SVC inside 0x529bc as terminating control flow and removes
        // the four following characteristic_add calls from its C output. Preserve the raw Thumb
        // instruction stream so the service initializer remains independently reproducible.
        dumpInstructions(0x529bc, 0x52b28);
        addReferencesTo(toAddr(CUSTOM_SERVICE_BASE_UUID), "UUID_REF", functions, queue);

        for (long raw : FUNCTION_ENTRIES) {
            Function function = functions.getFunctionAt(toAddr(raw));
            if (function == null) {
                disassemble(toAddr(raw));
                function = createFunction(toAddr(raw), null);
            }
            println("FUNCTION_ENTRY " + toAddr(raw) + " " + describe(function));
            if (function != null) {
                queue.add(function);
                addReferencesTo(function.getEntryPoint(), "CALLER", functions, queue);
            }
        }

        for (String target : TARGETS) {
            List<Data> matches = findStrings(target);
            println("\n=== TARGET " + target + " (" + matches.size() + ") ===");
            for (Data data : matches) {
                String value = StringDataInstance.getStringDataInstance(data).getStringValue();
                println("STRING " + data.getAddress() + " " + sanitize(value));
                addReferencesTo(data.getAddress(), "STRING_REF", functions, queue);
                // Several compiler literal pools point to strings while Ghidra records the pool as
                // data rather than a code xref. Keep the nearest preceding bounded function too.
                FunctionIterator iterator = functions.getFunctions(data.getAddress(), false);
                if (iterator.hasNext()) {
                    Function preceding = iterator.next();
                    long distance = data.getAddress().subtract(preceding.getEntryPoint());
                    if (distance >= 0 && distance <= 0x1200) {
                        println("  PRECEDING " + describe(preceding) + " DISTANCE=0x"
                            + Long.toHexString(distance));
                        queue.add(preceding);
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
            DecompileResults results = decompiler.decompileFunction(function, 120, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        decompiler.dispose();
    }

    private void addReferencesTo(ghidra.program.model.address.Address address, String label,
            FunctionManager functions, Set<Function> queue) {
        ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(address);
        while (refs.hasNext()) {
            Reference ref = refs.next();
            Function function = functions.getFunctionContaining(ref.getFromAddress());
            println("  " + label + " " + ref.getFromAddress() + " " + ref.getReferenceType()
                + " FUNCTION=" + describe(function));
            if (function != null) {
                queue.add(function);
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

    private String readHex(long address, int length) throws Exception {
        Memory memory = currentProgram.getMemory();
        byte[] bytes = new byte[length];
        int count = memory.getBytes(toAddr(address), bytes);
        if (count != length) {
            throw new IllegalStateException("short read at " + toAddr(address));
        }
        StringBuilder result = new StringBuilder(length * 3 - 1);
        for (int i = 0; i < length; i++) {
            if (i != 0) {
                result.append(' ');
            }
            result.append(String.format("%02x", bytes[i] & 0xff));
        }
        return result.toString();
    }

    private void dumpInstructions(long start, long endInclusive) throws Exception {
        println("\n=== CUSTOM SERVICE THUMB INSTRUCTIONS " + toAddr(start) + ".."
            + toAddr(endInclusive) + " ===");
        Instruction instruction = currentProgram.getListing().getInstructionAt(toAddr(start));
        while (instruction != null
                && instruction.getAddress().compareTo(toAddr(endInclusive)) <= 0) {
            println(instruction.getAddress() + "  " + instruction);
            instruction = instruction.getNext();
        }
    }
}
