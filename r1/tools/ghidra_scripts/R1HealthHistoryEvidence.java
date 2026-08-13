// Recover exact EUS-to-internal history query records and internal event-14 handling.
// @category Firmware

import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1HealthHistoryEvidence extends GhidraScript {
    private static final long METRIC_DESCRIPTOR_TABLE_ADDRESS = 0x99bf4;
    private static final int METRIC_DESCRIPTOR_COUNT = 6;
    private static final int METRIC_DESCRIPTOR_LENGTH = 16;
    private static final long[] BACKFILL_WINDOW_LITERAL_ADDRESSES = {
        0x8c570, // HR
        0x8d188, // SpO2
        0x8bf28, // activity
        0x8cb78  // HRV
    };
    private static final long[] FUNCTION_ENTRIES = {
        0x82c8a, // health 01/01 HR daily
        0x82e34, // health 01/02 HR points
        0x82dbe, // health 01/03 HR measure
        0x82d5a, // health 02/01 SpO2 daily
        0x82e9a, // health 02/02 SpO2 points
        0x82dfa, // health 02/03 SpO2 measure
        0x82cce, // health 04/01 HRV daily
        0x82e66, // health 04/02 HRV points
        0x82df8, // health 04/03 HRV measure (no-op)
        0x82c44, // health 05/01 activity daily
        0x82c10, // health 05/02 activity detail
        0x82d14, // health 06/01 sleep daily
        0x82d9e, // health 06/02 sleep detail
        0x82ece, // health 7f/01 report setting
        0x4286e, // internal sensor-event 0x000e service handler
        0x8b8e8, // internal health-history query consumer
        0x5aca6, // timestamp-to-24-slot index
        0x5aba0, // per-slot rolling average update
        0x8af40, // firmware timestamp plus UTC offset to calendar fields
        0x70648, 0x706a4, 0x7062c, // HR descriptor callbacks
        0x90df0, 0x90e4c, 0x90dd4, // SpO2 descriptor callbacks
        0x91918, 0x91954, 0x918de, // temperature descriptor callbacks
        0x9113e, 0x91158, 0x91124, // stress descriptor callbacks
        0x482a8, 0x4832c, 0x48288, // activity descriptor callbacks
        0x706d8, 0x7073c, 0x706be  // HRV descriptor callbacks
    };

    @Override
    protected void run() throws Exception {
        reportMetricDescriptors();
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();
        for (long raw : FUNCTION_ENTRIES) {
            Address address = toAddr(raw);
            Function function = functions.getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
            }
            println("FUNCTION " + address + " " + describe(function));
            if (function == null) {
                continue;
            }
            queue.add(function);
            ReferenceIterator callers = currentProgram.getReferenceManager()
                .getReferencesTo(function.getEntryPoint());
            while (callers.hasNext()) {
                Reference reference = callers.next();
                Function caller = functions.getFunctionContaining(reference.getFromAddress());
                println("  CALLER " + reference.getFromAddress() + " "
                    + reference.getReferenceType() + " FUNCTION=" + describe(caller));
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

    private void reportMetricDescriptors() throws Exception {
        for (int index = 0; index < METRIC_DESCRIPTOR_COUNT; index++) {
            long entry = METRIC_DESCRIPTOR_TABLE_ADDRESS
                + index * METRIC_DESCRIPTOR_LENGTH;
            println(String.format(
                "METRIC_DESCRIPTOR index=%d address=%s metric=%d length=%d reserved=0x%04x "
                    + "callbacks=[0x%08x,0x%08x,0x%08x]",
                index,
                toAddr(entry),
                readUnsignedByte(entry),
                readUnsignedByte(entry + 1),
                readUnsignedHalfWord(entry + 2),
                readUnsignedWord(entry + 4),
                readUnsignedWord(entry + 8),
                readUnsignedWord(entry + 12)
            ));
        }
        for (long address : BACKFILL_WINDOW_LITERAL_ADDRESSES) {
            println(String.format("BACKFILL_WINDOW address=%s seconds=%d",
                toAddr(address), readUnsignedWord(address)));
        }
    }

    private int readUnsignedByte(long address) throws Exception {
        return currentProgram.getMemory().getByte(toAddr(address)) & 0xff;
    }

    private int readUnsignedHalfWord(long address) throws Exception {
        return readUnsignedByte(address) | readUnsignedByte(address + 1) << 8;
    }

    private long readUnsignedWord(long address) throws Exception {
        return (long)readUnsignedByte(address)
            | (long)readUnsignedByte(address + 1) << 8
            | (long)readUnsignedByte(address + 2) << 16
            | (long)readUnsignedByte(address + 3) << 24;
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
