// Recover the production nonvolatile recovery/calibration envelope and merge rules.
// @category Firmware

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.StringDataInstance;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1NVEvidence extends GhidraScript {
    // These Thumb entries were recovered from the system command dispatch and the embedded
    // NV_RECOVER diagnostics. Several sit next to inline strings, so creating them explicitly
    // keeps the evidence reproducible even when auto-analysis mistakes code for data.
    private static final long[] FUNCTION_ENTRIES = {
        0x29cdc, // low-level optical event dispatcher used by hard ADT
        0x2b218, // hard ADT wear transition and 16-byte event producer
        0x2d324, // low-level wear-detect status getter
        0x2f880, // consumer of configuration UInt32 at offset 0x4c
        0x30e6c, // consumer of configuration byte at offset 0x70
        0x3cd24, // consumer/updater of offsets 0x74 and 0x78
        0x3cd80, // higher-level optical wear/ADT topic callback
        0x3ce1c, // wear-state history update
        0x3ce44, // living-object confirmation callback
        0x3ceec, // ADT topic record normalization
        0x3d06c, // wear history lookup
        0x3d0c0, // ADT topic unsubscribe
        0x3d0fc, // raw-HR/wear-LED gate
        0x3d150, // ADT topic subscription
        0x3d1b8, // sleep-status input to wear fusion
        0x3d268, // wear-on IR/object confirmation path
        0x3d45c, // wear-off/object/living confirmation path
        0x3e938, // touch dispatcher consumer of offset 0x70
        0x46b20, // consumer of configuration byte at offset 0x70
        0x46d10, // consumer of configuration byte at offset 0x70
        0x46dcc, // consumer of configuration byte at offset 0x70
        0x489e6, // consumer of configuration byte at offset 0x70
        0x48ba4, // consumer of offsets 0x74 and 0x78
        0x48bd0, // updater of offsets 0x74 and 0x78
        0x48c68, // updater of configuration UInt32 at offset 0x74
        0x42bbe, // linker veneer that branches to the compiled factory restore routine
        0x5d87c, // table-driven CRC-16/MODBUS, seed 0xffff
        0x62388, // configuration-record initialization/migration
        0x62840, // power-configuration validation consumer
        0x628f6, // configuration byte at offset 0x70 updater
        0x62a5c, // consolidated calibration/configuration consumer
        0x62bec, // configuration UInt32 at offset 0x4c consumer/updater
        0x62db0, // configuration byte at offset 0x70 updater
        0x66c4c, // consumer of configuration byte at offset 0x70
        0x6a2a0, // installs optical callback-table slot 0x14
        0x6a2b0, // installs optical callback-table slot 0x10
        0x6a2c0, // installs optical callback-table slot 0x18
        0x6a2d0, // installs optical callback-table slot 0x04
        0x6a2e0, // installs optical callback-table slot 0x00
        0x6a2f0, // installs optical callback-table slot 0x1c
        0x6a300, // installs optical callback-table slot 0x08
        0x6a310, // installs optical callback-table slot 0x0c
        0x6f228, // accelerometer-calibration producer
        0x6f304, // factory accelerometer subscription callback/start routine
        0x734e8, // lower-level NV flush/commit path
        0x73688, // commit wrapper used after a table restore
        0x73930, // fixed-record read helper
        0x73968, // fixed-record write helper
        0x7b634, // build and validate the 0x74-byte local recovery body
        0x7b9c8, // three-Int16 accelerometer-calibration getter
        0x7b9ec, // configuration byte at offset 0x78 getter
        0x7ba08, // configuration UInt32 at offset 0x74 getter
        0x7ba24, // configuration byte at offset 0x70 getter
        0x7ba40, // product BSN getter
        0x7ba78, // product SN getter
        0x7badc, // six-byte temperature-calibration getter
        0x7bb44, // battery-type getter
        0x7bb5c, // voltage-compensation nonzero predicate
        0x7bb7c, // signed voltage-compensation getter
        0x7bbe8, // allocate and report command-2 recovery envelope
        0x7bd68, // CRC-check and fill-only-if-local-invalid merge
        0x7c450, // command/length dispatcher
        0x7c52c, // restore product defaults selected from MAC-derived table
        0x7c8b0, // three-Int16 accelerometer-calibration setter
        0x7c8e4, // configuration byte at offset 0x78 setter
        0x7c910, // configuration UInt32 at offset 0x74 setter
        0x7c93c, // configuration byte at offset 0x70 setter
        0x7ca44, // configuration UInt32 at offset 0x4c setter
        0x8156c, // consumer/updater of configuration byte at offset 0x78
        0x815e4, // adjacent factory gray-channel callback
        0x8165c, // PPG open-mode dispatcher, including gray=8 and aging=9
        0x89d88, // accelerometer internal-topic registration
        0x89e30, // ADT five-value accumulator at state offset 0xd8
        0x89e50, // aging three-value setter at state offset 0xcc
        0x89e8c, // gray three-value setter at state offset 0xc0
        0x89ec8, // HR backing-state setter at offset 0x00
        0x89ed8, // SpO2 backing-state setter at offset 0x10
        0x89eec, // complete PPG internal-topic registry and payload sizes
        0x8a01c, // raw-HR 30-value accumulator at state offset 0x40
        0x8a03c, // HRV backing-state setter at offset 0x28
        0x8a054, // wear living-object byte setter at offsets 0xbc/0xbd
        0x839b4, // system nvRecover outbound wrapper
        0x84150, // system command handler/unwrapper
        0x91270, // direct consumer of configuration byte at offset 0x70
        0x91290, // inverse consumer of configuration byte at offset 0x70
        0x90fac, // factory accelerometer worker registration
        0x96a7c, // late-init consumer of configuration byte at offset 0x70
        0x96ad0  // late-init consumer of configuration byte at offset 0x78
    };

    private static final String[] TARGETS = {
        "NV_RECOVER",
        "invalid battery_type",
        "invalid voltage_compensation",
        "invalid ring_size",
        "invalid product_bsn_len",
        "set product bsn",
        "set product sn",
        "set temp cal",
        "set acc cal",
        "crc mismatch",
        "NV_RESTORE",
        "not found in restore table",
        "CMD_SYSTEM_NV_RECOVER",
        "IQS7211E_Init: comp divider",
        "ppg open type",
        "raw_hr",
        "GH_NADT_pre",
        "wear on event",
        "wear off event",
        "algo wear",
        "aging",
        "gray"
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();

        for (long entry : FUNCTION_ENTRIES) {
            Address address = toAddr(entry);
            Function function = functions.getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
            }
            println("EXPLICIT_FUNCTION " + address + " " + describe(function));
            enqueueWithCallers(queue, function, functions);
        }

        for (String target : TARGETS) {
            List<Data> matches = findStrings(target);
            println("\n=== TARGET: " + target + " (" + matches.size() + ") ===");
            for (Data data : matches) {
                String value = StringDataInstance.getStringDataInstance(data).getStringValue();
                println("STRING " + data.getAddress() + " " + sanitize(value));
                ReferenceIterator refs = currentProgram.getReferenceManager()
                    .getReferencesTo(data.getAddress());
                while (refs.hasNext()) {
                    Reference ref = refs.next();
                    Function function = functions.getFunctionContaining(ref.getFromAddress());
                    println("  XREF " + ref.getFromAddress() + " " + ref.getReferenceType()
                        + " FUNCTION=" + describe(function));
                    enqueueWithCallers(queue, function, functions);
                }
            }
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        decompiler.toggleSyntaxTree(true);
        if (!decompiler.openProgram(currentProgram)) {
            printerr("Decompiler setup failed");
            return;
        }
        for (Function function : queue) {
            println("\n--- " + describe(function) + " ---");
            DecompileResults results = decompiler.decompileFunction(function, 90, monitor);
            if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                println(results.getDecompiledFunction().getC());
            } else {
                println("DECOMPILE_FAILED: " + results.getErrorMessage());
            }
        }
        decompiler.dispose();
    }

    private void enqueueWithCallers(
            Set<Function> queue,
            Function function,
            FunctionManager functions) {
        if (function == null || !queue.add(function)) {
            return;
        }
        ReferenceIterator callers = currentProgram.getReferenceManager()
            .getReferencesTo(function.getEntryPoint());
        while (callers.hasNext()) {
            Reference ref = callers.next();
            Function caller = functions.getFunctionContaining(ref.getFromAddress());
            println("    CALLER " + ref.getFromAddress() + " " + ref.getReferenceType()
                + " FUNCTION=" + describe(caller));
            if (caller != null) {
                queue.add(caller);
            }
        }
    }

    private List<Data> findStrings(String needle) {
        List<Data> matches = new ArrayList<>();
        for (Data data : currentProgram.getListing().getDefinedData(true)) {
            if (!data.hasStringValue()) {
                continue;
            }
            String value = StringDataInstance.getStringDataInstance(data).getStringValue();
            if (value != null && value.toLowerCase().contains(needle.toLowerCase())) {
                matches.add(data);
            }
        }
        return matches;
    }

    private String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }

    private String sanitize(String value) {
        return value.replace("\r", "\\r").replace("\n", "\\n");
    }
}
