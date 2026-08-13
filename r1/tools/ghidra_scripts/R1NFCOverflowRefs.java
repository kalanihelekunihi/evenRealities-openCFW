// Trace every known reference in the R1 NFC mailbox overflow destination.
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

public class R1NFCOverflowRefs extends GhidraScript {
    private static final long DEFAULT_START = 0x20016b40L;
    private static final long DEFAULT_END_EXCLUSIVE = 0x20016c40L;

    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        long start = arguments.length > 0 ? Long.decode(arguments[0]) : DEFAULT_START;
        long endExclusive = arguments.length > 1
            ? Long.decode(arguments[1])
            : DEFAULT_END_EXCLUSIVE;
        if (endExclusive <= start) {
            throw new IllegalArgumentException("end address must be greater than start address");
        }

        FunctionManager manager = currentProgram.getFunctionManager();
        Set<Function> callers = new LinkedHashSet<>();

        println("NFC_OVERFLOW_RANGE start=" + toAddr(start)
            + " endExclusive=" + toAddr(endExclusive)
            + " byteCount=" + (endExclusive - start));

        for (long raw = start; raw < endExclusive; raw++) {
            Address address = toAddr(raw);
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(address);
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function caller = manager.getFunctionContaining(ref.getFromAddress());
                println("REF target=" + address
                    + " from=" + ref.getFromAddress()
                    + " type=" + ref.getReferenceType()
                    + " caller=" + describe(caller));
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
