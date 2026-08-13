// Decompile selected R1 functions and list their callers/references.
// @category Firmware

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1Functions extends GhidraScript {
    private static final long[] ADDRESSES = {
        0x27488,
        0x3e938, 0x7ba24, 0x4cb34, 0x34064, 0x7d28c, 0x7efd6, 0x7d6f4,
        0x4f160, 0x4f040, 0x4f1c4, 0x4ed34, 0x4ed14, 0x4f2dc, 0x4f2bc,
        0x4f8e0, 0x4f8bc, 0x4f94c, 0x4f928, 0x4f348, 0x4f328, 0x4eddc,
        0x4f10c, 0x4e5bc, 0x4ef24, 0x4eff8, 0x45078, 0x45c78,
        0x4ef8c, 0x3d7ac, 0x84874, 0x8e6a0, 0x93424,
        0x45c54, 0x9230c,
        0x45f3c, 0x48ba4, 0x33af8, 0x33dbc, 0x32198, 0x500fc,
        0x4f260, 0x625c0,
        0x8a55c, 0x89d88, 0x89eec, 0x8a1ac, 0x92440, 0x8a45c,
        0x50208, 0x5025c, 0x508da, 0x5128c, 0x503b4, 0x3530c, 0x510d8, 0x51108,
        0x4ed64, 0x4f30c, 0x4f378, 0x4f914, 0x4f980,
        0x575d8, 0x4a24c, 0x8a83e, 0x5af60,
        0x53b2c, 0x53c6c, 0x541a8,
        0x6f1a8, 0x6f1bc, 0x6f1da, 0x6f1dc,
        0x6f380, 0x6f394, 0x6f3b2, 0x6f3b4,
        0x751b8, 0x75290, 0x754dc, 0x75510,
        0x6f404, 0x6f418, 0x6f436, 0x6f448,
        0x86d40, 0x86e34, 0x86e68, 0x86ee4, 0x86fa8, 0x86ff4, 0x8714c,
        0x50f9c, 0x6ccc0, 0x2cd00, 0x2e0d0
    };

    @Override
    protected void run() throws Exception {
        FunctionManager manager = currentProgram.getFunctionManager();
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }

        for (long raw : ADDRESSES) {
            Address address = toAddr(raw);
            Function function = manager.getFunctionAt(address);
            if (function == null) {
                function = manager.getFunctionContaining(address);
            }
            if (function == null && currentProgram.getMemory().contains(address)) {
                disassemble(address);
                function = createFunction(address, null);
            }
            println("\n=== REQUEST " + address + " FUNCTION=" + describe(function) + " ===");
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(address);
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function caller = manager.getFunctionContaining(ref.getFromAddress());
                println("REF " + ref.getFromAddress() + " " + ref.getReferenceType()
                    + " CALLER=" + describe(caller));
            }
            ReferenceIterator thumbRefs = currentProgram.getReferenceManager()
                .getReferencesTo(address.add(1));
            while (thumbRefs.hasNext()) {
                Reference ref = thumbRefs.next();
                Function caller = manager.getFunctionContaining(ref.getFromAddress());
                println("THUMB_REF " + ref.getFromAddress() + " " + ref.getReferenceType()
                    + " CALLER=" + describe(caller));
            }
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

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
