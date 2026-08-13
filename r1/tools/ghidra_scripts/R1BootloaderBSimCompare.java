// Compare the live R1 bootloader with a symbol-bearing Nordic SDK reference
// program already imported into the same Ghidra project.
//
// Usage:
//   -postScript R1BootloaderBSimCompare.java \
//       /nrf52840_xxaa_s140.out /absolute/output/source-correlations-raw.csv
//
// The output is evidence, not an automatic renaming decision. BSim signatures
// are compiler-independent decompiler features, but high scores still require
// corroboration from constants, call topology, and source behavior.
// @category Firmware

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;

import generic.lsh.vector.LSHVector;
import generic.lsh.vector.LSHVectorFactory;
import generic.lsh.vector.VectorCompare;
import ghidra.app.decompiler.DecompileException;
import ghidra.app.script.GhidraScript;
import ghidra.features.bsim.query.FunctionDatabase;
import ghidra.features.bsim.query.GenSignatures;
import ghidra.features.bsim.query.LSHException;
import ghidra.features.bsim.query.client.Configuration;
import ghidra.features.bsim.query.description.FunctionDescription;
import ghidra.framework.model.DomainFile;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Program;

public class R1BootloaderBSimCompare extends GhidraScript {
    private static final long DEFAULT_IMAGE_BASE = 0x000f8000L;
    private static final long DEFAULT_IMAGE_END = 0x000fe000L;
    private static final int MATCHES_PER_FUNCTION = 12;
    private static final String TEMPLATE_NAME = "medium_nosize";

    private static class Signature {
        Function function;
        LSHVector vector;
        double selfSignificance;

        Signature(Function function, LSHVector vector, double selfSignificance) {
            this.function = function;
            this.vector = vector;
            this.selfSignificance = selfSignificance;
        }
    }

    private static class Match {
        Signature target;
        double similarity;
        double significance;

        Match(Signature target, double similarity, double significance) {
            this.target = target;
            this.similarity = similarity;
            this.significance = significance;
        }
    }

    private String csv(String value) {
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }

    private String hex(long value) {
        return String.format(Locale.ROOT, "0x%08x", value);
    }

    private LSHVectorFactory vectorFactory() throws LSHException {
        LSHVectorFactory factory = FunctionDatabase.generateLSHVectorFactory();
        Configuration configuration = FunctionDatabase.loadConfigurationTemplate(TEMPLATE_NAME);
        factory.set(
            configuration.weightfactory,
            configuration.idflookup,
            configuration.info.settings
        );
        return factory;
    }

    private List<Function> imageFunctions(Program program, long imageBase, long imageEnd) {
        List<Function> functions = new ArrayList<>();
        Address start = program.getAddressFactory().getDefaultAddressSpace()
            .getAddress(imageBase);
        FunctionIterator iterator = program.getFunctionManager().getFunctions(start, true);
        while (iterator.hasNext()) {
            Function function = iterator.next();
            long entry = function.getEntryPoint().getOffset();
            if (entry >= imageEnd) {
                break;
            }
            if (entry >= imageBase && !function.isExternal()) {
                functions.add(function);
            }
        }
        return functions;
    }

