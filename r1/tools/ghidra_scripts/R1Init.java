// Initialize a raw R1 image as Cortex-M Thumb code before auto-analysis.
// @category Firmware

import java.math.BigInteger;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.symbol.SourceType;

public class R1Init extends GhidraScript {
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

        Address reset = toAddr(0x27488);
        disassemble(reset);
        if (getFunctionAt(reset) == null) {
            createFunction(reset, "reset_handler");
        }
        currentProgram.getSymbolTable().addExternalEntryPoint(reset);
        createLabel(reset, "reset_handler", true, SourceType.USER_DEFINED);
        println("Configured Thumb mode and reset entry point at " + reset);
    }
}
