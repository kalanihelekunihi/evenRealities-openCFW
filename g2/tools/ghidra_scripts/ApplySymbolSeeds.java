// SPDX-License-Identifier: MIT
//
// Apply naming seeds (g2/symbols/<payload>.tsv) to the current program.
//
// Usage:
//   -postScript ApplySymbolSeeds.java <seeds.tsv> [address-offset]
//
// For every row with an address inside the program, the script creates a
// function there if none exists (Thumb targets are marked with the TMode
// context register when the language has one). It then applies the seed name
// as the primary symbol, unless a name is already set by a stronger source.
// Rows without a name only create the function. The optional offset is added
// to every seed address, for images loaded at a different base.
// A summary line "SEEDS applied=<n> created=<n> skipped=<n>" is printed.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import java.io.BufferedReader;
import java.io.FileReader;
import java.math.BigInteger;

public class ApplySymbolSeeds extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            throw new IllegalArgumentException("usage: ApplySymbolSeeds.java <seeds.tsv> [offset]");
        }
        long offset = args.length > 1 ? Long.decode(args[1]) : 0L;
        Register tmode = currentProgram.getProgramContext().getRegister("TMode");
        int applied = 0, created = 0, skipped = 0;
        try (BufferedReader reader = new BufferedReader(new FileReader(args[0]))) {
            String header = reader.readLine();
            String line;
            while ((line = reader.readLine()) != null) {
                String[] cols = line.split("\t", -1);
                if (cols.length < 4 || !cols[0].startsWith("0x")) {
                    skipped++;
                    continue;
                }
                long value = Long.decode(cols[0]) + offset;
                Address address = toAddr(value & ~1L);
                if (!currentProgram.getMemory().contains(address)) {
                    skipped++;
                    continue;
                }
                Function function = getFunctionAt(address);
                if (function == null) {
                    if (tmode != null && getInstructionAt(address) == null) {
                        try {
                            currentProgram.getProgramContext().setValue(tmode, address, address, BigInteger.ONE);
                        } catch (Exception conflict) {
                            // An existing instruction already fixes the mode here.
                        }
                    }
                    disassemble(address);
                    function = createFunction(address, null);
                    if (function == null) {
                        skipped++;
                        continue;
                    }
                    created++;
                }
                String name = cols[3].trim();
                if (!name.isEmpty() && function.getSymbol().getSource() != SourceType.USER_DEFINED) {
                    try {
                        function.setName(name.replaceAll("[^A-Za-z0-9_.:]", "_"), SourceType.IMPORTED);
                        applied++;
                    } catch (Exception duplicate) {
                        skipped++;
                    }
                }
            }
        }
        println("SEEDS applied=" + applied + " created=" + created + " skipped=" + skipped);
    }
}
