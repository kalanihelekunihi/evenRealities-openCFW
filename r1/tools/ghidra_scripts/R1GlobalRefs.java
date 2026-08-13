// Trace references to R1 EUS reassembly state and decompile the owning functions.
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

public class R1GlobalRefs extends GhidraScript {
    private static final long[] ADDRESSES = {
        0x32388, 0x3238c, // EUS fragment accumulator and static response buffer.
        0x5d784, 0x5d788, 0x5d78c, // BLE event handler context.
        0x528b8, 0x528bc, // EUS service/log context.
        0x4e6e4, 0x4e6e8 // BLE event callback literal and shared connection context.
    };

    @Override
    protected void run() throws Exception {
        FunctionManager manager = currentProgram.getFunctionManager();
        Set<Function> callers = new LinkedHashSet<>();
        for (long raw : ADDRESSES) {
            Address address = toAddr(raw);
            println("\n=== GLOBAL " + address + " ===");
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(address);
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function caller = manager.getFunctionContaining(ref.getFromAddress());
                println("REF " + ref.getFromAddress() + " " + ref.getReferenceType()
                    + " CALLER=" + describe(caller));
                if (caller != null) {
                    callers.add(caller);
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
        for (Function function : callers) {
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

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
