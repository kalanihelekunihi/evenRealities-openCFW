// Export a complete function map, string census, string xrefs, and full
// decompilation for the G2 charging-case STM32G0 application.
// Deterministic: output depends only on the imported bytes and Ghidra 12.1.2.
// @category openCFW

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

public class BoxExportFunctionMap extends GhidraScript {

    private static final long APP_BASE = 0x08000000L;
    private static final long APP_SIZE = 55752L;
    private static final long APP_END = APP_BASE + APP_SIZE;

    private PrintWriter open(File dir, String name) throws Exception {
        return new PrintWriter(new OutputStreamWriter(
            new FileOutputStream(new File(dir, name)), StandardCharsets.UTF_8));
    }

    private String sha256(File f) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] buf = java.nio.file.Files.readAllBytes(f.toPath());
        byte[] dig = md.digest(buf);
        StringBuilder sb = new StringBuilder();
        for (byte b : dig) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    private String hex(long v) {
        return String.format("0x%08x", v);
    }

    private String joinHex(Set<Long> vals) {
        StringBuilder sb = new StringBuilder();
        boolean first = true;
        for (long v : vals) {
            if (!first) {
                sb.append(",");
            }
            sb.append(hex(v));
            first = false;
        }
        return sb.toString();
    }

    private int exportFunctions(File dir) throws Exception {
        int count = 0;
        try (PrintWriter fh = open(dir, "functions.tsv")) {
            fh.println("entry\tsize\tinstructions\tcallees\tdatarefs\tscalars");
            FunctionIterator functions =
                currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                Function function = functions.next();
                long entry = function.getEntryPoint().getOffset();
                Set<Long> callees = new TreeSet<>();
                Set<Long> datarefs = new TreeSet<>();
                Set<Long> scalars = new TreeSet<>();
                int ninsn = 0;
                InstructionIterator it = currentProgram.getListing()
                    .getInstructions(function.getBody(), true);
                while (it.hasNext()) {
                    Instruction ins = it.next();
                    ninsn++;
                    for (Address flow : ins.getFlows()) {
                        long t = flow.getOffset();
                        if (t != entry) {
                            callees.add(t);
                        }
                    }
                    for (Reference ref : ins.getReferencesFrom()) {
                        if (ref.isMemoryReference()) {
                            datarefs.add(ref.getToAddress().getOffset());
                        }
                    }
                    for (int op = 0; op < ins.getNumOperands(); op++) {
                        for (Object obj : ins.getOpObjects(op)) {
                            if (obj instanceof Scalar) {
                                scalars.add(((Scalar) obj).getUnsignedValue());
                            }
                        }
                    }
                }
                fh.println(hex(entry) + "\t"
                    + function.getBody().getNumAddresses() + "\t" + ninsn + "\t"
                    + joinHex(callees) + "\t" + joinHex(datarefs) + "\t"
                    + joinHex(scalars));
                count++;
            }
        }
        return count;
    }

    private int[] exportStrings(File dir) throws Exception {
        Memory mem = currentProgram.getMemory();
        byte[] data = new byte[(int) APP_SIZE];
        for (int i = 0; i < (int) APP_SIZE; i++) {
            data[i] = mem.getByte(toAddr(APP_BASE + i));
        }
        List<long[]> strings = new ArrayList<>();
        List<String> texts = new ArrayList<>();
        int i = 0;
        while (i < data.length) {
            int b = data[i] & 0xFF;
            if (b >= 0x20 && b < 0x7F) {
                int j = i;
                while (j < data.length) {
                    int c = data[j] & 0xFF;
                    if (c < 0x20 || c >= 0x7F) {
                        break;
                    }
                    j++;
                }
                if (j - i >= 6) {
                    strings.add(new long[]{APP_BASE + i, j - i});
                    texts.add(new String(data, i, j - i, StandardCharsets.US_ASCII));
                }
                i = j;
            } else {
                i++;
            }
        }
        int totalRefs = 0;
        try (PrintWriter fh = open(dir, "strings.tsv");
             PrintWriter fx = open(dir, "string_xrefs.tsv")) {
            fh.println("vaddr\ttext\treference_count");
            fx.println("string_vaddr\treferencing_functions");
            for (int k = 0; k < strings.size(); k++) {
                long vaddr = strings.get(k)[0];
                Address addr = toAddr(vaddr);
                Set<Long> entries = new TreeSet<>();
                int cnt = 0;
                ReferenceIterator refs =
                    currentProgram.getReferenceManager().getReferencesTo(addr);
                while (refs.hasNext()) {
                    Reference ref = refs.next();
                    cnt++;
                    Function container = currentProgram.getFunctionManager()
                        .getFunctionContaining(ref.getFromAddress());
                    if (container != null) {
                        entries.add(container.getEntryPoint().getOffset());
                    }
                }
                totalRefs += cnt;
                String safe = texts.get(k).replace('\t', ' ');
                fh.println(hex(vaddr) + "\t" + safe + "\t" + cnt);
                fx.println(hex(vaddr) + "\t" + joinHex(entries));
            }
        }
        return new int[]{strings.size(), totalRefs};
    }

    private String exportDecompilation(File dir) throws Exception {
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        decompiler.setSimplificationStyle("decompile");
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException("could not open program in decompiler");
        }
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        try (PrintWriter fh = open(dir, "decomp.c")) {
            FunctionIterator functions =
                currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                Function function = functions.next();
                long entry = function.getEntryPoint().getOffset();
                String c;
                try {
                    DecompileResults result = decompiler.decompileFunction(
                        function, 60, monitor);
                    if (result.decompileCompleted()) {
                        c = result.getDecompiledFunction().getC();
                    } else {
                        c = "/* decompile failed: " + result.getErrorMessage()
                            + " */";
                    }
                } catch (Exception e) {
                    c = "/* decompile error: " + e.getMessage() + " */";
                }
                String block = "/* FUN " + hex(entry) + " " + function.getName()
                    + " */\n" + c + "\n";
                fh.println(block);
                md.update(block.getBytes(StandardCharsets.UTF_8));
            }
        } finally {
            decompiler.dispose();
        }
        byte[] dig = md.digest();
        StringBuilder sb = new StringBuilder();
        for (byte b : dig) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 1) {
            throw new IllegalArgumentException("expected output directory");
        }
        File dir = new File(arguments[0]);
        if (!dir.isDirectory()) {
            throw new IllegalArgumentException("not a directory: " + dir);
        }
        int nfunc = exportFunctions(dir);
        int[] strStats = exportStrings(dir);
        String decompSha = exportDecompilation(dir);
        try (PrintWriter fh = open(dir, "meta.tsv")) {
            fh.println("key\tvalue");
            fh.println("image_base\t" + hex(APP_BASE));
            fh.println("image_bytes\t" + APP_SIZE);
            fh.println("functions\t" + nfunc);
            fh.println("strings\t" + strStats[0]);
            fh.println("string_references\t" + strStats[1]);
            fh.println("decomp_c_sha256\t" + decompSha);
            fh.println("language\t" + currentProgram.getLanguageID());
        }
        String[] names = {"functions.tsv", "strings.tsv", "string_xrefs.tsv",
            "decomp.c", "meta.tsv"};
        try (PrintWriter fh = open(dir, "SHA256SUMS")) {
            for (String name : names) {
                fh.println(sha256(new File(dir, name)) + "  " + name);
            }
        }
        println("OPENCFW_BOX_EXPORT_SUMMARY functions=" + nfunc
            + " strings=" + strStats[0] + " string_refs=" + strStats[1]);
    }
}
