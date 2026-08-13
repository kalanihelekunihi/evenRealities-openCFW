// Remove one or more accidentally-created function entries and clear only their
// instruction bodies. This is a project-repair helper, not a firmware mutation.
// Usage: -postScript R1RemoveFalseFunction.java 0x5a9cc
// @category Firmware

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;

public class R1RemoveFalseFunction extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        FunctionManager functions = currentProgram.getFunctionManager();
        for (String argument : arguments) {
            Address entry = toAddr(Long.decode(argument));
            Function function = functions.getFunctionAt(entry);
            if (function == null) {
                println("NO_FUNCTION " + entry);
                continue;
            }
            AddressSetView body = function.getBody();
            println("REMOVE " + function.getName() + "@" + entry + " BODY=" + body);
            functions.removeFunction(entry);
            clearListing(body);
        }
    }
}
