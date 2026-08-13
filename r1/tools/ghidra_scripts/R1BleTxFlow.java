// Reconstruct the R1 BAE8 GATT event and notification-transmit pipeline.
//
// The stock analyzer misses several Thumb entries because functions and literal
// pools are densely interleaved in this part of the image.  This script creates
// only the version-pinned entries below when necessary, then decompiles them.
// It does not execute the firmware or access Bluetooth hardware.
//
// Usage:
//   -postScript R1BleTxFlow.java
// @category Firmware

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.mem.Memory;

public class R1BleTxFlow extends GhidraScript {
    private static final long[] ENTRIES = {
        0x32408, // EUS 239-byte fragment producer.
        0x32198, // EUS synchronous fragment reassembly and CRC gate.
        0x33af8, // Factory-marker channel-1 RX enqueue.
        0x33dbc, // Normal channel-1 RX enqueue.
        0x34064, // Mode 0: ordinary channel-1/glasses dispatcher.
        0x34070, // Mode 2: explicit-handle channel-1 dispatcher (eAT output).
        0x3407c, // Mode 1: EUS/phone dispatcher.
        0x3e274, // Shared allocation, occupancy warning, and queue-send core.
        0x3e7a8, // Per-role notification-credit wrapper and EUS retry.
        0x3e8ae, // Give at most one notification credit.
        0x3e8b4, // Give a bounded number of credits, capped at four.
        0x3e8dc, // Drain and refill one semaphore to four credits.
        0x3e8fc, // Connection-handle to glasses/phone semaphore mapping.
        0x3e924, // Timed semaphore take.
        0x44ef0, // Channel-1 TX thread creation.
        0x44f20, // BLE event thread creation.
        0x44f50, // TX queue drain and mode-to-characteristic selection.
        0x450cc, // BAE8 RX queue drain and lane selection.
        0x45f3c, // Factory-marker channel-1 queue drain and AT^ split.
        0x4e650, // EUS low-level thunk: lane 1, initial wait 200.
        0x4e65e, // Channel-1 low-level thunk: lane 0, initial wait 100.
        0x4e66c, // BAE8 service plus two 4/4 counting semaphores.
        0x526cc, // sd_ble_gatts_hvx notification wrapper.
        0x52b20, // Raw BAE8 BLE-event demultiplexer.
        0x5d5e0, // Application callback for custom service events 2/3/6..9.
        0x7ccb4, // Connect-time CCCD restoration.
        0x7cf4c, // GATTS write-to-custom-event translation.
        0x7a38c, // SoftDevice event fetch and observer-set dispatch.
        0x7a53c, // Observer priority-group iterator initialization.
        0x7a56a, // Observer priority-group iterator advance.
        0x920ec, // Channel-1 output queue: 20 pointer records.
        0x92178, // BAE8 input queue: 50 pointer records.
        0x9227c, // Shared EUS/explicit output queue: 50 pointer records.
        0x9230c  // Factory-marker channel-1 input queue: 8 pointer records.
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }

        println("R1_BLE_TX_FLOW application=2.2.6.0009 base=0x00027000");
        println("QUEUE_FACTS channel1_records=20 shared_eus_explicit_records=50 item_bytes=4");
        println("RX_QUEUE_FACTS normal_channel1_records=50 factory_channel1_records=8"
            + " eus_reassembly=synchronous enqueue_wait=0");
        println("CREDIT_FACTS per_role_initial=4 per_role_max=4 svc_hvn_queue=4");
        println("EVENT_FACTS connect=0x10 disconnect=0x11 write=0x50 hvn_complete=0x57");
        printObserverTable();

        for (long raw : ENTRIES) {
            Address address = toAddr(raw);
            Function function = functions.getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
            }
            println("\n--- " + (function == null
                ? "NO_FUNCTION@" + address
                : function.getName() + "@" + function.getEntryPoint()) + " ---");
            if (function == null) {
                continue;
            }
            DecompileResults results = decompiler.decompileFunction(function, 90, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        decompiler.dispose();
    }

    private void printObserverTable() throws Exception {
        Memory memory = currentProgram.getMemory();
        Address spans = toAddr(0x9ca70);
        println("OBSERVER_FACTS priorities=4 record_bytes=8 iteration=ascending");
        for (int priority = 0; priority < 4; priority++) {
            long start = Integer.toUnsignedLong(memory.getInt(spans.add(priority * 8L)));
            long end = Integer.toUnsignedLong(memory.getInt(spans.add(priority * 8L + 4)));
            println("OBSERVER_PRIORITY " + priority + " start=0x"
                + Long.toHexString(start) + " end=0x" + Long.toHexString(end));
            for (long record = start; record < end; record += 8) {
                long handler = Integer.toUnsignedLong(memory.getInt(toAddr(record)));
                long context = Integer.toUnsignedLong(memory.getInt(toAddr(record + 4)));
                println("  OBSERVER record=0x" + Long.toHexString(record)
                    + " handler=0x" + Long.toHexString(handler)
                    + " context=0x" + Long.toHexString(context));
            }
        }
    }
}
