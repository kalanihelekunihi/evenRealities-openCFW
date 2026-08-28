// SPDX-License-Identifier: MIT
//
// Report a one-line census of the current program so a harvest driver can
// choose between candidate Ghidra projects deterministically.
//
// Usage:
//   -postScript ReportProgramCensus.java

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SymbolTable;

public class ReportProgramCensus extends GhidraScript {
    @Override
    public void run() throws Exception {
        long functions = 0;
        long named = 0;
        long bodyBytes = 0;
        long thunks = 0;

        FunctionIterator iterator = currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            Function function = iterator.next();
            functions++;
            if (function.isThunk()) {
                thunks++;
            }
            if (!function.getName().startsWith("FUN_")) {
                named++;
            }
            AddressSetView body = function.getBody();
            bodyBytes += body.getNumAddresses();
        }

        long memoryBytes = 0;
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            memoryBytes += block.getSize();
        }

        SymbolTable symbols = currentProgram.getSymbolTable();

        println(
            "CENSUS program=" + currentProgram.getName()
            + " executable_sha256=" + currentProgram.getExecutableSHA256()
            + " image_base=" + currentProgram.getImageBase()
            + " memory_bytes=" + memoryBytes
            + " functions=" + functions
            + " named_functions=" + named
            + " thunks=" + thunks
            + " function_body_bytes=" + bodyBytes
            + " symbols=" + symbols.getNumSymbols()
        );
    }
}
