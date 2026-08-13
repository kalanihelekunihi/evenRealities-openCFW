// Decompile the production EUS/factory transport and its immediate dispatch/reply chain.
// @category Firmware

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1FactoryRoute extends GhidraScript {
    private static final long[] ADDRESSES = {
        // EUS notification transmitter and receive-state handler.
        0x526cc, 0x5d5e0,
        // Channel-1 callbacks, raw BLE transmitter, ingress, and structured response route.
        0x3d7ac, 0x3d7fc, 0x3dff8, 0x3e00e, 0x3e7a8,
        0x45f3c, 0x4d654, 0x625c0, 0x8967c,
        // Runtime-populated command 0xf2 dispatch targets (RAM table 0x20006c60).
        0x62c48, 0x62c5e, 0x62c74, 0x62c90, 0x62cd0, 0x62ce6,
        0x62cfc, 0x62d12, 0x62d28, 0x62d3e, 0x62d54, 0x62d6a,
        0x62d84, 0x62db0, 0x62dd4,
        // Immediate operations wrapped by those command 0xf2 handlers.
        0x5025c, 0x503b4, 0x50690, 0x508da, 0x50d2a, 0x50e1c,
        0x510d8, 0x51108, 0x5128c,
        0x913c8, 0x50870, 0x50892, 0x508b6, 0x7effe, 0x381c8,
        0x7c93c, 0x80e74,
        // Advertising/GATT initialization and negotiated-MTU lifecycle.
        0x48a28, 0x489e6, 0x78186, 0x781b4, 0x783b6, 0x7ce34,
        0x4d4ac, 0x4df18, 0x4e4b4,
        // Nordic buttonless-DFU application wrapper.
        0x4c92c,
        // eAT tokenizer/dispatcher and exact normal/factory BLE-name constructor.
        0x4f260, 0x4f6f8, 0x66c4c,
        // Factory task/queue and command dispatch candidates.
        0x33af8, 0x33dbc, 0x34064,
        // BLE service initialization containing the EUS event callback table.
        0x4e66c, 0x529bc,
        // Protocol-port initialization, EUS send/completion registration, and callback.
        0x830aa, 0x8316c, 0x832d4, 0x83448, 0x32408,
        // Phone application-auth state updates reached from system/pairAuth (subcommand 0x08).
        0x842ec, 0x4da28, 0x33850,
        0x4ed14, 0x4ed34, 0x4eddc, 0x4ef24, 0x4ef8c, 0x4eff8,
        0x4f040, 0x4f10c, 0x4f160, 0x4f1c4, 0x4f260,
        0x4f2bc, 0x4f2dc, 0x4f30c, 0x4f328, 0x4f348, 0x4f378,
        0x4f8bc, 0x4f8e0, 0x4f914, 0x4f928, 0x4f94c, 0x4f980
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
            printReferences(manager, address);
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

    private void printReferences(FunctionManager manager, Address address) {
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
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
