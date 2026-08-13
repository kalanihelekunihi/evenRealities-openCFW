// Decompile every analyzed function whose entry lies in one half-open chunk.
// @category openCFW

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

public class DumpDecompilationChunk extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 3) {
            throw new IllegalArgumentException(
                "expected inclusive start, exclusive end, and per-function timeout seconds"
            );
        }
        Address start = toAddr(arguments[0]);
        Address end = toAddr(arguments[1]);
        int timeout = Integer.decode(arguments[2]);
        if (start.compareTo(end) >= 0 || timeout <= 0) {
            throw new IllegalArgumentException("invalid chunk or timeout") ;
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        decompiler.setSimplificationStyle("decompile");
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException("could not open program in decompiler");
        }

        int seen = 0;
        int completed = 0;
        int failed = 0;
        println("OPENCFW_CHUNK_BEGIN start=" + start + " end=" + end);
        try {
            FunctionIterator functions =
                currentProgram.getFunctionManager().getFunctions(start, true);
            while (functions.hasNext()) {
                Function function = functions.next();
                Address entry = function.getEntryPoint();
                if (entry.compareTo(start) < 0) {
                    continue;
                }
                if (entry.compareTo(end) >= 0) {
                    break;
                }
                seen++;
                println(
                    "OPENCFW_FUNCTION_BEGIN entry=" + entry +
                    " body_start=" + function.getBody().getMinAddress() +
                    " body_end=" + function.getBody().getMaxAddress() +
                    " name=" + function.getName()
                );
                DecompileResults result = decompiler.decompileFunction(
                    function, timeout, monitor
                );
                if (!result.decompileCompleted()) {
                    failed++;
                    println(
                        "OPENCFW_DECOMPILE_ERROR entry=" + entry +
                        " message=" + result.getErrorMessage()
                    );
                }
                else {
                    completed++;
                    println(result.getDecompiledFunction().getC());
                }
                println("OPENCFW_FUNCTION_END entry=" + entry);
            }
        }
        finally {
            decompiler.dispose();
        }
        println(
            "OPENCFW_CHUNK_SUMMARY start=" + start + " end=" + end +
            " functions=" + seen + " completed=" + completed + " failed=" + failed
        );
    }
}
