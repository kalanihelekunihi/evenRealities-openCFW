// Recover internal health-event publication, storage, and aggregation consumers.
// @category Firmware

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1HealthEventEvidence extends GhidraScript {
    private static final long DATA_LOAD_ADDRESS = 0xc4610;
    private static final long DATA_RUNTIME_ADDRESS = 0x200064a8L;
    private static final int DATA_RUNTIME_LENGTH = 0x195c;
    // These are the exact literal bases loaded by dispatcher 0x8d888. Sensor dispatch indexes
    // `base + id * 4 - 4`, so its first reported ID is the null slot at base. System/storage
    // dispatch indexes `base + (id - familyBase) * 4 + 4`; their base words are sentinels and
    // their first real event slots begin one word later.
    private static final long SENSOR_EVENT_DISPATCH_BASE = 0x20006750L;
    private static final long SYSTEM_EVENT_DISPATCH_BASE = 0x20006e54L;
    private static final long STORAGE_EVENT_DISPATCH_BASE = 0x200066fcL;

    private static final long[] DATA_ADDRESSES = {
        0x5ae6f, 0x5ae9c, 0x5aeb8, 0x5aeec, // HR latest/aggregate logs
        0x5b047, 0x5b074, 0x5b090, 0x5b0c8, // HRV latest/aggregate logs
        0x5bc0f, 0x5bc3c, 0x5bc5c, 0x5bc98, // SpO2 latest/aggregate logs
        0x5bf77, 0x5bfa4, 0x5bfc4, 0x5c000  // temperature latest/aggregate logs
    };

    private static final long[] FUNCTION_ENTRIES = {
        0x5ad90, // HR storage/aggregation
        0x5af60, // HRV storage/aggregation
        0x5bb2c, // SpO2 storage/aggregation
        0x5bcec, // stress storage/aggregation
        0x5be7c, // temperature storage/aggregation
        0x8a80a, // HR event consumer
        0x8a83e, // HRV event consumer
        0x8a8ae, // SpO2 event consumer
        0x8a8d8, // stress event consumer
        0x8a8fc, // temperature event consumer
        0x42860, // internal event 15 consumer (unsafe daily-health test injection)
        0x8d888, // sensor-task event dispatcher
        0x8d8fc  // internal event publisher
    };

    @Override
    protected void run() throws Exception {
        reportInitialDispatchTables();

        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();
        for (long raw : DATA_ADDRESSES) {
            Address target = toAddr(raw);
            println("DATA " + target);
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
                ReferenceIterator callers = currentProgram.getReferenceManager()
                    .getReferencesTo(function.getEntryPoint());
                while (callers.hasNext()) {
                    Reference reference = callers.next();
                    Function caller = functions.getFunctionContaining(reference.getFromAddress());
                    println("  CALLER " + reference.getFromAddress() + " "
                        + reference.getReferenceType() + " FUNCTION=" + describe(caller));
                    if (caller != null) {
                        queue.add(caller);
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

    private void reportInitialDispatchTables() throws Exception {
        List<Integer> output = new ArrayList<>(DATA_RUNTIME_LENGTH);
        long source = DATA_LOAD_ADDRESS;
        while (output.size() < DATA_RUNTIME_LENGTH) {
            int token = readUnsignedByte(source++);
            int literalCount = token & 0x07;
            if (literalCount == 0) {
                literalCount = readUnsignedByte(source++);
            }
            int runLength = token >>> 4;
            if (runLength == 0) {
                runLength = readUnsignedByte(source++);
            }
            for (int index = 1; index < literalCount; index++) {
                output.add(readUnsignedByte(source++));
            }
            if ((token & 0x08) == 0) {
                for (int index = 0; index < runLength; index++) {
                    output.add(0);
                }
            } else {
                int distance = readUnsignedByte(source++);
                if (distance == 0 || distance > output.size()) {
                    throw new IllegalStateException("Invalid scatter back-reference distance "
                        + distance + " at " + toAddr(source - 1));
                }
                for (int index = 0; index < runLength + 2; index++) {
                    output.add(output.get(output.size() - distance));
                }
            }
        }
        reportTable(output, "SENSOR_EVENT", SENSOR_EVENT_DISPATCH_BASE, 1, 16);
        reportSentinel(output, "SYSTEM_EVENT", SYSTEM_EVENT_DISPATCH_BASE);
        reportTable(output, "SYSTEM_EVENT", SYSTEM_EVENT_DISPATCH_BASE + 4, 0x1000, 15);
        reportSentinel(output, "STORAGE_EVENT", STORAGE_EVENT_DISPATCH_BASE);
        reportTable(output, "STORAGE_EVENT", STORAGE_EVENT_DISPATCH_BASE + 4, 0x2000, 7);
    }

    private void reportSentinel(List<Integer> bytes, String name, long address) {
        int offset = Math.toIntExact(address - DATA_RUNTIME_ADDRESS);
        println(String.format("%s sentinel=%s address=%s", name, formatWord(bytes, offset),
            toAddr(address)));
    }

    private void reportTable(
        List<Integer> bytes, String name, long address, int firstIdentifier, int count
    ) {
        int offset = Math.toIntExact(address - DATA_RUNTIME_ADDRESS);
        for (int index = 0; index < count; index++) {
            println(String.format("%s id=0x%04x handler=%s", name, firstIdentifier + index,
                formatWord(bytes, offset + index * 4)));
        }
    }

    private int readUnsignedByte(long address) throws Exception {
        return currentProgram.getMemory().getByte(toAddr(address)) & 0xff;
    }

    private String formatWord(List<Integer> bytes, int offset) {
        long value = (long) bytes.get(offset)
            | ((long) bytes.get(offset + 1) << 8)
            | ((long) bytes.get(offset + 2) << 16)
            | ((long) bytes.get(offset + 3) << 24);
        return String.format("0x%08x", value);
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
