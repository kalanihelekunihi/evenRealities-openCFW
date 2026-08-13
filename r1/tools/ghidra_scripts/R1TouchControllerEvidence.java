// Recover low-level IQS7211E initialization, status and diagnostic touch-controller evidence.
// @category Firmware

import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1TouchControllerEvidence extends GhidraScript {
    // File offsets from application.bin plus the 0x27000 load address.
    private static final long[] DATA_ADDRESSES = {
        0x2fc98, // IQS7211E_Init compensation-divider selection
        0x2fe48, // enter suspend mode
        0x310fc, // too-many-fingers status
        0x31138, // E0/E1/E2/E3 raw-channel bank selector table
        0x3ebfc, // guarded five-click host reset
        0x622c0, // ATI diagnostic register selection
        0x92a0c, // factory TOUCH_INIT parameter gate
        0x9316c  // coordinate scaling overflow/clamp
    };

    private static final long[] FUNCTION_ENTRIES = {
        0x2fdc8, // normal communication-window config refresh
        0x2fde2, // address-only communication terminator at register 0xff
        0x2f866, // one-byte factory communication terminator at register 0xff
        0x2fe9c, // shared IQS7211E register read wrapper
        0x2feac, // shared IQS7211E register write wrapper
        0x30e6c, // IRQ worker and raw-channel bank forwarder
        0x34070, // glasses-connection raw-frame dispatcher
        0x3e938, // application touch-event dispatcher
        0x41a40, // periodic E3 ATI-compensation audit
        0x502c4, // resolve the PPG-enable and touch-LDO GPIO devices by name
        0x50304, // disable the selected PPG-enable/touch-LDO GPIO device
        0x50338, // enable the selected PPG-enable/touch-LDO GPIO device
        0x51310, // resolve I2C0 and touch RDY input/output GPIO devices by name
        0x51368, // RDY/IRQ worker wrapper
        0x54b90, // active-low low-accuracy GPIO input open path
        0x54ff8, // repeated-start register read transaction
        0x5505c, // bounded register-address-plus-data write transaction
        0x6ed94, // generic GPIO interrupt callback dispatcher
        0x7a81c, // nRF GPIOTE/PORT input configuration
        0x6210c, // ATI diagnostic command consumer
        0x6a03c, // unsigned mean of a 21/24-word count frame
        0x6a234, // hardware-dependent 21/24 channel count
        0x6fc78, // count-mean callback bridge
        0x728b4, // ring-size/hardware-dependent electrode-map selector
        0x85cba, // generic device operation-table call at offset 0x0c
        0x85ccc, // generic device operation-table call at offset 0x18
        0x85ce0, // generic device lookup by name
        0x85d58, // generic device registration
        0x87ba4, // generic one-word IQS7211E register reader
        0x8e758, // ring-size-dependent Y-coordinate scaling initializer
        0x8e7ac, // touch IRQ-processing thunk adjacent to coordinate/touch callbacks
        0x8e7b0, // install RDY/task and coordinate callbacks
        0x933fc, // RDY callback posts task event bit 1
        0x93404, // install lower-level RDY callback
        0x92cbc, // scaled-coordinate/gesture producer
        0x93414, // diagnostic trackpad-register selector
        0x93424  // final slider-event producer
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();

        for (long raw : DATA_ADDRESSES) {
            Address target = toAddr(raw);
            println("DATA " + target);
            FunctionIterator precedingFunctions = functions.getFunctions(target, false);
            Function preceding = precedingFunctions.hasNext() ? precedingFunctions.next() : null;
            println("  PRECEDING_FUNCTION=" + describe(preceding));
            if (preceding != null && target.subtract(preceding.getEntryPoint()) <= 0x1000) {
                queue.add(preceding);
            }
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
            Address address = toAddr(raw);
            Function function = functions.getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
            }
            println("FUNCTION " + address + " " + describe(function));
            if (function != null) {
                queue.add(function);
                addCallers(functions, function, queue);
            }
        }

        printInstructionRange(0x92cbc, 0x92df0);
        printInstructionRange(0x502c4, 0x5036c);
        printInstructionRange(0x51310, 0x51440);

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

    private void addCallers(
            FunctionManager functions,
            Function function,
            Set<Function> queue) {
        ReferenceIterator callers = currentProgram.getReferenceManager()
            .getReferencesTo(function.getEntryPoint());
        while (callers.hasNext()) {
            Reference reference = callers.next();
            Function caller = functions.getFunctionContaining(reference.getFromAddress());
            println("  CALLER " + reference.getFromAddress() + " " + reference.getReferenceType()
                + " FUNCTION=" + describe(caller));
            if (caller != null) {
                queue.add(caller);
            }
        }
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }

    private void printInstructionRange(long start, long endExclusive) {
        println("INSTRUCTIONS " + toAddr(start) + "..." + toAddr(endExclusive));
        InstructionIterator instructions = currentProgram.getListing()
            .getInstructions(toAddr(start), true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            if (instruction.getAddress().compareTo(toAddr(endExclusive)) >= 0) {
                break;
            }
            println("  " + instruction.getAddress() + "  " + instruction);
        }
    }
}
