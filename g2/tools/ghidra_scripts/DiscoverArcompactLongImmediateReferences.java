// Discover ARCompact halfword-swapped long-immediate references to fixed values.
// The probe retries the legal 16-bit and 32-bit opcode starts independently.
// Use only on a disposable project because candidate retries clear nearby listing.
// @category openCFW

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;

public class DiscoverArcompactLongImmediateReferences extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException("expected target [target ...]");
        }
        Memory memory = currentProgram.getMemory();
        for (String argument : arguments) {
            long target = Long.decode(argument) & 0xffff_ffffL;
            byte[] encoded = {
                (byte)((target >>> 16) & 0xff),
                (byte)((target >>> 24) & 0xff),
                (byte)(target & 0xff),
                (byte)((target >>> 8) & 0xff),
            };
            int rawMatches = 0;
            int instructionCandidates = 0;
            for (MemoryBlock block : memory.getBlocks()) {
                Address end = block.getEnd().subtract(3);
                for (Address cursor = block.getStart();
                     cursor.compareTo(end) <= 0 && !monitor.isCancelled();
                     cursor = cursor.add(1)) {
                    if (!matches(memory, cursor, encoded)) {
                        continue;
                    }
                    rawMatches += 1;
                    println("OPENCFW_ARC_LIMM_RAW target=" + hex(target)
                        + " immediate=" + cursor);
                    for (int opcodeBytes : new int[] { 4, 2 }) {
                        Address candidate = cursor.subtract(opcodeBytes);
                        clearListing(candidate, cursor.add(3));
                        boolean decoded = disassemble(candidate);
                        Instruction instruction = getInstructionAt(candidate);
                        boolean exactLength = instruction != null
                            && instruction.getLength() == opcodeBytes + 4;
                        if (exactLength) {
                            instructionCandidates += 1;
                        }
                        println("OPENCFW_ARC_LIMM_CANDIDATE target=" + hex(target)
                            + " immediate=" + cursor
                            + " opcode_bytes=" + opcodeBytes
                            + " decoded=" + decoded
                            + " exact_length=" + exactLength
                            + " instruction="
                            + (instruction == null ? "none" : instruction.toString()));
                    }
                }
            }
            println("OPENCFW_ARC_LIMM_SUMMARY target=" + hex(target)
                + " raw_matches=" + rawMatches
                + " exact_length_candidates=" + instructionCandidates);
        }
    }

    private boolean matches(Memory memory, Address address, byte[] pattern)
            throws Exception {
        for (int index = 0; index < pattern.length; ++index) {
            if (memory.getByte(address.add(index)) != pattern[index]) {
                return false;
            }
        }
        return true;
    }

    private String hex(long value) {
        return String.format("0x%08x", value);
    }
}
