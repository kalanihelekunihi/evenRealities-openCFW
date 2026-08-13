// Export a reproducible whole-image census and Ghidra C decompilation for the
// live Even Realities R1 nRF52840 bootloader.
//
// Usage (after raw-binary import at 0x000f8000):
//   -postScript R1BootloaderWholeImageExport.java /absolute/output/directory
//
// @category Firmware

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.DataType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class R1BootloaderWholeImageExport extends GhidraScript {
    private static final long IMAGE_BASE = 0x000f8000L;
    private static final long LOGICAL_END = 0x000fdf64L;
    private static final long DUMP_END = 0x000fe000L;
    private static final int VECTOR_WORDS = 64;
    private static final int DECOMPILE_TIMEOUT_SECONDS = 60;

    private BufferedWriter open(File directory, String name) throws IOException {
        return new BufferedWriter(new FileWriter(new File(directory, name)));
    }

    private String csv(String value) {
        if (value == null) {
            return "";
        }
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }

    private String hex(long value) {
        return String.format(Locale.ROOT, "0x%08x", value);
    }

    private String ranges(AddressSetView set) {
        List<String> values = new ArrayList<>();
        AddressRangeIterator iterator = set.getAddressRanges();
        while (iterator.hasNext()) {
            AddressRange range = iterator.next();
            values.add(range.getMinAddress() + "-" + range.getMaxAddress());
        }
        return String.join(";", values);
    }

    private String joinedFunctions(Set<Function> functions) {
        List<Function> ordered = new ArrayList<>(functions);
        Collections.sort(ordered, Comparator.comparing(Function::getEntryPoint));
        List<String> values = new ArrayList<>();
        for (Function function : ordered) {
            values.add(function.getName() + "@" + function.getEntryPoint());
        }
        return String.join(";", values);
    }

    private long countBytes(AddressSetView set) {
        return set.getNumAddresses();
    }

    private String bodySha256(AddressSetView body) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        AddressRangeIterator iterator = body.getAddressRanges();
        while (iterator.hasNext()) {
            AddressRange range = iterator.next();
            long remaining = range.getLength();
            Address cursor = range.getMinAddress();
            while (remaining > 0) {
                int count = (int) Math.min(remaining, 4096);
                byte[] bytes = new byte[count];
                currentProgram.getMemory().getBytes(cursor, bytes);
                digest.update(bytes);
                cursor = cursor.add(count);
                remaining -= count;
            }
        }
        StringBuilder value = new StringBuilder();
        for (byte item : digest.digest()) {
            value.append(String.format(Locale.ROOT, "%02x", item & 0xff));
        }
        return value.toString();
    }

    private void exportVectors(File directory) throws Exception {
        try (BufferedWriter out = open(directory, "vectors.csv")) {
            out.write("index,slot_address,raw_value,target_address,thumb,in_image\n");
            Address base = toAddr(IMAGE_BASE);
            for (int index = 0; index < VECTOR_WORDS; index++) {
                Address slot = base.add((long) index * 4);
                long raw = Integer.toUnsignedLong(getInt(slot));
                long target = raw & ~1L;
                boolean thumb = (raw & 1L) != 0;
                boolean inImage = target >= IMAGE_BASE && target < LOGICAL_END;
                out.write(index + "," + hex(slot.getOffset()) + "," + hex(raw) + "," +
                    hex(target) + "," + thumb + "," + inImage + "\n");
            }
        }
    }

    private void exportFunctionsAndCalls(File directory, List<Function> functions)
            throws Exception {
        try (BufferedWriter functionOut = open(directory, "functions.csv");
             BufferedWriter callOut = open(directory, "callgraph.csv")) {
            functionOut.write(
                "entry,name,body_min,body_max,body_bytes,body_sha256,body_ranges,thunk,external," +
                "calling_functions,called_functions\n"
            );
            callOut.write("caller_entry,caller_name,callsite,callee_entry,callee_name,reference_type\n");
            for (Function function : functions) {
                AddressSetView body = function.getBody();
                Set<Function> callers = function.getCallingFunctions(monitor);
                Set<Function> callees = function.getCalledFunctions(monitor);
                functionOut.write(
                    hex(function.getEntryPoint().getOffset()) + "," + csv(function.getName()) + "," +
                    hex(body.getMinAddress().getOffset()) + "," +
                    hex(body.getMaxAddress().getOffset()) + "," +
                    countBytes(body) + "," + bodySha256(body) + "," + csv(ranges(body)) + "," +
                    function.isThunk() + "," + function.isExternal() + "," +
                    csv(joinedFunctions(callers)) + "," + csv(joinedFunctions(callees)) + "\n"
                );

                InstructionIterator instructions =
                    currentProgram.getListing().getInstructions(body, true);
                while (instructions.hasNext()) {
                    Instruction instruction = instructions.next();
                    Reference[] references = instruction.getReferencesFrom();
                    for (Reference reference : references) {
                        RefType type = reference.getReferenceType();
                        if (!type.isCall()) {
                            continue;
                        }
                        Function callee = currentProgram.getFunctionManager()
                            .getFunctionAt(reference.getToAddress());
                        callOut.write(
                            hex(function.getEntryPoint().getOffset()) + "," +
                            csv(function.getName()) + "," +
                            hex(instruction.getAddress().getOffset()) + "," +
                            (callee == null ? hex(reference.getToAddress().getOffset()) :
                                hex(callee.getEntryPoint().getOffset())) + "," +
                            csv(callee == null ? "<unresolved>" : callee.getName()) + "," +
                            csv(type.getName()) + "\n"
                        );
                    }
                }
            }
        }
    }

    private int exportDecompilation(File directory, List<Function> functions) throws Exception {
        int failed = 0;
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        decompiler.setSimplificationStyle("decompile");
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException("could not open program in the decompiler");
        }
        try (BufferedWriter out = open(directory, "r1_bootloader_ghidra.c")) {
            out.write("/*\n");
            out.write(" * Mechanical Ghidra 12.1.2 decompilation of the live R1 bootloader.\n");
            out.write(" * Base: 0x000f8000; logical bytes: 0x5f64; dump bytes: 0x6000.\n");
            out.write(" * This is analysis pseudocode, not a claim of source-level identity.\n");
            out.write(" */\n\n");
            out.write("#include <stdbool.h>\n#include <stdint.h>\n\n");
            out.write("typedef uint8_t undefined1;\n");
            out.write("typedef uint16_t undefined2;\n");
            out.write("typedef uint32_t undefined4;\n");
            out.write("typedef uint64_t undefined8;\n");
            out.write("typedef uint8_t undefined;\n");
            out.write("typedef uint8_t byte;\n");
            out.write("typedef unsigned int uint;\n");
            out.write("typedef unsigned short ushort;\n");
            out.write("typedef unsigned long ulong;\n\n");
            for (Function function : functions) {
                out.write("\n/* ============================================================\n");
                out.write(" * entry: " + function.getEntryPoint() + "\n");
                out.write(" * name: " + function.getName() + "\n");
                out.write(" * body: " + ranges(function.getBody()) + "\n");
                out.write(" * ============================================================ */\n");
                DecompileResults result = decompiler.decompileFunction(
                    function, DECOMPILE_TIMEOUT_SECONDS, monitor
                );
                if (!result.decompileCompleted() || result.getDecompiledFunction() == null) {
                    failed++;
                    out.write("/* DECOMPILE_FAILED: " +
                        result.getErrorMessage().replace("*/", "* /") + " */\n");
                }
                else {
                    out.write(result.getDecompiledFunction().getC());
                    out.write("\n");
                }
            }
        }
        finally {
            decompiler.dispose();
        }
        return failed;
    }

    private AddressSet exportInstructions(File directory) throws Exception {
        AddressSet instructionBytes = new AddressSet();
        Address start = toAddr(IMAGE_BASE);
        Address end = toAddr(DUMP_END - 1);
        try (BufferedWriter out = open(directory, "instructions.tsv")) {
            out.write("address\tbytes\tmnemonic\toperands\tcontaining_function\n");
            InstructionIterator iterator =
                currentProgram.getListing().getInstructions(start, true);
            while (iterator.hasNext()) {
                Instruction instruction = iterator.next();
                if (instruction.getAddress().compareTo(end) > 0) {
                    break;
                }
                byte[] bytes = instruction.getBytes();
                StringBuilder byteText = new StringBuilder();
                for (byte value : bytes) {
                    byteText.append(String.format(Locale.ROOT, "%02x", value & 0xff));
                }
                Function owner = currentProgram.getFunctionManager()
                    .getFunctionContaining(instruction.getAddress());
                String rendered = instruction.toString();
                String mnemonic = instruction.getMnemonicString();
                String operands = rendered.length() > mnemonic.length()
                    ? rendered.substring(mnemonic.length()).trim() : "";
                out.write(hex(instruction.getAddress().getOffset()) + "\t" + byteText + "\t" +
                    mnemonic + "\t" + operands + "\t" +
                    (owner == null ? "" : owner.getName() + "@" + owner.getEntryPoint()) + "\n");
                instructionBytes.addRange(
                    instruction.getMinAddress(), instruction.getMaxAddress()
                );
            }
        }
        return instructionBytes;
    }

    private AddressSet exportData(File directory) throws Exception {
        AddressSet dataBytes = new AddressSet();
        Address start = toAddr(IMAGE_BASE);
        Address end = toAddr(DUMP_END - 1);
        try (BufferedWriter out = open(directory, "defined-data.csv")) {
            out.write("address,end,length,data_type,value\n");
            DataIterator iterator = currentProgram.getListing().getDefinedData(start, true);
            while (iterator.hasNext()) {
                Data data = iterator.next();
                if (data.getAddress().compareTo(end) > 0) {
                    break;
                }
                DataType type = data.getDataType();
                Object value = data.getValue();
                out.write(
                    hex(data.getAddress().getOffset()) + "," +
                    hex(data.getMaxAddress().getOffset()) + "," + data.getLength() + "," +
                    csv(type == null ? "" : type.getDisplayName()) + "," +
                    csv(value == null ? "" : value.toString()) + "\n"
                );
                dataBytes.addRange(data.getMinAddress(), data.getMaxAddress());
            }
        }
        return dataBytes;
    }

    private void exportSymbols(File directory) throws Exception {
        try (BufferedWriter out = open(directory, "symbols.csv")) {
            out.write("address,name,type,source,primary\n");
            SymbolIterator iterator = currentProgram.getSymbolTable().getAllSymbols(true);
            while (iterator.hasNext()) {
                Symbol symbol = iterator.next();
                Address address = symbol.getAddress();
                if (!address.isMemoryAddress()) {
                    continue;
                }
                long offset = address.getOffset();
                if (offset < IMAGE_BASE || offset >= DUMP_END) {
                    continue;
                }
                out.write(
                    hex(offset) + "," + csv(symbol.getName(true)) + "," +
                    csv(symbol.getSymbolType().toString()) + "," +
                    csv(symbol.getSource().toString()) + "," + symbol.isPrimary() + "\n"
                );
            }
        }
    }

    private void exportSummary(
            File directory,
            List<Function> functions,
            int decompileFailures,
            AddressSet instructionBytes,
            AddressSet dataBytes) throws Exception {
        AddressSet logical = new AddressSet(toAddr(IMAGE_BASE), toAddr(LOGICAL_END - 1));
        AddressSet functionBytes = new AddressSet();
        for (Function function : functions) {
            functionBytes.add(function.getBody());
        }
        AddressSet classified = new AddressSet(instructionBytes);
        classified.add(dataBytes);
        AddressSet unclassified = new AddressSet(logical);
        unclassified.delete(classified);
        try (BufferedWriter out = open(directory, "summary.json")) {
            out.write("{\n");
            out.write("  \"image_base\": \"" + hex(IMAGE_BASE) + "\",\n");
            out.write("  \"logical_end_exclusive\": \"" + hex(LOGICAL_END) + "\",\n");
            out.write("  \"dump_end_exclusive\": \"" + hex(DUMP_END) + "\",\n");
            out.write("  \"logical_bytes\": " + (LOGICAL_END - IMAGE_BASE) + ",\n");
            out.write("  \"dump_bytes\": " + (DUMP_END - IMAGE_BASE) + ",\n");
            out.write("  \"function_count\": " + functions.size() + ",\n");
            out.write("  \"decompile_failures\": " + decompileFailures + ",\n");
            out.write("  \"function_body_bytes_union\": " + functionBytes.getNumAddresses() + ",\n");
            out.write("  \"decoded_instruction_bytes\": " + instructionBytes.getNumAddresses() + ",\n");
            out.write("  \"defined_data_bytes\": " + dataBytes.getNumAddresses() + ",\n");
            out.write("  \"unclassified_logical_bytes\": " + unclassified.getNumAddresses() + ",\n");
            out.write("  \"unclassified_ranges\": " + csv(ranges(unclassified)) + "\n");
            out.write("}\n");
        }
    }

    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 1) {
            throw new IllegalArgumentException("expected one absolute output directory");
        }
        File directory = new File(arguments[0]);
        if (!directory.isAbsolute()) {
            throw new IllegalArgumentException("output directory must be absolute");
        }
        if (!directory.exists() && !directory.mkdirs()) {
            throw new IOException("could not create output directory " + directory);
        }

        List<Function> functions = new ArrayList<>();
        FunctionIterator iterator = currentProgram.getFunctionManager()
            .getFunctions(toAddr(IMAGE_BASE), true);
        while (iterator.hasNext()) {
            Function function = iterator.next();
            long entry = function.getEntryPoint().getOffset();
            if (entry >= DUMP_END) {
                break;
            }
            if (entry >= IMAGE_BASE) {
                functions.add(function);
            }
        }

        exportVectors(directory);
        exportFunctionsAndCalls(directory, functions);
        int failures = exportDecompilation(directory, functions);
        AddressSet instructionBytes = exportInstructions(directory);
        AddressSet dataBytes = exportData(directory);
        exportSymbols(directory);
        exportSummary(directory, functions, failures, instructionBytes, dataBytes);
        println(
            "R1_BOOTLOADER_EXPORT functions=" + functions.size() +
            " decompile_failures=" + failures +
            " output=" + directory
        );
    }
}
