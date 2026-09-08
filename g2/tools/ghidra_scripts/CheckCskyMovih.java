// SPDX-License-Identifier: MIT
// Regression check against the actual codec's movih r3,0xa0a0 instruction.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.Varnode;
import java.util.HashMap;
import java.util.Map;

public class CheckCskyMovih extends GhidraScript {
    private final Map<String, Long> values = new HashMap<>();
    private long value(Varnode node) {
        if (node.isConstant()) return node.getOffset();
        Long result = values.get(node.toString());
        if (result == null) throw new IllegalStateException("nonconstant movih input " + node);
        return result;
    }
    @Override
    protected void run() throws Exception {
        Instruction instruction = getInstructionAt(toAddr(0x1000588cL));
        if (instruction == null || !instruction.getMnemonicString().equals("movih")) {
            throw new IllegalStateException("missing authenticated movih instruction");
        }
        byte[] bytes = instruction.getBytes();
        if (bytes.length != 4 || (bytes[0]&255)!=0x23 || (bytes[1]&255)!=0xea ||
            (bytes[2]&255)!=0xa0 || (bytes[3]&255)!=0xa0) {
            throw new IllegalStateException("movih oracle bytes changed");
        }
        long result = -1;
        for (PcodeOp op : instruction.getPcode()) {
            switch (op.getOpcode()) {
                case PcodeOp.COPY:
                case PcodeOp.INT_ZEXT: result = value(op.getInput(0)); break;
                case PcodeOp.INT_LEFT: result = value(op.getInput(0)) << value(op.getInput(1)); break;
                default: throw new IllegalStateException("unsupported movih pcode " + op);
            }
            Varnode target = op.getOutput();
            if (target == null || target.getSize() > 4) throw new IllegalStateException("bad movih output");
            result &= (1L << (target.getSize()*8)) - 1;
            values.put(target.toString(), result);
        }
        if (result != 0xa0a00000L) throw new IllegalStateException("movih immediate was truncated: " + result);
        println("CSKY_MOVIH_CHECK_OK 0xa0a00000");
    }
}
