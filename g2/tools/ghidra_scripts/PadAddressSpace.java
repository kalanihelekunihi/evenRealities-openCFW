// SPDX-License-Identifier: MIT
//
// Pad the mapped address space with additional uninitialized memory
// immediately after the imported image.
//
// Some functions' decompilation speculatively probes a byte or two past the
// last mapped address while resolving switch/jump-table bounds. Against a
// raw BinaryLoader import whose single block ends exactly at end-of-file,
// that probe throws "Trying to construct memory range beyond end of address
// space: ram" and the function is reported as a decompiler failure even
// though its own body is fully defined and correctly bounded. Reserving
// extra uninitialized address space (never given defined bytes, so it can
// never contribute instructions or data of its own) removes that artifact
// without changing what is analyzed.
//
// Usage:
//   -preScript PadAddressSpace.java <pad-byte-count>
//
// @category openCFW

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;

public class PadAddressSpace extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 1) {
            throw new IllegalArgumentException("expected pad byte count");
        }
        long padBytes = Long.decode(arguments[0]);
        Memory memory = currentProgram.getMemory();
        Address end = memory.getMaxAddress();
        Address padStart = end.add(1);
        memory.createUninitializedBlock("pad", padStart, padBytes, false);
        println("OPENCFW_PAD_SUMMARY start=" + padStart + " bytes=" + padBytes);
    }
}
