// Recover Service Changed, bonded system attributes, and peer CAR cache handling.
// Import application.bin as raw ARM:LE:32:Cortex at 0x00027000 first.
// @category Firmware

import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;

public class R1GattCacheRoute extends GhidraScript {
    private static final long[] SEED_ADDRESSES = {
        0x578cc, // Schedule cache/CAR work for a connection.
        0x578f4, // Read peer GAP Central Address Resolution characteristic 2AA6.
        0x66f28, // GATT cache BLE event handler, including both CAR read responses.
        0x6edfc, // Restore bonded GATTS system attributes.
        0x6eeb4, // Retrieve/cache bonded GATTS system attributes.
        0x6f118, // Send Service Changed from first user handle through 0xffff.
        0x7f2b0, // Application Peer Manager callback; new-bond branch logs but does not whitelist.
        0x8a928, // Register the cache-manager BLE observer.
        0x8a93c, // Persist the service-changed-pending flag across peers.
        0x8aa08  // Event-context Service Changed state machine.
    };

    @Override
    protected void run() throws Exception {
        FunctionManager manager = currentProgram.getFunctionManager();
        Set<Function> functions = new LinkedHashSet<>();

        printAlignedSvc(manager, 0xaf, "sd_ble_gatts_service_changed");
        printAlignedSvc(manager, 0xb1, "sd_ble_gatts_sys_attr_set");
        printAlignedSvc(manager, 0xb2, "sd_ble_gatts_sys_attr_get");
        printAlignedSvc(manager, 0xb3, "sd_ble_gatts_initial_user_handle_get");
        printAlignedSvc(manager, 0xb4, "sd_ble_gatts_attr_get");

        for (long raw : SEED_ADDRESSES) {
            Address address = toAddr(raw);
            Function function = manager.getFunctionAt(address);
            if (function == null) {
                function = manager.getFunctionContaining(address);
            }
            if (function == null && currentProgram.getMemory().contains(address)) {
                disassemble(address);
                function = createFunction(address, null);
            }
            if (function != null) {
                functions.add(function);
            }
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }
        for (Function function : functions) {
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

    private void printAlignedSvc(FunctionManager manager, int svc, String name) throws Exception {
        Address address = currentProgram.getMemory().getMinAddress();
        Address max = currentProgram.getMemory().getMaxAddress();
        println("\n=== ALIGNED SVC 0x" + Integer.toHexString(svc) + " " + name + " ===");
        while (address.compareTo(max) < 0) {
            int first = currentProgram.getMemory().getByte(address) & 0xff;
            int second = currentProgram.getMemory().getByte(address.add(1)) & 0xff;
            if (first == svc && second == 0xdf) {
                Function function = manager.getFunctionContaining(address);
                println("SVC " + address + " FUNCTION=" + describe(function));
            }
            address = address.add(2);
        }
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
