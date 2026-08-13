// Print exact discovered function bodies for version-pinned signature ranges.
// Usage: -postScript R1FunctionBoundaryEvidence.java 0x60680 0x68840
// @category Firmware

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;

public class R1FunctionBoundaryEvidence extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            printerr("Expected at least one function-entry address");
            return;
        }

        FunctionManager manager = currentProgram.getFunctionManager();
        for (String argument : arguments) {
            Address requested = toAddr(Long.decode(argument));
            Function function = manager.getFunctionAt(requested);
            if (function == null) {
                function = manager.getFunctionContaining(requested);
            }
            if (function == null) {
                println("NO_FUNCTION " + requested);
                continue;
            }
            AddressSetView body = function.getBody();
            println(function.getName()
                + " entry=" + function.getEntryPoint()
                + " min=" + body.getMinAddress()
                + " max_inclusive=" + body.getMaxAddress()
                + " bytes=" + body.getNumAddresses());
        }
    }
}
