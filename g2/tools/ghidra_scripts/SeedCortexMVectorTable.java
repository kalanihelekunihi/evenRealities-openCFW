// Deterministically seed Cortex-M vector handlers before whole-image analysis.
// @category openCFW

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;

import java.math.BigInteger;
import java.util.HashSet;
import java.util.Set;

public class SeedCortexMVectorTable extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 3) {
            throw new IllegalArgumentException(
                "expected vector base, image end-exclusive, and vector-word count"
            );
        }
        Address vectorBase = toAddr(arguments[0]);
        long imageStart = vectorBase.getOffset();
        long imageEnd = Long.decode(arguments[1]);
        int vectorWords = Integer.decode(arguments[2]);
        Register tMode = currentProgram.getRegister("TMode");
        Set<Long> seeded = new HashSet<>();
        int rejected = 0;

        for (int index = 1; index < vectorWords; index++) {
            Address slot = vectorBase.add((long) index * 4);
            long raw = Integer.toUnsignedLong(getInt(slot));
            long targetValue = raw & ~1L;
            if ((raw & 1L) == 0 || targetValue < imageStart || targetValue >= imageEnd) {
                rejected++;
                continue;
            }
            if (!seeded.add(targetValue)) {
                continue;
            }
            Address target = toAddr(targetValue);
            if (tMode != null) {
                currentProgram.getProgramContext().setValue(
                    tMode, target, target, BigInteger.ONE
                );
            }
            disassemble(target);
            Function function = getFunctionAt(target);
            if (function == null) {
                function = createFunction(target, null);
            }
            if (function == null) {
                println("OPENCFW_VECTOR_SEED_FAILED index=" + index + " target=" + target);
            }
        }
        println(
            "OPENCFW_VECTOR_SEED_SUMMARY unique=" + seeded.size() +
            " rejected=" + rejected + " words=" + vectorWords
        );
    }
}
