// Recover producer, logging, publication, and consumer evidence for stock optical result records.
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

public class R1OpticalResultEvidence extends GhidraScript {
    private static final long[] DATA_ADDRESSES = {
        0x4f318, // heartrate:%d
        0x4f38c, // hrv:%d,%d,%d,%d
        0x4f91c, // spo2:%d
        0xc02f4, // once: hr, con, sig
        0xc0334, // same, short log form
        0xc0390, // timing: hr, con, sig
        0xc03d0, // same, short log form
        0xc04fc, // once: spo2, r_value, con, level, hr, mark
        0xc0550, // same, short log form
        0xc05a0, // timing: spo2, r_value, con, level, hr, mark
        0xc05f8  // same, short log form
    };

    private static final long[] FUNCTION_ENTRIES = {
        0x499e0, // HR validity gate
        0x499f0, // one-shot HR result callback
        0x49b60, // timing HR result callback
        0x4aa98, // SpO2 calibration/clamp transform
        0x4aac0, // SpO2 validity gate
        0x4abec, // one-shot SpO2 result callback
        0x4ada0, // timing SpO2 result callback
        0x4f30c, // factory HR text callback
        0x4f378, // factory HRV text callback
        0x4f914, // factory SpO2 text callback
        0x89ec8, // HR producer wrapper
        0x89ed8, // SpO2 producer wrapper
        0x8a03c  // HRV producer wrapper
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();

        for (long raw : DATA_ADDRESSES) {
            Address target = toAddr(raw);
            println("DATA " + target);
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
            Function function = functions.getFunctionAt(toAddr(raw));
            if (function == null) {
                disassemble(toAddr(raw));
                function = createFunction(toAddr(raw), null);
            }
            println("FUNCTION " + toAddr(raw) + " " + describe(function));
            if (function != null) {
                queue.add(function);
                ReferenceIterator callers = currentProgram.getReferenceManager()
                    .getReferencesTo(function.getEntryPoint());
                while (callers.hasNext()) {
                    Reference reference = callers.next();
                    Function caller = functions.getFunctionContaining(reference.getFromAddress());
                    println("  CALLER " + reference.getFromAddress() + " "
                        + reference.getReferenceType() + " FUNCTION=" + describe(caller));
                    if (caller != null) {
                        queue.add(caller);
                    }
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

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
