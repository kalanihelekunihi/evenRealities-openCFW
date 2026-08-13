// Recover production IQS7211E power, GPIO, IRQ and service lifecycle evidence.
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
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1TouchLifecycleEvidence extends GhidraScript {
    private static final long[] FUNCTION_ENTRIES = {
        0x2fdc8, // refresh register-0x34 low byte before an IRQ communication window
        0x2fde2, // normal address-only register-0xff communication terminator
        0x2fdf8, // read-modify-write system-control suspend branch
        0x2f866, // one-byte register-0xff factory communication terminator
        0x2f880, // complete IQS7211E production initializer/reset acknowledgement
        0x2fe9c, // IQS register read wrapper
        0x2feac, // IQS register write wrapper
        0x30e6c, // normal IRQ state machine
        0x41a40, // bounded ATI-error E3 diagnostic audit
        0x45ec8, // consume queued factory parameters before termination task bits
        0x46650, // touch-task event-bit dispatcher
        0x46908, // cancel pending recovery/reinitialization timer
        0x46920, // touch-task/event-group bootstrap
        0x46954, // touch task body
        0x46eac, // recovery timer: clear pending and post open bit 2
        0x4e070, // connection-scoped fast-mode timer reset
        0x4eb60, // hardware close sequence
        0x4eb80, // hardware open/reset/IRQ-arm sequence
        0x4fa8c, // factory terminator payload 1
        0x4faa8, // factory terminator payload 2
        0x4fac4, // factory terminator payload 3 plus byte state
        0x4fae4, // factory terminator payload 4 plus UInt16 state
        0x4fb04, // factory terminator payload 5 plus byte state
        0x4fb24, // factory terminator payload 6 plus byte-backed state
        0x502c4, // resolve PPG-enable/touch-LDO devices by name
        0x50304, // disable one of the PPG-enable/touch-LDO GPIO devices
        0x50338, // enable one of the PPG-enable/touch-LDO GPIO devices
        0x51310, // resolve I2C0 and touch-RDY devices by name
        0x51368, // touch RDY interrupt worker
        0x54b90, // GPIO-input open and nRF GPIOTE/PORT configuration
        0x54ff8, // repeated-start register read transaction
        0x5505c, // bounded register-address-plus-data write transaction
        0x6f9e4, // bounded trackpad ATI-error recovery state machine
        0x6fce8, // show-reset full reinitialization
        0x6ed94, // generic GPIO interrupt-to-device callback dispatcher
        0x7a81c, // nRF GPIOTE input setup and high/low-accuracy selection
        0x7287c, // clear recovery-pending latch
        0x72888, // query recovery-pending latch
        0x85cba, // generic device operation-table call at offset 0x0c
        0x85ccc, // generic device operation-table call at offset 0x18
        0x85ce0, // generic device lookup by name
        0x85d58, // generic device registration
        0x8e6a0, // reference-counted service close
        0x8e7b0, // install RDY/task and coordinate callbacks; hold hardware closed
        0x8e7d0, // reference-counted service open
        0x933fc, // RDY callback: post touch-task bit 1
        0x93404, // install lower-level RDY callback
        0x93424, // synthesize final release before power-down
        0x93504  // post touch-task event flags
    };

    @Override
    protected void run() throws Exception {
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
            if (function != null) {
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
        }

        printInstructions(0x46650, 0x46908);
        printInstructions(0x4fa8c, 0x4fb44);
        printInstructions(0x502c4, 0x5036c);
        printInstructions(0x51310, 0x51440);
        printInstructions(0x54b90, 0x54c18);
        printInstructions(0x8e7ac, 0x8e7d0);
        printInstructions(0x933fc, 0x93414);

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

    private void printInstructions(long start, long endExclusive) {
        println("INSTRUCTIONS " + toAddr(start) + "..." + toAddr(endExclusive));
        InstructionIterator iterator = currentProgram.getListing().getInstructions(toAddr(start), true);
        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();
            if (instruction.getAddress().compareTo(toAddr(endExclusive)) >= 0) {
                break;
            }
            println("  " + instruction.getAddress() + "  " + instruction);
        }
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
