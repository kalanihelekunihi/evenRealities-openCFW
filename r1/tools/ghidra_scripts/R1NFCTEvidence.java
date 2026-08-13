// Audit whether the nRF52840 internal NFC-A/NFCT driver is a live R1 interface.
// Exact addresses are pinned to application 2.2.7.0005.
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

public class R1NFCTEvidence extends GhidraScript {
    private static final long VECTOR_WORD = 0x27054L;
    private static final long HANDLER = 0x3060cL;
    private static final long CALLBACK = 0x2002c2d8L;
    private static final long[] ENTRIES = {
        HANDLER,
        0x7a500L, // event test
        0x7a510L, // event clear
        0x7a520L, // interrupt-enabled test
        0x7b448L  // field-event state handler
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> decompile = new LinkedHashSet<>();

        long vector = Integer.toUnsignedLong(
            currentProgram.getMemory().getInt(toAddr(VECTOR_WORD)));
        println("NFCT_VECTOR word=" + toAddr(VECTOR_WORD)
            + " value=" + String.format("0x%08x", vector)
            + " handlerMatch=" + ((vector & ~1L) == HANDLER));

        for (long raw : ENTRIES) {
            Address entry = toAddr(raw);
            Function function = functions.getFunctionAt(entry);
            if (function == null) {
                disassemble(entry);
                function = createFunction(entry, null);
            }
            println("ENTRY " + describe(function));
            if (function != null) {
                decompile.add(function);
            }
            printCallers(entry, functions);
        }

        println("CALLBACK address=" + toAddr(CALLBACK));
        ReferenceIterator callbackRefs = currentProgram.getReferenceManager()
            .getReferencesTo(toAddr(CALLBACK));
        while (callbackRefs.hasNext()) {
            Reference reference = callbackRefs.next();
            Function caller = functions.getFunctionContaining(reference.getFromAddress());
            println("  REF from=" + reference.getFromAddress()
                + " type=" + reference.getReferenceType()
                + " caller=" + describe(caller));
            if (caller != null) {
                decompile.add(caller);
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
            DecompileResults result = decompiler.decompileFunction(function, 90, monitor);
            if (result.decompileCompleted() && result.getDecompiledFunction() != null) {
                println(result.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + result.getErrorMessage());
            }
        }
        decompiler.dispose();
    }

    private void printCallers(Address entry, FunctionManager functions) {
        ReferenceIterator callers = currentProgram.getReferenceManager().getReferencesTo(entry);
        while (callers.hasNext()) {
            Reference reference = callers.next();
            Function caller = functions.getFunctionContaining(reference.getFromAddress());
            println("  CALLER from=" + reference.getFromAddress()
                + " type=" + reference.getReferenceType()
                + " function=" + describe(caller));
        }
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
