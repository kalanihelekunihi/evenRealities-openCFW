// SPDX-License-Identifier: GPL-3.0-only
//
// Export every defined function in the current program as decompilation
// evidence, in a deterministic, machine-readable form.
//
// Usage:
//   -postScript ExportAllFunctionDecomp.java <output-dir> [shard-index] [shard-count]
//
// Emits, into <output-dir>:
//   functions-<shard>.jsonl  one record per function, sorted by entry point
//   decomp/<entry>.c         decompiled C for that function
//
// Each JSONL record carries entry point, body bounds, byte length, name,
// signature, calling convention, callees, and the SHA-256 of the function's
// bytes as read from the program image, so a later ingest can pin the
// decompilation to the exact stock bytes it came from.

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

public class ExportAllFunctionDecomp extends GhidraScript {

    private static final int DECOMPILE_TIMEOUT_SECONDS = 60;

    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException(
                "usage: ExportAllFunctionDecomp <output-dir> [shard-index] [shard-count]"
            );
        }

        Path outputRoot = Paths.get(arguments[0]);
        int shardIndex = arguments.length > 1 ? Integer.parseInt(arguments[1]) : 0;
        int shardCount = arguments.length > 2 ? Integer.parseInt(arguments[2]) : 1;
        if (shardCount < 1 || shardIndex < 0 || shardIndex >= shardCount) {
            throw new IllegalArgumentException("invalid shard selection");
        }

        Path decompRoot = outputRoot.resolve("decomp");
        Files.createDirectories(decompRoot);

        List<Function> selected = new ArrayList<>();
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        int ordinal = 0;
        while (functions.hasNext()) {
            Function function = functions.next();
            if (ordinal++ % shardCount == shardIndex) {
                selected.add(function);
            }
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        decompiler.setSimplificationStyle("decompile");
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException("could not open program in decompiler");
        }

        String shardName = String.format("%03d", shardIndex);
        Path recordPath = outputRoot.resolve("functions-" + shardName + ".jsonl");

        int exported = 0;
        int failed = 0;
        try (BufferedWriter records = Files.newBufferedWriter(recordPath, StandardCharsets.UTF_8)) {
            for (Function function : selected) {
                if (monitor.isCancelled()) {
                    break;
                }
                try {
                    if (exportFunction(decompiler, function, decompRoot, records)) {
                        exported++;
                    } else {
                        failed++;
                    }
                } catch (Exception failure) {
                    failed++;
                    println("EXPORT_ERROR " + function.getEntryPoint() + " " + failure);
                }
            }
        } finally {
            decompiler.dispose();
        }

        println("EXPORTED " + exported + " FAILED " + failed + " SHARD " + shardName);
    }

    private boolean exportFunction(
        DecompInterface decompiler,
        Function function,
        Path decompRoot,
        BufferedWriter records
    ) throws IOException {
        Address entry = function.getEntryPoint();
        AddressSetView body = function.getBody();
        Address minimum = body.getMinAddress();
        Address maximum = body.getMaxAddress();

        DecompileResults results = decompiler.decompileFunction(
            function, DECOMPILE_TIMEOUT_SECONDS, monitor
        );

        String code = null;
        String signature = function.getPrototypeString(true, false);
        String error = null;
        if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
            code = results.getDecompiledFunction().getC();
            String decompiledSignature = results.getDecompiledFunction().getSignature();
            if (decompiledSignature != null && !decompiledSignature.isEmpty()) {
                signature = decompiledSignature;
            }
        } else {
            error = results.getErrorMessage();
        }

        String entryKey = entry.toString();
        if (code != null) {
            Path codePath = decompRoot.resolve(entryKey + ".c");
            Files.write(codePath, code.getBytes(StandardCharsets.UTF_8));
        }

        byte[] bytes = readBody(body);
        String digest = bytes == null ? null : sha256(bytes);

        StringBuilder record = new StringBuilder();
        record.append('{');
        appendString(record, "entry", entryKey);
        record.append(',');
        appendString(record, "name", function.getName());
        record.append(',');
        appendString(record, "body_start", minimum == null ? null : minimum.toString());
        record.append(',');
        appendString(record, "body_end_inclusive", maximum == null ? null : maximum.toString());
        record.append(",\"body_bytes\":").append(body.getNumAddresses());
        record.append(',');
        appendString(record, "signature", signature);
        record.append(',');
        appendString(record, "calling_convention", function.getCallingConventionName());
        record.append(",\"thunk\":").append(function.isThunk());
        record.append(",\"external\":").append(function.isExternal());
        record.append(",\"body_sha256\":");
        if (digest == null) {
            record.append("null");
        } else {
            record.append('"').append(digest).append('"');
        }
        record.append(",\"ranges\":[");
        Iterator<ghidra.program.model.address.AddressRange> ranges = body.iterator();
        while (ranges.hasNext()) {
            ghidra.program.model.address.AddressRange range = ranges.next();
            record.append("[\"").append(range.getMinAddress()).append("\",\"")
                  .append(range.getMaxAddress()).append("\"]");
            if (ranges.hasNext()) {
                record.append(',');
            }
        }
        record.append(']');
        record.append(",\"callees\":[");
        Set<String> callees = new TreeSet<>();
        for (Function callee : function.getCalledFunctions(monitor)) {
            callees.add(callee.getEntryPoint().toString());
        }
        Iterator<String> calleeIterator = callees.iterator();
        while (calleeIterator.hasNext()) {
            record.append('"').append(calleeIterator.next()).append('"');
            if (calleeIterator.hasNext()) {
                record.append(',');
            }
        }
        record.append(']');
        record.append(",\"decompiled\":").append(code != null);
        if (error != null && !error.isEmpty()) {
            record.append(',');
            appendString(record, "error", error);
        }
        record.append('}');

        records.write(record.toString());
        records.newLine();
        return code != null;
    }

    private byte[] readBody(AddressSetView body) {
        Address minimum = body.getMinAddress();
        Address maximum = body.getMaxAddress();
        if (minimum == null || maximum == null) {
            return null;
        }
        long length = maximum.subtract(minimum) + 1;
        if (length <= 0 || length > (1 << 20)) {
            return null;
        }
        byte[] bytes = new byte[(int) length];
        try {
            currentProgram.getMemory().getBytes(minimum, bytes);
        } catch (Exception failure) {
            return null;
        }
        return bytes;
    }

    private static String sha256(byte[] data) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(data);
            StringBuilder text = new StringBuilder(hash.length * 2);
            for (byte value : hash) {
                text.append(Character.forDigit((value >> 4) & 0xF, 16));
                text.append(Character.forDigit(value & 0xF, 16));
            }
            return text.toString();
        } catch (Exception failure) {
            return null;
        }
    }

    private static void appendString(StringBuilder target, String key, String value) {
        target.append('"').append(key).append("\":");
        if (value == null) {
            target.append("null");
            return;
        }
        target.append('"');
        for (int index = 0; index < value.length(); index++) {
            char character = value.charAt(index);
            switch (character) {
                case '"':
                    target.append("\\\"");
                    break;
                case '\\':
                    target.append("\\\\");
                    break;
                case '\n':
                    target.append("\\n");
                    break;
                case '\r':
                    target.append("\\r");
                    break;
                case '\t':
                    target.append("\\t");
                    break;
                default:
                    if (character < 0x20) {
                        target.append(String.format("\\u%04x", (int) character));
                    } else {
                        target.append(character);
                    }
            }
        }
        target.append('"');
    }
}
