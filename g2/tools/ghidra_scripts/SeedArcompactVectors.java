// Seed raw ARCompact firmware analysis from a bounded vector/pointer table.
// @category openCFW

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.Memory;

import java.util.LinkedHashSet;
import java.util.Set;

public class SeedArcompactVectors extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length < 4) {
            throw new IllegalArgumentException(
                "expected table-start table-end image-start image-end [entry ...]"
            );
        }

        Address tableStart = toAddr(arguments[0]);
        Address tableEnd = toAddr(arguments[1]);
        long imageStart = Long.decode(arguments[2]);
        long imageEnd = Long.decode(arguments[3]);
        Memory memory = currentProgram.getMemory();
        Set<Long> targets = new LinkedHashSet<>();

        for (int index = 4; index < arguments.length; ++index) {
            long value = Long.decode(arguments[index]);
            if (value < imageStart || value >= imageEnd || (value & 1) != 0) {
                throw new IllegalArgumentException(
                    "explicit entry is outside the image or unaligned: " + arguments[index]
                );
            }
            targets.add(value);
        }

        for (Address cursor = tableStart;
             cursor.compareTo(tableEnd) < 0;
             cursor = cursor.add(4)) {
            long value = Integer.toUnsignedLong(memory.getInt(cursor));
            if (value >= imageStart && value < imageEnd && (value & 1) == 0) {
                targets.add(value);
            }
        }

        int created = 0;
        for (long value : targets) {
            Address target = toAddr(value);
            if (!memory.contains(target)) {
                throw new IllegalStateException("vector target is unmapped: " + target);
            }
            disassemble(target);
            Function function = getFunctionAt(target);
            if (function == null) {
                function = createFunction(target, "open_cfw_arc_vector_" + target);
                if (function != null) {
                    created += 1;
                }
            }
            println("OPENCFW_ARC_VECTOR " + cursorLabel(target));
        }
        println("OPENCFW_ARC_VECTOR_SUMMARY targets=" + targets.size()
            + " created=" + created);
    }

    private String cursorLabel(Address address) {
        return "0x" + address.toString(false, false);
    }
}
