import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.pcode.PcodeOp;
import java.util.HashMap;

public class ProbeCskyMovih extends GhidraScript {
    public void run() throws Exception {
        disassemble(toAddr(0));
        Instruction insn = getInstructionAt(toAddr(0));
        println("PROBE_INSTRUCTION=" + insn);
        for (PcodeOp op : insn.getPcode()) println("PROBE_PCODE=" + op);
        HashMap<String, Long> values = new HashMap<>();
        long result = -1;
        for (PcodeOp op : insn.getPcode()) {
            long value = op.getInput(0).isConstant() ? op.getInput(0).getOffset() : values.get(op.getInput(0).toString());
            if (op.getOpcode() == PcodeOp.INT_LEFT) value <<= op.getInput(1).getOffset();
            else if (op.getOpcode() != PcodeOp.INT_ZEXT && op.getOpcode() != PcodeOp.COPY) throw new IllegalStateException("Unexpected opcode");
            result = value & ((1L << (op.getOutput().getSize() * 8)) - 1);
            values.put(op.getOutput().toString(), result);
        }
        long expected = ((long)0xa0a0 << 16) & 0xffffffffL;
        println("PROBE_RESULT=" + Long.toHexString(result) + " EXPECTED=" + Long.toHexString(expected));
        if (result != expected) throw new IllegalStateException("Incorrect high-immediate semantics");
    }
}
