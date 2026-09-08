// SPDX-License-Identifier: MIT
// Seed authenticated image-B candidates at their actual SRAM addresses.
// This produces analysis evidence only, not reviewed source ownership.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.SourceType;
import java.nio.file.Files;
import java.nio.file.Paths;

public class PrepareGx8002KnownFunctions extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("expected seed TSV");
        MemoryBlock block = currentProgram.getMemory().getBlock(toAddr(0x10003000L));
        if (block == null || block.getStart().getOffset() != 0x10003000L || block.getSize() != 82060) {
            throw new IllegalStateException("unexpected image-B memory extent");
        }
        currentProgram.getMemory().split(block, toAddr(0x1001651cL));
        block.setName("image_b_text");
        block.setRead(true);
        block.setWrite(false);
        block.setExecute(true);
        MemoryBlock data = currentProgram.getMemory().getBlock(toAddr(0x1001651cL));
        data.setName("image_b_data");
        data.setRead(true);
        data.setWrite(true);
        data.setExecute(false);
        // Analysis windows around authenticated MMIO addresses, not RAM.
        // Volatility prevents the decompiler merging distinct hardware accesses.
        long[] mmio = {0xa0003000L, 0xa0005000L, 0xa0a00000L, 0xe000f000L};
        for (long base : mmio) {
            MemoryBlock registers = currentProgram.getMemory().createUninitializedBlock(
                "mmio_" + Long.toHexString(base), toAddr(base), 0x1000, false);
            registers.setRead(true);
            registers.setWrite(true);
            registers.setExecute(false);
            registers.setVolatile(true);
        }
        for (String line : Files.readAllLines(Paths.get(args[0]))) {
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] fields = line.split("\t");
            if (fields.length != 2) throw new IllegalArgumentException("invalid seed row");
            Address entry = toAddr(fields[0]);
            if (entry.getOffset() < 0x10003000L || entry.getOffset() >= 0x1001651cL) {
                throw new IllegalArgumentException("seed outside reviewed text range");
            }
            disassemble(entry);
            Function function = getFunctionAt(entry);
            if (function == null) function = createFunction(entry, fields[1]);
            if (function == null) throw new IllegalStateException("could not create " + entry);
            function.setName(fields[1], SourceType.USER_DEFINED);
        }
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            if (!instruction.getMnemonicString().equals("lrw")) continue;
            for (Object operand : instruction.getOpObjects(1)) {
                Address literal;
                if (operand instanceof Address) literal = (Address) operand;
                else if (operand instanceof Scalar) literal = toAddr(((Scalar)operand).getUnsignedValue());
                else continue;
                if (block.contains(literal) && getInstructionContaining(literal) == null &&
                    currentProgram.getListing().getDefinedDataAt(literal) == null) {
                    createDWord(literal);
                }
            }
            for (Reference reference : instruction.getReferencesFrom()) {
                Address literal = reference.getToAddress();
                if (reference.getReferenceType().isRead() && block.contains(literal) &&
                    getInstructionContaining(literal) == null &&
                    currentProgram.getListing().getDefinedDataAt(literal) == null) {
                    createDWord(literal);
                }
            }
        }
    }
}
