// Decompile the exact R1 2.2.7 BLE transmit routines needed by a read-only
// application-ACE bootloader dump. This script never executes or patches firmware.
// @category Firmware

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;

public class R1BootloaderExfilEvidence extends GhidraScript {
    private static final long[] ENTRIES = {
        0x32414, // 239-byte EUS fragment producer, relocated from 2.2.6.
        0x34070, // Mode-0 channel-1 TX dispatcher.
        0x3407c, // Mode-2 explicit-handle channel-1 TX dispatcher.
        0x34088, // Mode-1 EUS/phone TX dispatcher.
        0x3e2e4, // Shared BLE TX allocation and queue core, relocated from 2.2.6.
        0x3e818, // Per-role notification-credit wrapper, relocated from 2.2.6.
        0x44fd8, // TX queue worker, relocated from 2.2.6.
        0x52968  // BAE8 sd_ble_gatts_hvx wrapper, relocated from 2.2.6.
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException("Decompiler setup failed");
        }

        println("R1_BOOTLOADER_EXFIL_EVIDENCE application=2.2.7.0005");
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
}
