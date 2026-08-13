// Recover the production ST25DV NFC, GPO, mailbox, RF-field, and charging path.
// @category Firmware

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.StringDataInstance;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class R1NFCEvidence extends GhidraScript {
    private static final long[] FUNCTION_ENTRIES = {
        0x31b46, 0x31c56, 0x31cb6, 0x31d36, 0x31d52, 0x31d88,
        0x31dc8, 0x31e0e, 0x31e22,
        0x44be4, 0x44bec, 0x44c58, 0x44c64, 0x44c6e, 0x44c78,
        0x44c84, 0x44c8a, 0x44c90, 0x44c9c, 0x44ce8,
        0x502c4, 0x50384, 0x503b4, 0x50464, 0x504c0, 0x504d8,
        0x50510, 0x50534, 0x50618, 0x5061c, 0x5069e, 0x506a4,
        0x50708, 0x5074c, 0x50750, 0x50758, 0x5079c, 0x507a0,
        0x5083c, 0x50d00, 0x50d3c, 0x51260,
        0x5d1d8, 0x5d1f4, 0x65b4c, 0x70ee4,
        0x7719c, 0x771b0, 0x771e2, 0x77214, 0x77220, 0x77240,
        0x77250, 0x7725c, 0x77268, 0x77274, 0x77290, 0x7729c,
        0x772a8, 0x77430, 0x77764, 0x77be0, 0x77c50, 0x77ce4, 0x77cf0,
        0x77cfc, 0x77d08, 0x77d20, 0x7803e, 0x784f0,
        0x7b9c8, 0x7b9ec, 0x7ba08, 0x7ba24, 0x7ba40, 0x7ba78,
        0x7badc, 0x8345c, 0x91270, 0x91290, 0x913fc,
        0x96a54, 0x96a60, 0x96a7c, 0x96ad0, 0x96cc8,
        0x31fd0, 0x42d1c, 0x42d26, 0x42d2e, 0x42ec4, 0x42ed8,
        0x45f3c, 0x461cc, 0x47f10, 0x93504, 0x93514
    };

    private static final String[] TARGETS = {
        "ST25DVxxKC_GetGPO2_ALL",
        "st25dvxxkc_set_gpo",
        "nfc_st25dvxxkc_init",
        "nfctag_id",
        "mailbox free or empty",
        "stop nfc field get right adc",
        "nfc_protocol_control_dock_adv",
        "NFC_CHARGE_EVENT_STDCMD_IRQ_HANDLER",
        "NFC_CHARGE_EVENT_NOT_CHARGING",
        "NFC_CHARGE_EVENT_CHARGING_BATTERY_UPDATA",
        "nfc_charge_task_msg_send",
        "pmic_isns_voltage",
        "vpmic_isns_adc",
        "bc_nfc_st25dv_device_chip_id",
        "nfc_gpo_irq",
        "vnfc_rect_adc"
    };

    @Override
    protected void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        Set<Function> queue = new LinkedHashSet<>();

        long nfcObject = 0x20016b08L;
        long inboundBuffer = nfcObject + 0x38L;
        long nextGlobal = 0x20016b54L;
        long chargeTaskState = Integer.toUnsignedLong(
            currentProgram.getMemory().getInt(toAddr(0x46464)));
        long queuedMessageState = Integer.toUnsignedLong(
            currentProgram.getMemory().getInt(toAddr(0x93510)));
        println("GLOBAL_LAYOUT nfcObject=" + hex(nfcObject)
            + " inboundBuffer=" + hex(inboundBuffer)
            + " nextGlobal=" + hex(nextGlobal)
            + " provenCapacity=" + (nextGlobal - inboundBuffer));
        println("TASK_STATE chargeConsumer=" + hex(chargeTaskState)
            + " queuedMessageProducer=" + hex(queuedMessageState)
            + " distinct=" + (chargeTaskState != queuedMessageState));

        for (long raw : FUNCTION_ENTRIES) {
            Function function = functions.getFunctionAt(toAddr(raw));
            if (function == null) {
                disassemble(toAddr(raw));
                function = createFunction(toAddr(raw), null);
            }
            println("FUNCTION_ENTRY " + toAddr(raw) + " " + describe(function));
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

    private String hex(long value) {
        return String.format("0x%08x", value);
    }
}
