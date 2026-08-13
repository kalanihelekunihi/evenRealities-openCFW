// Recover the complete SoftDevice enable/configuration surface in the R1 production image.
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
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;

public class R1SoftDeviceConfig extends GhidraScript {
    private static final long[] SEED_ADDRESSES = {
        0x4df18, // Application BLE bootstrap after the SoftDevice is enabled.
        0x539b8, // SoftDevice/BLE enable and extra GATTS/RC-calibration configuration.
        0x79e58, // Returns the linker-provided application RAM start.
        0x79e6c, // nrf_sdh_ble_default_cfg_set equivalent.
        0x7a0ec, // sd_ble_enable wrapper and RAM-boundary diagnostics.
        0x7a440  // sd_softdevice_enable wrapper and LFCLK configuration.
    };

    private static final long[][] INSTRUCTION_RANGES = {
        {0x539b8, 0x53a5a},
        {0x79e58, 0x79e68},
        {0x79e6c, 0x7a0b4}
    };

    private static final long[][] DATA_RANGES = {
        {0x9ca28, 4}, // nrf_clock_lf_cfg_t: source, rc_ctiv, rc_temp_ctiv, accuracy.
        {0x9ca90, 4}  // Linker-provided application RAM start.
    };

    @Override
    protected void run() throws Exception {
        FunctionManager manager = currentProgram.getFunctionManager();
        Set<Function> functions = new LinkedHashSet<>();

        printAlignedSvc(manager, 0x60, "sd_ble_enable");
        printAlignedSvc(manager, 0x67, "sd_ble_opt_set");
        printAlignedSvc(manager, 0x69, "sd_ble_cfg_set");
        printAlignedSvc(manager, 0xb8, "sd_ble_l2cap_ch_setup");

        for (long[] range : DATA_RANGES) {
            printBytes(range[0], (int) range[1]);
        }

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

        for (long[] range : INSTRUCTION_RANGES) {
            printInstructions(range[0], range[1]);
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

    private void printBytes(long raw, int count) throws Exception {
        Address address = toAddr(raw);
        StringBuilder output = new StringBuilder();
        for (int index = 0; index < count; index++) {
            if (index != 0) {
                output.append(' ');
            }
            output.append(String.format("%02x", currentProgram.getMemory().getByte(address.add(index)) & 0xff));
        }
        println("\nDATA " + address + " " + output);
    }

    private void printInstructions(long rawStart, long rawEnd) {
        Address start = toAddr(rawStart);
        Address end = toAddr(rawEnd);
        disassemble(start);
        println("\n=== INSTRUCTIONS " + start + "..." + end + " ===");
        InstructionIterator iterator = currentProgram.getListing().getInstructions(start, true);
        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();
            if (instruction.getAddress().compareTo(end) >= 0) {
                break;
            }
            println(instruction.getAddress() + "  " + instruction);
        }
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
