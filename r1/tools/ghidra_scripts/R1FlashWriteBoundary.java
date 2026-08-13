// Inventory application instructions at the SoftDevice/flash/MBR trust boundary.
// Import application.bin as raw ARM:LE:32:Cortex at 0x00027000 first.
// @category Firmware

import java.util.Arrays;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1FlashWriteBoundary extends GhidraScript {
    private static final Set<Integer> BOUNDARY_SVCS = new HashSet<>(Arrays.asList(
        0x11, // SD_SOFTDEVICE_DISABLE
        0x18, // SD_MBR_COMMAND
        0x28, // SD_FLASH_PAGE_ERASE
        0x29  // SD_FLASH_WRITE
    ));

    private static final long[] SEED_FUNCTIONS = {
        0x5498c, // Internal-flash erase/query callback.
        0x54aa4, // Internal-flash write callback.
        0x7ca7c, // 2.2.6 direct NVMC.CONFIG write and READY poll helper.
        0x7d2a0, // 2.2.7 direct NVMC.CONFIG write and READY poll helper.
        0x87520, // 2.2.6 SoftDevice flash-operation dispatcher/wrappers.
        0x87d6c, // 2.2.7 SoftDevice flash-operation dispatcher/wrappers.
        0x8ed5c  // Buttonless-DFU advertisement-name settings helper.
    };

    @Override
    protected void run() throws Exception {
        Listing listing = currentProgram.getListing();
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> decompile = new LinkedHashSet<>();
        Address address = currentProgram.getMemory().getMinAddress();
        Address maximum = currentProgram.getMemory().getMaxAddress();

        println("kind\tsvc\taddress\tfunction");
        while (address.compareTo(maximum) < 0) {
            int first = currentProgram.getMemory().getByte(address) & 0xff;
            int second = currentProgram.getMemory().getByte(address.add(1)) & 0xff;
            if (BOUNDARY_SVCS.contains(first) && second == 0xdf) {
                Instruction instruction = listing.getInstructionAt(address);
                Function function = functions.getFunctionContaining(address);
                boolean real = instruction != null
                    && "svc".equalsIgnoreCase(instruction.getMnemonicString())
                    && function != null;
                println((real ? "CALL" : "DATA_OR_UNCLASSIFIED") + "\t0x"
                    + Integer.toHexString(first) + "\t" + address + "\t"
                    + describe(function));
                if (real) {
                    decompile.add(function);
                }
            }
            address = address.add(2);
        }

        for (long raw : SEED_FUNCTIONS) {
            Address seed = toAddr(raw);
            Function function = functions.getFunctionContaining(seed);
            if (function == null) {
                function = functions.getFunctionAt(seed);
            }
            if (function == null) {
                disassemble(seed);
                function = createFunction(seed, null);
            }
            if (function != null) {
                decompile.add(function);
            } else {
                println("SEED_NOT_IN_FUNCTION\t" + seed);
            }
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }
        for (Function function : decompile) {
            println("\n=== FUNCTION " + describe(function) + " ===");
            printEntryReferences(functions, function.getEntryPoint());
            DecompileResults results = decompiler.decompileFunction(function, 90, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        decompiler.dispose();
    }

    private void printEntryReferences(FunctionManager functions, Address entry) {
        ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(entry);
        while (references.hasNext()) {
            Reference reference = references.next();
            Function caller = functions.getFunctionContaining(reference.getFromAddress());
            println("ENTRY_REF " + reference.getFromAddress() + " "
                + reference.getReferenceType() + " CALLER=" + describe(caller));
        }
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
