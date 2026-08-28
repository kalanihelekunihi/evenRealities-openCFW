// SPDX-License-Identifier: MIT
//
// Emit every Ghidra reference to one or more reviewed addresses.
// Usage:
//   -postScript DumpAddressReferences.java 0x004801FC 0x0048020C

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class DumpAddressReferences extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException(
                "expected one or more referenced addresses"
            );
        }

        for (String argument : arguments) {
            Address address = toAddr(argument);
            int count = 0;
            println("ADDRESS " + address);

            ReferenceIterator references =
                currentProgram.getReferenceManager().getReferencesTo(address);
            while (references.hasNext()) {
                Reference reference = references.next();
                Address from = reference.getFromAddress();
                Function containing = getFunctionContaining(from);
                CodeUnit codeUnit =
                    currentProgram.getListing().getCodeUnitContaining(from);
                println(
                    "REFERENCE " + from +
                    " " + reference.getReferenceType() +
                    " function=" +
                    (containing == null
                        ? "<none>"
                        : containing.getEntryPoint().toString()) +
                    " code_unit=" +
                    (codeUnit == null
                        ? "<none>"
                        : codeUnit.getAddress().toString())
                );
                ++count;
            }
            println("REFERENCE_COUNT " + count);
        }
    }
}
