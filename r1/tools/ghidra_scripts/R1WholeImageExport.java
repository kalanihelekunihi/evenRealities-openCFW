// Export a complete, address-indexed R1 decompilation corpus from the current Ghidra program.
//
// Script arguments:
//   0: output directory
//   1: image label (for example "application" or "bootloader")
//
// This script is intentionally read-only with respect to firmware and hardware. It writes only
// analysis artifacts beneath the caller-selected output directory.
// @category Firmware

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.framework.Application;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

public class R1WholeImageExport extends GhidraScript {
    private static final int DECOMPILE_TIMEOUT_SECONDS = 45;

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            throw new IllegalArgumentException("usage: R1WholeImageExport.java OUTPUT_DIR IMAGE_LABEL");
        }

        File outputDir = new File(args[0]);
        String imageLabel = args[1];
        Files.createDirectories(outputDir.toPath());

        recoverVectorEntries();

        List<Function> functions = new ArrayList<>();
        FunctionIterator functionIterator = currentProgram.getFunctionManager().getFunctions(true);
        while (functionIterator.hasNext()) {
            functions.add(functionIterator.next());
        }
        Collections.sort(functions, Comparator.comparing(Function::getEntryPoint));

        exportMemoryMap(new File(outputDir, "memory-blocks.csv"));
        exportFunctions(new File(outputDir, "functions.csv"), functions);
        exportSymbols(new File(outputDir, "symbols.csv"));
        exportCallGraph(new File(outputDir, "call-graph.csv"), functions);
        exportDisassembly(new File(outputDir, "disassembly.s"));
        DecompileStats stats = exportDecompilerOutput(
            new File(outputDir, "decompiler-output.c"),
            new File(outputDir, "decompiler-failures.csv"),
            functions
        );
        exportSummary(new File(outputDir, "analysis-summary.json"), imageLabel, functions, stats);

        println("R1 whole-image export complete: " + functions.size() + " functions -> " + outputDir);
    }

    private void recoverVectorEntries() throws Exception {
        Memory memory = currentProgram.getMemory();
        Address base = memory.getMinAddress();
        long min = base.getOffset();
        long max = memory.getMaxAddress().getOffset();
        int vectorWords = (int)Math.min(64, memory.getSize() / 4);
        for (int index = 1; index < vectorWords; index++) {
            long value = Integer.toUnsignedLong(memory.getInt(base.add(index * 4L)));
            long entry = value & ~1L;
            if ((value & 1L) == 0 || entry < min || entry > max) {
                continue;
            }
            Address address = toAddr(entry);
            disassemble(address);
            Function function = getFunctionAt(address);
            if (function == null) {
                function = createFunction(address, null);
            }
            if (function != null && index == 1) {
                function.setName("reset_handler", SourceType.USER_DEFINED);
            }
            currentProgram.getSymbolTable().addExternalEntryPoint(address);
        }
    }

    private void exportMemoryMap(File file) throws IOException {
        try (BufferedWriter writer = writer(file)) {
            writer.write("name,start,end,size,initialized,read,write,execute,volatile\n");
            for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
                writer.write(csv(block.getName()) + "," + hex(block.getStart()) + "," +
                    hex(block.getEnd()) + "," + block.getSize() + "," + block.isInitialized() +
                    "," + block.isRead() + "," + block.isWrite() + "," + block.isExecute() +
                    "," + block.isVolatile() + "\n");
            }
        }
    }

    private void exportFunctions(File file, List<Function> functions) throws IOException {
        try (BufferedWriter writer = writer(file)) {
            writer.write("entry,end,size,name,namespace,calling_convention,parameters,return_type,thunk,no_return,external\n");
            for (Function function : functions) {
                writer.write(hex(function.getEntryPoint()) + "," +
                    hex(function.getBody().getMaxAddress()) + "," +
                    function.getBody().getNumAddresses() + "," +
                    csv(function.getName()) + "," +
                    csv(function.getParentNamespace().getName(true)) + "," +
                    csv(function.getCallingConventionName()) + "," +
                    function.getParameterCount() + "," +
                    csv(function.getReturnType().getDisplayName()) + "," +
                    function.isThunk() + "," + function.hasNoReturn() + "," + function.isExternal() + "\n");
            }
        }
    }

    private void exportSymbols(File file) throws IOException {
        try (BufferedWriter writer = writer(file)) {
            writer.write("address,name,namespace,type,source,primary,dynamic,external_entry\n");
            SymbolIterator iterator = currentProgram.getSymbolTable().getAllSymbols(true);
            while (iterator.hasNext()) {
                Symbol symbol = iterator.next();
                writer.write(hex(symbol.getAddress()) + "," + csv(symbol.getName()) + "," +
                    csv(symbol.getParentNamespace().getName(true)) + "," +
                    csv(symbol.getSymbolType().toString()) + "," +
                    csv(symbol.getSource().toString()) + "," + symbol.isPrimary() + "," +
                    symbol.isDynamic() + "," + symbol.isExternalEntryPoint() + "\n");
            }
        }
    }

    private void exportCallGraph(File file, List<Function> functions) throws IOException {
        try (BufferedWriter writer = writer(file)) {
            writer.write("caller_entry,caller_name,from_address,to_address,reference_type,callee_entry,callee_name\n");
            for (Function caller : functions) {
                InstructionIterator instructions = currentProgram.getListing().getInstructions(caller.getBody(), true);
                while (instructions.hasNext()) {
                    Instruction instruction = instructions.next();
                    Reference[] references = currentProgram.getReferenceManager()
                        .getReferencesFrom(instruction.getAddress());
                    for (Reference reference : references) {
                        if (!reference.getReferenceType().isCall()) {
                            continue;
                        }
                        Function callee = currentProgram.getFunctionManager()
                            .getFunctionAt(reference.getToAddress());
                        writer.write(hex(caller.getEntryPoint()) + "," + csv(caller.getName()) + "," +
                            hex(reference.getFromAddress()) + "," + hex(reference.getToAddress()) + "," +
                            csv(reference.getReferenceType().toString()) + "," +
                            (callee == null ? "" : hex(callee.getEntryPoint())) + "," +
                            (callee == null ? "" : csv(callee.getName())) + "\n");
                    }
                }
            }
        }
    }

    private void exportDisassembly(File file) throws Exception {
        Listing listing = currentProgram.getListing();
        try (BufferedWriter writer = writer(file)) {
            writer.write("/* Address-complete Ghidra instruction listing. Bytes not decoded as instructions\n");
            writer.write(" * remain represented by the exact byte-rebuild corpus. */\n\n");
            InstructionIterator iterator = listing.getInstructions(true);
            while (iterator.hasNext()) {
                Instruction instruction = iterator.next();
                byte[] bytes = instruction.getBytes();
                writer.write(hex(instruction.getAddress()));
                writer.write("  ");
                writer.write(bytesToHex(bytes));
                for (int i = bytes.length; i < 8; i++) {
                    writer.write("  ");
                }
                writer.write("  ");
                writer.write(instruction.toString());
                writer.write("\n");
            }
        }
    }

    private DecompileStats exportDecompilerOutput(
        File outputFile,
        File failuresFile,
        List<Function> functions
    ) throws IOException {
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            throw new IOException("Ghidra decompiler could not open the current program");
        }

        int succeeded = 0;
        int failed = 0;
        try (BufferedWriter output = writer(outputFile); BufferedWriter failures = writer(failuresFile)) {
            output.write("/*\n");
            output.write(" * Machine-generated Ghidra C-like decompilation. This is analysis output, not\n");
            output.write(" * recovered original source. Types, names, volatile qualifiers, inline boundaries,\n");
            output.write(" * and undefined-behavior assumptions require manual validation before semantic use.\n");
            output.write(" */\n\n");
            failures.write("entry,name,error\n");

            int index = 0;
            for (Function function : functions) {
                index++;
                if (monitor.isCancelled()) {
                    break;
                }
                monitor.setMessage("Decompiling " + index + "/" + functions.size() + " " + function.getName());
                DecompileResults results = decompiler.decompileFunction(
                    function,
                    DECOMPILE_TIMEOUT_SECONDS,
                    monitor
                );
                output.write("\n/* ================================================================\n");
                output.write(" * entry: " + hex(function.getEntryPoint()) + "\n");
                output.write(" * end:   " + hex(function.getBody().getMaxAddress()) + "\n");
                output.write(" * size:  " + function.getBody().getNumAddresses() + " bytes\n");
                output.write(" * name:  " + function.getName() + "\n");
                output.write(" * ================================================================ */\n");
                if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                    output.write(results.getDecompiledFunction().getC());
                    output.write("\n");
                    succeeded++;
                } else {
                    String error = results.getErrorMessage();
                    output.write("/* DECOMPILE_FAILED: " + sanitizeComment(error) + " */\n");
                    failures.write(hex(function.getEntryPoint()) + "," + csv(function.getName()) + "," +
                        csv(error) + "\n");
                    failed++;
                }
            }
        } finally {
            decompiler.dispose();
        }
        return new DecompileStats(succeeded, failed);
    }

    private void exportSummary(
        File file,
        String imageLabel,
        List<Function> functions,
        DecompileStats stats
    ) throws Exception {
        Memory memory = currentProgram.getMemory();
        Listing listing = currentProgram.getListing();
        long instructionBytes = 0;
        long instructionCount = 0;
        InstructionIterator iterator = listing.getInstructions(true);
        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();
            instructionBytes += instruction.getLength();
            instructionCount++;
        }

        long functionBytes = 0;
        AddressSet functionUnion = new AddressSet();
        for (Function function : functions) {
            functionUnion.add(function.getBody());
        }
        functionBytes = functionUnion.getNumAddresses();

        Map<String, Object> values = new LinkedHashMap<>();
        values.put("image_label", imageLabel);
        values.put("program_name", currentProgram.getName());
        values.put("language_id", currentProgram.getLanguageID().toString());
        values.put("compiler_spec_id", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        values.put("minimum_address", hex(memory.getMinAddress()));
        values.put("maximum_address", hex(memory.getMaxAddress()));
        values.put("memory_bytes", memory.getSize());
        values.put("function_count", functions.size());
        values.put("function_body_unique_bytes", functionBytes);
        values.put("instruction_count", instructionCount);
        values.put("instruction_bytes", instructionBytes);
        values.put("decompile_succeeded", stats.succeeded);
        values.put("decompile_failed", stats.failed);
        values.put("analysis_tool", "Ghidra " + ghidraVersion());

        try (BufferedWriter writer = writer(file)) {
            writer.write("{\n");
            int index = 0;
            for (Map.Entry<String, Object> entry : values.entrySet()) {
                writer.write("  \"");
                writer.write(jsonEscape(entry.getKey()));
                writer.write("\": ");
                Object value = entry.getValue();
                if (value instanceof Number || value instanceof Boolean) {
                    writer.write(value.toString());
                } else {
                    writer.write("\"");
                    writer.write(jsonEscape(String.valueOf(value)));
                    writer.write("\"");
                }
                writer.write(++index == values.size() ? "\n" : ",\n");
            }
            writer.write("}\n");
        }
    }

    private String ghidraVersion() {
        return Application.getApplicationVersion();
    }

    private BufferedWriter writer(File file) throws IOException {
        return new BufferedWriter(new FileWriter(file, StandardCharsets.UTF_8));
    }

    private String hex(Address address) {
        return String.format("0x%08x", address.getOffset());
    }

    private String bytesToHex(byte[] bytes) {
        StringBuilder builder = new StringBuilder();
        for (byte value : bytes) {
            builder.append(String.format("%02x", value & 0xff));
        }
        return builder.toString();
    }

    private String csv(String value) {
        if (value == null) {
            return "";
        }
        return "\"" + value.replace("\"", "\"\"").replace("\r", " ").replace("\n", " ") + "\"";
    }

    private String sanitizeComment(String value) {
        if (value == null) {
            return "unknown error";
        }
        return value.replace("*/", "* /").replace("\r", " ").replace("\n", " ");
    }

    private String jsonEscape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"")
            .replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t");
    }

    private static class DecompileStats {
        final int succeeded;
        final int failed;

        DecompileStats(int succeeded, int failed) {
            this.succeeded = succeeded;
            this.failed = failed;
        }
    }
}