    private List<Signature> signatures(
            Program program,
            List<Function> functions,
            LSHVectorFactory factory) throws LSHException, DecompileException {
        GenSignatures generator = new GenSignatures(false);
        generator.setVectorFactory(factory);
        generator.openProgram(program, null, null, null, null, null);
        generator.scanFunctions(functions.iterator(), functions.size(), monitor);

        List<Signature> result = new ArrayList<>();
        Iterator<FunctionDescription> descriptions =
            generator.getDescriptionManager().listAllFunctions();
        while (descriptions.hasNext()) {
            FunctionDescription description = descriptions.next();
            Address address = program.getAddressFactory().getDefaultAddressSpace()
                .getAddress(description.getAddress());
            Function function = program.getFunctionManager().getFunctionAt(address);
            if (function == null) {
                continue;
            }
            LSHVector vector = description.getSignatureRecord().getLSHVector();
            result.add(new Signature(function, vector, factory.getSelfSignificance(vector)));
        }
        return result;
    }

    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 2 && arguments.length != 6) {
            throw new IllegalArgumentException(
                "expected reference project path, absolute output CSV, and optional " +
                "source/target start/end addresses"
            );
        }
        if (currentProgram == null) {
            throw new IllegalStateException("current R1 program is required");
        }

        DomainFile referenceFile = state.getProject().getProjectData().getFile(arguments[0]);
        if (referenceFile == null) {
            throw new IllegalArgumentException(
                "reference program not found in project: " + arguments[0]
            );
        }
        File output = new File(arguments[1]);
        if (!output.isAbsolute()) {
            throw new IllegalArgumentException("output CSV must be absolute");
        }
        File parent = output.getParentFile();
        if (parent != null && !parent.exists() && !parent.mkdirs()) {
            throw new IllegalStateException("could not create output directory " + parent);
        }

        long sourceBase = DEFAULT_IMAGE_BASE;
        long sourceEnd = DEFAULT_IMAGE_END;
        long targetBase = DEFAULT_IMAGE_BASE;
        long targetEnd = DEFAULT_IMAGE_END;
        if (arguments.length == 6) {
            sourceBase = Long.decode(arguments[2]);
            sourceEnd = Long.decode(arguments[3]);
            targetBase = Long.decode(arguments[4]);
            targetEnd = Long.decode(arguments[5]);
        }

        Program referenceProgram = null;
        try {
            referenceProgram = (Program) referenceFile.getDomainObject(
                this, false, false, monitor
            );
            LSHVectorFactory factory = vectorFactory();
            List<Signature> source = signatures(
                currentProgram,
                imageFunctions(currentProgram, sourceBase, sourceEnd),
                factory
            );
            List<Signature> target = signatures(
                referenceProgram,
                imageFunctions(referenceProgram, targetBase, targetEnd),
                factory
            );

            try (BufferedWriter writer = new BufferedWriter(new FileWriter(output))) {
                writer.write(
                    "r1_entry,r1_name,rank,reference_entry,reference_name," +
                    "similarity,significance,r1_self_significance," +
                    "reference_self_significance\n"
                );
                VectorCompare compare = new VectorCompare();
                for (Signature sourceSignature : source) {
                    List<Match> matches = new ArrayList<>();
                    for (Signature targetSignature : target) {
                        double similarity = sourceSignature.vector.compare(
                            targetSignature.vector, compare
                        );
                        double significance = factory.calculateSignificance(compare);
                        matches.add(new Match(
                            targetSignature, similarity, significance
                        ));
                    }
                    Collections.sort(matches, Comparator
                        .comparingDouble((Match item) -> item.significance).reversed()
                        .thenComparing(
                            Comparator.comparingDouble(
                                (Match item) -> item.similarity
                            ).reversed()
                        )
                        .thenComparing(item -> item.target.function.getEntryPoint()));
                    int limit = Math.min(MATCHES_PER_FUNCTION, matches.size());
                    for (int index = 0; index < limit; index++) {
                        Match match = matches.get(index);
                        writer.write(
                            hex(sourceSignature.function.getEntryPoint().getOffset()) + "," +
                            csv(sourceSignature.function.getName()) + "," + (index + 1) + "," +
                            hex(match.target.function.getEntryPoint().getOffset()) + "," +
                            csv(match.target.function.getName()) + "," +
                            String.format(Locale.ROOT, "%.9f", match.similarity) + "," +
                            String.format(Locale.ROOT, "%.9f", match.significance) + "," +
                            String.format(
                                Locale.ROOT, "%.9f", sourceSignature.selfSignificance
                            ) + "," +
                            String.format(
                                Locale.ROOT, "%.9f", match.target.selfSignificance
                            ) + "\n"
                        );
                    }
                }
            }
            println(
                "R1_BSIM_COMPARE source=" + source.size() +
                " reference=" + target.size() +
                " output=" + output
            );
        }
        finally {
            if (referenceProgram != null) {
                referenceProgram.release(this);
            }
        }
    }
}
