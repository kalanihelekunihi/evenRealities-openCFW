// Recover the production EUS system, health, and testable command registration tables.
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

public class R1ProtocolRegistrationEvidence extends GhidraScript {
    private static final long DATA_LOAD_ADDRESS = 0xc4610;
    private static final long DATA_RUNTIME_ADDRESS = 0x200064a8L;
    private static final int DATA_RUNTIME_LENGTH = 0x195c;
    private static final long MODULE_DISPATCH_TABLE_ADDRESS = 0x20006b90L;
    private static final long HEALTH_TABLE_ADDRESS = 0x9a454;
    private static final int HEALTH_ENTRY_COUNT = 14;
    private static final long SYSTEM_TABLE_ADDRESS = 0x9a4cc;
    private static final int SYSTEM_ENTRY_COUNT = 20;
    private static final long TESTABLE_TABLE_ADDRESS = 0x9a588;
    private static final int TESTABLE_ENTRY_COUNT = 1;
    private static final long[] MODULE_DISPATCHER_ADDRESSES = {
        0x8316c, // top-level EUS module ingress, including special module 0x7f path
        0x83298, // shared command/subcommand lookup helper
        0x82be8, // health: table 0x9a454, 14 entries
        0x83ca8, // system: table 0x9a4cc, 20 entries
        0x84c98  // orphan sport-shaped dispatcher over 0x9a588; module 0x03 slot is null
    };
    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> handlers = new LinkedHashSet<>();
        reportInitialModuleDispatchTable();
        reportReferences("HEALTH_TABLE", HEALTH_TABLE_ADDRESS, functions);
        reportReferences("SYSTEM_TABLE", SYSTEM_TABLE_ADDRESS, functions);
        reportReferences("TESTABLE_TABLE", TESTABLE_TABLE_ADDRESS, functions);
        reportTable("HEALTH", HEALTH_TABLE_ADDRESS, HEALTH_ENTRY_COUNT, handlers, functions);
        reportTable("SYSTEM", SYSTEM_TABLE_ADDRESS, SYSTEM_ENTRY_COUNT, handlers, functions);
        reportTable("TESTABLE", TESTABLE_TABLE_ADDRESS, TESTABLE_ENTRY_COUNT, handlers, functions);
        for (long raw : MODULE_DISPATCHER_ADDRESSES) {
            Function dispatcher = functions.getFunctionAt(toAddr(raw));
            if (dispatcher == null) {
                disassemble(toAddr(raw));
                dispatcher = createFunction(toAddr(raw), null);
            }
            println("MODULE_DISPATCHER " + toAddr(raw) + " " + describe(dispatcher));
            if (dispatcher != null) {
                handlers.add(dispatcher);
            }
        }
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }
        for (Function function : handlers) {
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

    private void reportInitialModuleDispatchTable() throws Exception {
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
        int offset = Math.toIntExact(MODULE_DISPATCH_TABLE_ADDRESS - DATA_RUNTIME_ADDRESS);
        for (int module = 0; module <= 3; module++) {
            println(String.format("MODULE_TABLE module=0x%02x handler=0x%08x", module,
                readRuntimeWord(output, offset + module * 4)));
        }
        println("MODULE_TABLE module=0x7f special-uses-testable-command-table=0x0009a588");
    }

    private void reportTable(
        String name,
        long address,
        int count,
        Set<Function> handlers,
        FunctionManager functions
    ) throws Exception {
        for (int index = 0; index < count; index++) {
            long entryAddress = address + index * 8L;
            long identifier = readUnsignedWord(entryAddress);
            long thumbPointer = readUnsignedWord(entryAddress + 4);
            Address handlerAddress = toAddr(thumbPointer & ~1L);
            Function function = functions.getFunctionAt(handlerAddress);
            if (function == null) {
                disassemble(handlerAddress);
                function = createFunction(handlerAddress, null);
            }
            println(String.format("%s index=%d id=0x%04x entry=%s thumb=0x%08x handler=%s",
                name, index, identifier, toAddr(entryAddress), thumbPointer, describe(function)));
            if (function != null) {
                handlers.add(function);
            }
        }
    }

    private void reportReferences(String name, long raw, FunctionManager functions) {
        Address address = toAddr(raw);
        println(name + " address=" + address);
        ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(address);
        while (references.hasNext()) {
            Reference reference = references.next();
            Function caller = functions.getFunctionContaining(reference.getFromAddress());
            println("  REF " + reference.getFromAddress() + " " + reference.getReferenceType()
                + " FUNCTION=" + describe(caller));
        }
    }

    private long readUnsignedWord(long address) throws Exception {
        byte[] bytes = new byte[4];
        currentProgram.getMemory().getBytes(toAddr(address), bytes);
        return (long)(bytes[0] & 0xff)
            | ((long)(bytes[1] & 0xff) << 8)
            | ((long)(bytes[2] & 0xff) << 16)
            | ((long)(bytes[3] & 0xff) << 24);
    }

    private int readUnsignedByte(long address) throws Exception {
        return currentProgram.getMemory().getByte(toAddr(address)) & 0xff;
    }

    private long readRuntimeWord(List<Integer> bytes, int offset) {
        return (long)bytes.get(offset)
            | ((long)bytes.get(offset + 1) << 8)
            | ((long)bytes.get(offset + 2) << 16)
            | ((long)bytes.get(offset + 3) << 24);
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
