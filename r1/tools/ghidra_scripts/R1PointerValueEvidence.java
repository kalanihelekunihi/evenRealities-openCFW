// Find exact little-endian 32-bit values (typically scatter-loaded Thumb
// function pointers) and report their containing/preceding functions.
// Usage: -postScript R1PointerValueEvidence.java 0x5a9d1 0x5dce9
// @category Firmware

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.mem.Memory;

public class R1PointerValueEvidence extends GhidraScript {
    @Override
    protected void run() throws Exception {
        Memory memory = currentProgram.getMemory();
        FunctionManager functions = currentProgram.getFunctionManager();
        for (String argument : getScriptArgs()) {
            long value = Long.decode(argument) & 0xffffffffL;
            byte[] needle = new byte[] {
                (byte)value, (byte)(value >>> 8), (byte)(value >>> 16), (byte)(value >>> 24)
            };
            println("VALUE 0x" + Long.toHexString(value));
            Address cursor = currentProgram.getMinAddress();
            int count = 0;
            while (cursor != null) {
                Address hit = memory.findBytes(cursor, needle, null, true, monitor);
                if (hit == null) {
                    break;
                }
                Function containing = functions.getFunctionContaining(hit);
                FunctionIterator previous = functions.getFunctions(hit, false);
                Function preceding = previous.hasNext() ? previous.next() : null;
                println("  " + hit + " CONTAINING=" + describe(containing)
                    + " PRECEDING=" + describe(preceding));
                count++;
                cursor = hit.add(1);
            }
            println("COUNT " + count);
        }
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
