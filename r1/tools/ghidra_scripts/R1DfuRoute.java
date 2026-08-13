// Find and decompile the Nordic buttonless-DFU path in the R1 production image.
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
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1DfuRoute extends GhidraScript {
    private static final long[] SEED_ADDRESSES = {
        0x75f64, // Immediate caller of the vector-handoff wrapper.
        0x52018, // Calls the bootloader-vector handoff routine at 0x78590.
        0x52050, 0x5207c, // DFU authorization and reset helpers.
        0x52090, // Adds the buttonless control characteristic.
        0x520e4, // Adds FE59 and references the Nordic DFU UUID base.
        0x52154, 0x521d8, 0x5227c, 0x522d8, // BLE/control/response handlers.
        0x5232c, // Application callback passed to ble_dfu_buttonless_init.
        0x78590, // SoftDevice vector-table handoff / bootloader presence check.
        0x8ed5c  // Bootloader settings-page write helper.
    };

    // Runtime addresses are file offsets plus the 0x27000 raw-image load address.
    private static final long[] STRING_ADDRESSES = {
        0x4ea8c, 0x4eac8, // Power management wants to reset to DFU mode.
        0x4eaf8, 0x4eb30, // Power management allowed the DFU reset.
        0x524a0, 0x524d4, // Device is preparing to enter bootloader mode.
        0x52544, 0x52570, // Device will enter bootloader mode.
        0x52594, 0x525d4, // Request to enter bootloader mode failed asynchronously.
        0x52674, 0x526a4, // Unknown event from ble_dfu_buttonless.
        0x9209c, 0x920c4, // THREAD_BLE_EVT_DFU_START
        0x78664, // Setting vector table to bootloader.
        0x78734, // No bootloader was found.
        0xc2a98  // Bootloader settings-page write-protection diagnostic.
    };

    @Override
    protected void run() throws Exception {
        FunctionManager manager = currentProgram.getFunctionManager();
        Set<Function> functions = new LinkedHashSet<>();

        printAlignedSvc(0xa8, "sd_ble_gatts_service_add");
        printAlignedSvc(0xb8, "sd_ble_l2cap_ch_setup");

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

        for (long raw : STRING_ADDRESSES) {
            Address stringAddress = toAddr(raw);
            println("\n=== STRING " + stringAddress + " ===");
            ReferenceIterator refs = currentProgram.getReferenceManager()
                .getReferencesTo(stringAddress);
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function function = manager.getFunctionContaining(ref.getFromAddress());
                println("REF " + ref.getFromAddress() + " " + ref.getReferenceType()
                    + " CALLER=" + describe(function));
                if (function != null) {
                    functions.add(function);
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

        for (Function function : functions) {
            println("\n=== FUNCTION " + describe(function) + " ===");
            printEntryReferences(manager, function.getEntryPoint());
            DecompileResults results = decompiler.decompileFunction(function, 90, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        decompiler.dispose();
    }

    private void printAlignedSvc(int svc, String name) throws Exception {
        Address address = currentProgram.getMemory().getMinAddress();
        Address max = currentProgram.getMemory().getMaxAddress();
        println("\n=== ALIGNED SVC 0x" + Integer.toHexString(svc) + " " + name + " ===");
        while (address.compareTo(max) < 0) {
            int first = currentProgram.getMemory().getByte(address) & 0xff;
            int second = currentProgram.getMemory().getByte(address.add(1)) & 0xff;
            if (first == svc && second == 0xdf) {
                println("SVC " + address);
            }
            address = address.add(2);
        }
    }

    private void printEntryReferences(FunctionManager manager, Address address) {
        ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(address);
        while (refs.hasNext()) {
            Reference ref = refs.next();
            Function caller = manager.getFunctionContaining(ref.getFromAddress());
            println("ENTRY_REF " + ref.getFromAddress() + " " + ref.getReferenceType()
                + " CALLER=" + describe(caller));
        }
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
