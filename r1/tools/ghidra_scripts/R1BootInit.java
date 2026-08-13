// Initialize a raw R1 nRF52840 bootloader image as Cortex-M Thumb code.
// Import the binary at its linked base (0x000f8000) before running this script.
// @category Firmware

import java.math.BigInteger;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.symbol.SourceType;

public class R1BootInit extends GhidraScript {
    @Override
    protected void run() throws Exception {
        Register tMode = currentProgram.getLanguage().getRegister("TMode");
        if (tMode == null) {
            throw new IllegalStateException("ARM TMode register was not found");
        }
        currentProgram.getProgramContext().setValue(
            tMode,
            currentProgram.getMemory().getMinAddress(),
            currentProgram.getMemory().getMaxAddress(),
            BigInteger.ONE
        );

        Address vectorBase = currentProgram.getMemory().getMinAddress();
        long resetVector = Integer.toUnsignedLong(
            currentProgram.getMemory().getInt(vectorBase.add(4))
        );
        Address reset = toAddr(resetVector & ~1L);
        if (!currentProgram.getMemory().contains(reset)) {
            throw new IllegalStateException("Reset vector is outside the imported bootloader");
        }
        disassemble(reset);
        if (getFunctionAt(reset) == null) {
            createFunction(reset, "reset_handler");
        }
        currentProgram.getSymbolTable().addExternalEntryPoint(reset);
        createLabel(reset, "reset_handler", true, SourceType.USER_DEFINED);
        println("Configured Thumb mode and bootloader reset entry point at " + reset);
    }
}
