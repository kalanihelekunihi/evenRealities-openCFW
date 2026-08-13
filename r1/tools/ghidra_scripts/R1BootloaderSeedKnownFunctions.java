// Seed source-level function boundaries that Ghidra cannot infer from optimized
// unconditional Thumb tail branches, then apply evidence-backed names.
// @category Firmware

import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.Map;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class R1BootloaderSeedKnownFunctions extends GhidraScript {
    private static final long[] TAIL_TARGETS = {
        0x000f8346L,
        0x000f8360L,
        0x000f837aL,
        0x000f83a4L,
        0x000fc3e4L,
        0x000fb740L,
        0x000fc244L,
        0x000fd6a0L,
        0x000fbed4L,
        0x000fbf00L,
        0x000fcf20L,
        0x000fbe48L,
        0x000fae44L,
        0x000fbf90L,
        0x000fc33cL,
        0x000fd104L,
        0x000fd41aL,
        0x000fc7e4L,
        0x000fc83cL,
        0x000fc894L,
        // Thumb targets recovered from immutable callback/API tables. Ghidra
        // decodes each body but does not create these indirect-only functions.
        0x000fa54cL,
        0x000fa594L,
        0x000fa640L,
        0x000fa99cL,
        0x000facd4L,
        0x000fad18L,
        0x000fad28L,
        0x000fc684L,
        0x000fc718L,
        // Seed thunk destinations before the indirect decoder table thunks so
        // Ghidra does not fold the destination body into the thunk function.
        0x000fc90aL,
        0x000fc934L,
        0x000fc75aL,
        0x000fc760L,
        0x000fc766L,
        0x000fd298L,
        0x000fd29cL,
        0x000fd6e4L,
        0x000fd6f4L,
        0x000fd7c8L,
        0x000fd7ccL,
        0x000fd7d0L,
    };

    private static Map<Long, String> knownNames() {
        Map<Long, String> names = new LinkedHashMap<>();
        names.put(0x000f83c4L, "SVC_Handler");
        names.put(0x000fc3e4L, "nrf_svc_handler_c");
        names.put(0x000f83d8L, "Reset_Handler");
        names.put(0x000f9a10L, "main");
        names.put(0x000f9cacL, "dfu_advertising_name_get");
        names.put(0x000f9d78L, "nrf_bootloader_app_activate");
        names.put(0x000f9f50L, "nrf_bootloader_bl_activate");
        names.put(0x000fa870L, "nrf_bootloader_app_is_valid");
        names.put(0x000fab04L, "gap_params_init");
        names.put(0x000faf56L, "nrf_bootloader_app_start_final");
        names.put(0x000fb004L, "nrf_bootloader_acl_add");
        names.put(0x000fb044L, "nrf_bootloader_fw_activate");
        names.put(0x000fb0b8L, "nrf_bootloader_init");
        names.put(0x000fb740L, "nrf_dfu_mbr_copy_bl");
        names.put(0x000fb930L, "bootloader_adv_name_record_valid");
        names.put(0x000fb950L, "nrf_dfu_settings_adv_name_write");
        names.put(0x000fb9d8L, "nrf_dfu_settings_reinit");
        names.put(0x000fbb76L, "nrf_dfu_validation_boot_validate");
        names.put(0x000fbd68L, "nrf_dfu_validation_prevalidate");
        names.put(0x000fbdb0L, "nrf_dfu_validation_signature_check");
        names.put(0x000fbe48L, "nrf_dfu_ver_validation_check");
        names.put(0x000fc4dcL, "nrf_dfu_data_object_create");
        names.put(0x000fc5c8L, "nrf_dfu_data_object_write");
        names.put(0x000fcc2cL, "nrf_dfu_init_command_decode_callback");
        names.put(0x000fcf20L, "nrf_dfu_validation_postvalidate_impl");
        names.put(0x000fd2a0L, "nrf_bootloader_sd_activate");
        return names;
    }

    @Override
    public void run() throws Exception {
        Register tMode = currentProgram.getRegister("TMode");
        int created = 0;
        for (long raw : TAIL_TARGETS) {
            Address address = toAddr(raw);
            if (tMode != null && getInstructionAt(address) == null) {
                currentProgram.getProgramContext().setValue(
                    tMode, address, address, BigInteger.ONE
                );
            }
            disassemble(address);
            Function function = getFunctionAt(address);
            if (function == null) {
                function = createFunction(address, null);
                if (function != null) {
                    created++;
                }
            }
        }

        int named = 0;
        for (Map.Entry<Long, String> entry : knownNames().entrySet()) {
            Address address = toAddr(entry.getKey());
            Function function = getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
            }
            if (function != null) {
                function.setName(entry.getValue(), SourceType.USER_DEFINED);
                named++;
            }
        }
        println("R1_BOOTLOADER_SEED created=" + created + " named=" + named);
    }
}
