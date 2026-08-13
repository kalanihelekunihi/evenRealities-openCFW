// Recover the production QMA6100 configuration, interrupt, FIFO, and sample path.
// @category Firmware

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1MotionEvidence extends GhidraScript {
    private static final long[] FUNCTION_ENTRIES = {
        0x4f10c, 0x50208, 0x5025c, 0x50270, 0x50294, 0x502ac,
        0x6f404, 0x6f418, 0x6f436, 0x6f448,
        0x86d40, 0x86e34, 0x86e68, 0x86ee4, 0x86fa8, 0x86ff4,
        0x8714c, 0x871c4, 0x87250, 0x872e4, 0x873f4, 0x92580
    };

    private static final long DATA_LOAD_ADDRESS = 0xc4610;
    private static final long DATA_RUNTIME_ADDRESS = 0x200064a8L;
    private static final int DATA_RUNTIME_LENGTH = 0x195c;
    private static final long QMA_RUNTIME_STATE_ADDRESS = 0x20007698L;

    @Override
    protected void run() throws Exception {
        reportInitialQMAState();

        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();
        for (long raw : FUNCTION_ENTRIES) {
            Function function = functions.getFunctionAt(toAddr(raw));
            if (function == null) {
                disassemble(toAddr(raw));
                function = createFunction(toAddr(raw), null);
            }
            println("FUNCTION_ENTRY " + toAddr(raw) + " " + describe(function));
            if (function == null) {
                continue;
            }
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

    /**
     * ARM scatter loading expands the compressed initialized-data range at 0xc4610 into
     * 0x200064a8...0x20007e03 with the decoder at 0x286f4. Recovering that image proves that the
     * production QMA I2C address is 0x12 and both optional interrupt callback hooks begin null.
     */
    private void reportInitialQMAState() throws Exception {
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

            // The compact ARM scatter format encodes the literal count one greater than the
            // number copied. Function 0x286f4 branches through its pre-decrement loop accordingly.
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
        if (output.size() != DATA_RUNTIME_LENGTH) {
            throw new IllegalStateException("Scatter output length " + output.size()
                + " does not equal expected " + DATA_RUNTIME_LENGTH);
        }

        int stateOffset = Math.toIntExact(QMA_RUNTIME_STATE_ADDRESS - DATA_RUNTIME_ADDRESS);
        println("QMA_INITIAL_STATE runtime=" + toAddr(QMA_RUNTIME_STATE_ADDRESS)
            + " i2cAddress=0x" + Integer.toHexString(output.get(stateOffset))
            + " doubleTapCallback=" + formatWord(output, stateOffset + 4)
            + " anyMotionCallback=" + formatWord(output, stateOffset + 8)
            + " compressedEnd=" + toAddr(source));
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
