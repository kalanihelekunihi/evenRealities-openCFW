// Apply an evidence ledger of recovered SDK/library names, then give every
// remaining stripped function an explicitly synthetic descriptive name.
//
// Usage:
//   -postScript R1BootloaderApplyNames.java /absolute/output/function-names.csv
// @category Firmware

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.symbol.SourceType;

public class R1BootloaderApplyNames extends GhidraScript {
    private static final long IMAGE_BASE = 0x000f8000L;
    private static final long IMAGE_END = 0x000fe000L;

    private static class RecoveredName {
        String name;
        String confidence;
        String evidence;

        RecoveredName(String name, String confidence, String evidence) {
            this.name = name;
            this.confidence = confidence;
            this.evidence = evidence;
        }
    }

    private static void add(
            Map<Long, RecoveredName> names,
            long address,
            String name,
            String confidence,
            String evidence) {
        names.put(address, new RecoveredName(name, confidence, evidence));
    }

    private static Map<Long, RecoveredName> recoveredNames() {
        Map<Long, RecoveredName> names = new LinkedHashMap<>();

        String vector = "nRF52840 vector slot and handler body";
        add(names, 0x000f83c4L, "SVC_Handler", "high", vector);
        add(names, 0x000f83d8L, "Reset_Handler", "high", vector);
        add(names, 0x000f83e0L, "NMI_Handler", "high", vector);
        add(names, 0x000f83e2L, "HardFault_Handler", "high", vector);
        add(names, 0x000f83e4L, "MemoryManagement_Handler", "high", vector);
        add(names, 0x000f83e6L, "BusFault_Handler", "high", vector);
        add(names, 0x000f83e8L, "UsageFault_Handler", "high", vector);
        add(names, 0x000f83ecL, "DebugMon_Handler", "high", vector);
        add(names, 0x000f83eeL, "PendSV_Handler", "high", vector);
        add(names, 0x000f83f0L, "SysTick_Handler", "high", vector);
        add(names, 0x000f83f2L, "Default_Handler", "high", vector);
        add(names, 0x000f84ecL, "CRYPTOCELL_IRQHandler", "high", vector);
        add(names, 0x000f9998L, "RTC2_IRQHandler", "high", vector);
        add(names, 0x000f9a0cL, "SWI2_EGU2_IRQHandler_vector", "high", vector);
        add(names, 0x000f9c30L, "SWI0_EGU0_IRQHandler", "high", vector);
        add(names, 0x000fc30cL, "SWI2_EGU2_IRQHandler", "high",
            "vector thunk target plus BSim 0.916");

        String atfifo = "Nordic nrf_atfifo source behavior plus BSim family match";
        add(names, 0x000f8218L, "nrf_atfifo_wspace_req", "high", atfifo);
        add(names, 0x000f8250L, "nrf_atfifo_wspace_close", "high", atfifo);
        add(names, 0x000f8262L, "nrf_atfifo_rspace_req", "high", atfifo);
        add(names, 0x000f829cL, "nrf_atfifo_rspace_close", "high", atfifo);
        add(names, 0x000f82aeL, "nrf_atfifo_space_clear", "high", atfifo);
        add(names, 0x000f82e0L, "nrf_atomic_internal_mov", "high",
            "instruction-identical __CC_ARM SDK assembly helper");
        add(names, 0x000f82f8L, "nrf_atomic_internal_orr", "high",
            "instruction-identical __CC_ARM SDK assembly helper");
        add(names, 0x000f8312L, "nrf_atomic_internal_and", "high",
            "instruction-identical __CC_ARM SDK assembly helper");
        add(names, 0x000f832cL, "nrf_atomic_internal_eor", "high",
            "instruction-identical __CC_ARM SDK assembly helper");
        add(names, 0x000f8346L, "nrf_atomic_internal_add", "high",
            "instruction-identical __CC_ARM SDK assembly helper");
        add(names, 0x000f8360L, "nrf_atomic_internal_sub", "high",
            "instruction-identical __CC_ARM SDK assembly helper");
        add(names, 0x000f837aL, "nrf_atomic_internal_cmp_exch", "high",
            "instruction-identical __CC_ARM SDK assembly helper");
        add(names, 0x000f83a4L, "nrf_atomic_internal_sub_hs", "high",
            "instruction-identical __CC_ARM SDK assembly helper");

        add(names, 0x000f83fcL, "armcc_runtime_lsl64", "medium",
            "descriptive name from recovered 64-bit left-shift semantics");
        add(names, 0x000f8208L, "armcc_runtime_entry_veneer", "high",
            "ArmCC startup veneer loading the recovered Thumb main address and branching to it");
        add(names, 0x000f841aL, "memmove", "high",
            "forward/backward overlap-aware copy semantics");
        add(names, 0x000f845cL, "armcc_memset_core", "high",
            "byte-fill semantics; __CC_ARM argument order");
        add(names, 0x000f846aL, "armcc_memclr", "high",
            "zero-fill tail wrapper over armcc_memset_core");
        add(names, 0x000f846eL, "memset", "high",
            "standard argument-order wrapper over armcc_memset_core");
        add(names, 0x000f8480L, "strlen", "high", "direct string-length semantics and BSim");
        add(names, 0x000f848eL, "memcmp", "medium",
            "bounded byte-comparison loop; return register obscured by decompiler");
        add(names, 0x000f84a8L, "strncmp", "medium",
            "bounded NUL-terminated byte-comparison loop");
        add(names, 0x000f84c8L, "armcc_scatterload", "high",
            "ArmCC scatter table walker over 16-byte records followed by the runtime-entry veneer");

        String pka = "CryptoCell/CC310 source corpus, call cluster, and BSim semantic match";
        add(names, 0x000f8510L, "CRYS_COMMON_ReverseMemcpy32", "high", pka);
        add(names, 0x000f852cL, "PkaAddAff", "high",
            "exact CC310 archive symbol order, affine-add control flow, and PkaJcb2Afn call topology");
        add(names, 0x000f8640L, "PkaAddJcbAfn2Mdf", "high",
            "exact CC310 archive symbol and PkaSum2ScalarMullt call-position correlation");
        add(names, 0x000f87d4L, "PkaClearBlockOfRegs", "high", pka);
        add(names, 0x000f8914L, "PkaCopyDataIntoPkaReg", "high", pka);
        add(names, 0x000f89d0L, "PkaDoubleMdf2Jcb", "high",
            "exact CC310 archive symbol and PkaSum2ScalarMullt call-position correlation");
        add(names, 0x000f8b48L, "PkaDoubleMdf2Mdf", "high",
            "exact CC310 archive symbol and PkaSum2ScalarMullt call-position correlation");
        add(names, 0x000f8cf4L, "PkaEcdsaVerify", "high",
            "exact CC310 archive symbol, ECDSA verification caller, and PkaSum2ScalarMullt callee");
        add(names, 0x000f8f80L, "PkaFinishAndMutexUnlock", "high", pka);
        add(names, 0x000f8fa4L, "PkaGetNextMsBit", "high", pka);
        add(names, 0x000f9018L, "PkaGetRegEffectiveSizeInBits", "high", pka);
        add(names, 0x000f90a8L, "PkaInitPka", "high", pka);
        add(names, 0x000f9124L, "PkaJcb2Afn", "medium", pka);
        add(names, 0x000f91d4L, "PkaSetRegsMapTab", "high", pka);
        add(names, 0x000f921cL, "PkaSetRegsSizesTab", "medium", pka);
        add(names, 0x000f9258L, "PkaSum2ScalarMullt", "high", pka);
        add(names, 0x000f943cL, "SaSi_HalClearInterruptBit", "high",
            "exact CC310 HAL symbol order and recovered HOST_ICR register literal");
        add(names, 0x000f9448L, "SaSi_HalMaskInterrupt", "high",
            "exact CC310 HAL symbol order and recovered HOST_IMR register literal");
        add(names, 0x000f9454L, "SaSi_HalWaitInterrupt", "medium", pka);
        add(names, 0x000f9488L, "SaSi_PalMemCopy", "high",
            "exact CC310 PAL wrapper slot and tail branch to the recovered overlap-safe copy runtime");
        add(names, 0x000f948cL, "SaSi_PalMemSet", "high",
            "exact CC310 PAL wrapper slot and tail branch to the recovered memset runtime");
        add(names, 0x000f9490L, "PkaInitAndMutexLock", "medium", pka);
        add(names, 0x000f95fcL, "nrf_cc310_bl_ecdsa_verify_init_secp256r1", "medium", pka);
        add(names, 0x000f9648L, "nrf_cc310_bl_ecdsa_verify_hash_secp256r1", "high", pka);
        add(names, 0x000f9670L, "nrf_cc310_bl_hash_sha256_finalize", "high", pka);
        add(names, 0x000f96d0L, "nrf_cc310_bl_hash_sha256_init", "medium", pka);
        add(names, 0x000f9704L, "nrf_cc310_bl_hash_sha256_update", "high", pka);
        add(names, 0x000f97a8L, "nrf_cc310_bl_hash_update_internal", "high", pka);
        add(names, 0x000f9898L, "nrf_cc310_bl_init", "medium", pka);
        add(names, 0x000f9958L, "verify_context_ecdsa_verify_secp256r1", "medium", pka);
        add(names, 0x000f9978L, "verify_context_hash_sha256", "medium", pka);

        add(names, 0x000f9a10L, "SystemInit", "high",
            "exact Nordic nRF52 system startup/errata and UICR initialization flow");
        add(names, 0x000f9c44L, "armcc_scatterload_copy", "high",
            "ArmCC scatter-copy entry branch into the recovered word-copy loop");
        add(names, 0x000f9c4cL, "armcc_scatterload_copy_loop", "high",
            "compiler-created overlapping local entry for the ArmCC scatter word-copy loop");
        add(names, 0x000f9c64L, "__sd_nvic_app_accessible_irq", "high",
            "exact S140 nrf_nvic.h application-accessible IRQ predicate");
        add(names, 0x000f9c88L, "addr_is_aligned32", "high",
            "exact Nordic fstorage 32-bit address-alignment predicate");
        add(names, 0x000f9c94L, "addr_is_within_bounds", "high",
            "exact Nordic fstorage overflow-safe start/end bounds predicate");
        add(names, 0x000f9cacL, "dfu_advertising_name_get", "high",
            "security-audit control/data-flow recovery");
        add(names, 0x000f9d44L, "advertising_start", "high",
            "exact Nordic BLE DFU advertising parameter setup, initialization, stop, and start flow");
        add(names, 0x000f9dc4L, "app_error_handler_bare", "high",
            "exact Nordic error wrapper tail call to the recovered fault handler");
        add(names, 0x000f9dc8L, "app_sched_event_put", "high",
            "exact Nordic scheduler queue insertion and critical-region behavior");
        add(names, 0x000f9e68L, "app_sched_execute", "high",
            "exact Nordic scheduler dequeue-and-dispatch loop");
        add(names, 0x000f9ea8L, "app_sched_init", "high",
            "exact Nordic scheduler queue geometry and initialization flow");
        add(names, 0x000f9d78L, "nrf_bootloader_app_activate", "high",
            "security-audit activation dispatcher call target");
        add(names, 0x000f9ed4L, "app_util_critical_region_enter", "high",
            "BSim 0.688 plus interrupt-mask semantics");
        add(names, 0x000f9f1cL, "app_util_critical_region_exit", "high",
            "BSim 0.676 plus interrupt-mask semantics");
        add(names, 0x000f9f50L, "nrf_bootloader_bl_activate", "high",
            "security-audit bootloader activation path and SDK bl_activate");
        add(names, 0x000f9f9cL, "ble_dfu_init", "high",
            "exact Nordic BLE DFU service, vendor UUID, and control-point characteristic setup");
        add(names, 0x000fa060L, "ble_dfu_req_handler_callback", "high",
            "exact Nordic BLE DFU response construction, extended-error handling, and indication path");
        add(names, 0x000fa210L, "ble_evt_handler", "high",
            "exact Nordic BLE DFU event dispatcher across connection, write, authorization, and advertising events");
        add(names, 0x000fa3e8L, "ble_srv_is_notification_enabled", "high",
            "exact BSim match and CCCD-bit semantics");
        add(names, 0x000fa4a4L, "bootloader_reset", "high",
            "exact Nordic bootloader settings-backup and system-reset helper");
        add(names, 0x000fa4e4L, "cc310_backend_mutex_trylock", "high",
            "exact Nordic SDK CryptoCell mutex wrapper and all recovered CC310_BL callers");
        add(names, 0x000fa500L, "cc310_backend_mutex_unlock", "high",
            "exact Nordic SDK CryptoCell mutex wrapper and all recovered CC310_BL callers");
        add(names, 0x000fa510L, "cc310_bl_backend_disable", "high",
            "exact Nordic SDK interrupt-enabled CryptoCell disable path and all recovered callers");
        add(names, 0x000fa534L, "cc310_bl_backend_enable", "high",
            "exact Nordic SDK interrupt-enabled CryptoCell enable path and all recovered callers");
        add(names, 0x000fa54cL, "cc310_bl_backend_hash_sha256_finalize", "high",
            "exact Nordic SDK CC310_BL source semantics and immutable SHA-256 provider table");
        add(names, 0x000fa594L, "cc310_bl_backend_hash_sha256_init", "high",
            "exact Nordic SDK CC310_BL source semantics and immutable SHA-256 provider table");
        add(names, 0x000fa5a4L, "cc310_bl_backend_hash_sha256_update", "high",
            "exact Nordic SDK CC310_BL source semantics and immutable SHA-256 provider table");
        add(names, 0x000fa608L, "cc310_bl_backend_init", "high",
            "exact Nordic SDK CC310_BL initialization semantics and immutable backend table");
        add(names, 0x000fa640L, "cc310_bl_backend_uninit", "high",
            "exact Nordic SDK CC310_BL uninitialization semantics and immutable backend table");
        add(names, 0x000fabf4L, "hash_result_get", "high",
            "exact Nordic SDK CryptoCell SHA-256 error mapping and all recovered backend callers");
        add(names, 0x000fa65cL, "crc32_compute", "high",
            "unique BSim match and 0xedb88320 reflected CRC polynomial literal");
        add(names, 0x000fa698L, "crc_ok", "high",
            "exact Nordic DFU settings stored-versus-computed CRC predicate");
        add(names, 0x000fa6b8L, "crypto_init", "high",
            "exact Nordic DFU validation one-time crypto and public-key initialization flow");
        add(names, 0x000fa776L, "nanopb_decode_field", "high",
            "BSim significance 121 and nanopb decoder call cluster");
        add(names, 0x000fa870L, "nrf_bootloader_app_is_valid", "high",
            "security-audit boot-validation recovery");
        add(names, 0x000fa908L, "nrf_bootloader_dfu_observer", "high",
            "exact static dfu_observer from nrf_bootloader.c, qualified to avoid the SDK-local duplicate");
        add(names, 0x000fa950L, "nrf_dfu_observer", "high",
            "exact static dfu_observer from nrf_dfu.c, qualified to avoid the SDK-local duplicate");
        add(names, 0x000fa3f0L, "boot_validate", "high",
            "exact Nordic static CRC-skip gate and boot-validation dispatch");
        add(names, 0x000fa400L, "boot_validation_crc", "high",
            "exact Nordic settings boot-validation CRC range and seed");
        add(names, 0x000fa64cL, "cmd_response_offset_and_crc_set", "high",
            "exact Nordic command-response offset and CRC copy helper");
        add(names, 0x000faabaL, "ext_err_code_handle", "high",
            "exact Nordic extended-error threshold, normalization, and setter dispatch");
        add(names, 0x000faac8L, "ext_error_get", "high",
            "exact Nordic read-and-clear extended-error helper");
        add(names, 0x000faad8L, "ext_error_set", "high",
            "exact Nordic extended-error store returning response code 0x0b");
        add(names, 0x000faa30L, "nrf_fstorage_nvmc_event_send", "high",
            "exact static event_send from nrf_fstorage_nvmc.c, qualified to avoid the SD-backend duplicate");
        add(names, 0x000faa66L, "event_send", "high",
            "BSim 0.922 and fstorage event-dispatch semantics");
        add(names, 0x000faafcL, "fw_hash_ok", "high",
            "exact Nordic validation wrapper tail-merging into the shared little-endian hash checker");
        add(names, 0x000fab04L, "gap_params_init", "high",
            "security-audit advertising-name data flow");
        add(names, 0x000fac3cL, "image_copy", "high",
            "exact Nordic bootloader activation page-chunk copy and progress-persistence loop");
        add(names, 0x000fad98L, "iter_from_extension", "high",
            "exact nanopb extension iterator construction and pointer-field special case");
        add(names, 0x000fae08L, "nrf_atfifo_init", "medium",
            "BSim and atomic-FIFO initialization semantics");
        add(names, 0x000faeb2L, "nrf_balloc_alloc", "high", "BSim plus balloc call cluster");
        add(names, 0x000faef6L, "nrf_balloc_free", "high", "BSim plus balloc call cluster");
        add(names, 0x000faf26L, "nrf_balloc_init", "medium", "BSim plus balloc structure setup");
        add(names, 0x000faf56L, "nrf_bootloader_app_start_final", "high",
            "BSim significance 46.9, ACL setup, MSP load, and reset-vector jump");
        add(names, 0x000fafdcL, "nrf_bootloader_dfu_inactivity_timer_restart", "high",
            "exact Nordic timer-stop and optional timer-start control flow");
        add(names, 0x000fb004L, "nrf_bootloader_acl_add", "high",
            "security-audit ACL register semantics");
        add(names, 0x000fb044L, "nrf_bootloader_fw_activate", "high",
            "security-audit bank-type activation dispatcher");
        add(names, 0x000fb0b8L, "nrf_bootloader_init", "high",
            "BSim plus Nordic bootloader initialization structure");
        add(names, 0x000fb168L, "nrf_bootloader_mbr_addrs_populate", "high",
            "BSim 0.910 and MBR address population semantics");
        add(names, 0x000fb198L, "nrf_bootloader_wdt_feed", "high",
            "exact Nordic bootloader watchdog started-check and feed call");
        add(names, 0x000fb1acL, "nrf_bootloader_wdt_feed_timer_start", "high",
            "exact Nordic repeated-timeout assignment and timer-start wrapper");
        add(names, 0x000fb1c0L, "nrf_bootloader_wdt_init", "high",
            "exact Nordic one-time watchdog initialization and timeout-reduction policy");

        String crypto = "Nordic nrf_crypto wrapper source and BSim/call-chain match";
        add(names, 0x000fb208L, "nrf_crypto_backend_secp256r1_public_key_from_raw", "high", crypto);
        add(names, 0x000fb228L, "nrf_crypto_backend_secp256r1_verify", "medium", crypto);
        add(names, 0x000fb298L, "nrf_crypto_ecc_public_key_from_raw", "high",
            "exact Nordic nrf_crypto parameter checks, backend dispatch, and init marker");
        add(names, 0x000fb2ccL, "nrf_crypto_ecdsa_verify", "high", crypto);
        add(names, 0x000fb320L, "nrf_crypto_hash_finalize", "medium", crypto);
        add(names, 0x000fb38cL, "nrf_crypto_hash_init", "high", crypto);
        add(names, 0x000fb3b8L, "nrf_crypto_hash_update", "high",
            "exact Nordic hash context/input checks and provider update dispatch");
        add(names, 0x000fb3e8L, "nrf_crypto_init", "high", crypto);
        add(names, 0x000fb428L, "nrf_crypto_internal_double_swap_endian", "high",
            "exact Nordic two-part endian-copy wrapper");
        add(names, 0x000fb442L, "nrf_crypto_internal_double_swap_endian_in_place", "medium", crypto);
        add(names, 0x000fb458L, "nrf_crypto_internal_ecc_key_input_check", "high", crypto);
        add(names, 0x000fb470L, "nrf_crypto_internal_ecc_key_output_prepare", "high", crypto);
        add(names, 0x000fb48aL, "nrf_crypto_internal_ecc_raw_input_check", "high", crypto);
        add(names, 0x000fb4a0L, "nrf_crypto_internal_swap_endian", "high",
            "exact Nordic reverse-order copy helper");
        add(names, 0x000fb4b6L, "nrf_crypto_internal_swap_endian_in_place", "medium", crypto);
        add(names, 0x000fb4d0L, "nrf_dfu_bank0_start_addr", "high",
            "exact Nordic SoftDevice-present bank-zero page alignment");
        add(names, 0x000fb4f8L, "nrf_dfu_bank1_start_addr", "high",
            "exact Nordic bank-zero plus image-size page alignment");
        add(names, 0x000fb518L, "nrf_dfu_bank_invalidate", "high",
            "exact Nordic bank-record clear and write-offset reset");
        add(names, 0x000fb52cL, "nrf_dfu_cache_prepare", "high",
            "exact Nordic three-pass app/SoftDevice cache-fit policy");
        add(names, 0x000fb5c4L, "nrf_dfu_command_req", "high",
            "exact Nordic command-object opcode dispatcher and response mutation flow");
        add(names, 0x000fb658L, "nrf_dfu_data_req", "high",
            "exact Nordic data-object opcode dispatcher and deferred-execute response policy");

        add(names, 0x000fb6dcL, "nrf_dfu_flash_init", "medium",
            "BSim plus settings-init caller semantics");
        add(names, 0x000fb710L, "nrf_dfu_init", "high",
            "exact Nordic DFU observer, transport, flash, and stored-init-command initialization flow");
        add(names, 0x000fb740L, "nrf_dfu_mbr_copy_bl", "high",
            "security-audit recovered MBR COPY_BL wrapper");
        add(names, 0x000fb758L, "nrf_dfu_mbr_init_sd", "high",
            "exact Nordic SD_MBR_COMMAND_INIT_SD stack command and SVC wrapper");
        add(names, 0x000fb770L, "nrf_dfu_mbr_irq_forward_address_set", "high",
            "exact BSim and MBR command structure");
        add(names, 0x000fb7c0L, "nrf_dfu_req_handler_on_req", "medium",
            "BSim and DFU request-dispatch behavior");
        add(names, 0x000fb7d8L, "nrf_dfu_req_handler_req_process", "high",
            "exact Nordic request/response template, object dispatcher, callback, and failure observer flow");
        add(names, 0x000fb868L, "nrf_dfu_set_adv_name_handler", "medium",
            "BSim and advertising-name settings path");
        add(names, 0x000fb8e4L, "nrf_dfu_settings_additional_erase", "high",
            "exact Nordic settings SVCI peer/advertising CRC gate and direct NVMC page rewrite");
        add(names, 0x000fb930L, "bootloader_adv_name_record_valid", "high",
            "security-audit CRC and unchecked-length recovery");
        add(names, 0x000fb950L, "nrf_dfu_settings_adv_name_write", "medium",
            "BSim plus advertising-name write behavior");
        add(names, 0x000fb994L, "nrf_dfu_settings_init", "high",
            "BSim plus flash-init/reinit/write-and-backup sequence");
        add(names, 0x000fb9b0L, "nrf_dfu_settings_progress_reset", "high",
            "exact Nordic init-command erase-fill, progress clear, and write-offset reset");
        add(names, 0x000fb918L, "nrf_dfu_settings_adv_name_copy", "high",
            "exact Nordic null-check, 28-byte advertising-name copy, and success return");
        add(names, 0x000fb988L, "nrf_dfu_settings_backup", "high",
            "exact Nordic public backup wrapper over settings_backup and primary buffer");
        add(names, 0x000fb9d8L, "nrf_dfu_settings_reinit", "high",
            "direct match to SDK primary/backup validation and merge behavior");
        add(names, 0x000fbae0L, "nrf_dfu_settings_write_and_backup", "high",
            "BSim 0.870 and settings write/backup behavior");
        add(names, 0x000fbaacL, "nrf_dfu_settings_write", "high",
            "exact Nordic settings CRC, boot-validation CRC, and primary-page write wrapper");
        add(names, 0x000fbb08L, "nrf_dfu_transports_close", "medium",
            "transport-section iteration through descriptor close callback");
        add(names, 0x000fbb3cL, "nrf_dfu_transports_init", "medium",
            "transport-section iteration through descriptor init callback");
        add(names, 0x000fbb70L, "nrf_dfu_validation_postvalidate", "medium",
            "thin wrapper calling postvalidate implementation with boot flag");
        add(names, 0x000fbb76L, "nrf_dfu_validation_boot_validate", "high",
            "security-audit boot-validation recovery");
        add(names, 0x000fbc28L, "nrf_dfu_validation_init", "high",
            "exact Nordic stored-command decode gate and valid-init-command state update");
        add(names, 0x000fbc94L, "nrf_dfu_validation_init_cmd_create", "medium",
            "BSim plus init-command state behavior");
        add(names, 0x000fbd68L, "nrf_dfu_validation_prevalidate", "high",
            "security-audit signature-before-version control flow");
        add(names, 0x000fbdb0L, "nrf_dfu_validation_signature_check", "high",
            "security-audit plus direct BSim name match");
        add(names, 0x000fbe48L, "nrf_dfu_ver_validation_check", "high",
            "security-audit plus direct BSim name match");
        add(names, 0x000fbf00L, "nrf_fstorage_init", "high", "exact BSim match");
        add(names, 0x000fbf08L, "nrf_fstorage_is_busy", "high", "BSim and busy-iteration semantics");
        add(names, 0x000fc120L, "nrf_sdh_ble_app_ram_start_get", "medium", "BSim and RAM-start access");
        add(names, 0x000fbd5cL, "nrf_dfu_validation_init_cmd_present", "high",
            "exact Nordic init-command-present state accessor and request-handler call sites");
        add(names, 0x000fc134L, "nrf_sdh_ble_default_cfg_set", "high",
            "exact Nordic two-argument default BLE configuration flow before stack enable");
        add(names, 0x000fc1d0L, "nrf_sdh_ble_enable", "high",
            "exact Nordic sd_ble_enable wrapper and successful-state update");
        add(names, 0x000fc330L, "nrf_sdh_is_enabled", "high",
            "exact Nordic SoftDevice enabled-state accessor in fstorage initialization");
        add(names, 0x000fc33cL, "nrf_sdh_request_continue", "high", "BSim and SDH state flow");
        add(names, 0x000fc3c2L, "nrf_section_iter_next", "high", "BSim and section iterator semantics");
        add(names, 0x000fc3e4L, "nrf_svc_handler_c", "high",
            "SVC vector target, SVC decode/dispatch semantics, and BSim");
        add(names, 0x000fc114L, "nrf_rtc_event_clear", "high",
            "exact Nordic RTC HAL event-register clear helper and timer callers");
        add(names, 0x000fc440L, "nrf_wdt_started", "high",
            "exact Nordic WDT run-status HAL accessor and all watchdog callers");
        add(names, 0x000fc450L, "nvmc_wait", "medium", "BSim and NVMC READY polling loop");
        add(names, 0x000fc468L, "on_ctrl_pt_write", "high",
            "exact Nordic BLE DFU control-point request decoding and request-handler dispatch");
        add(names, 0x000fc4dcL, "nrf_dfu_data_object_create", "high",
            "security-audit recovered signed-total/object bounds");
        add(names, 0x000fc550L, "on_data_obj_execute_request_sched", "medium",
            "BSim and scheduled execute callback behavior");
        add(names, 0x000fc5c8L, "nrf_dfu_data_object_write", "high",
            "security-audit recovered fragment/object bounds");
        add(names, 0x000fc654L, "app_error_fault_handler", "high",
            "exact Nordic SDK debug-break, AIRCR reset request, barriers, and fail-stop loop");
        add(names, 0x000fc684L, "on_flash_write", "high",
            "exact Nordic BLE DFU buffer-release callback and request callback-table slot");
        add(names, 0x000fc690L, "on_rw_authorize_req", "high",
            "exact Nordic BLE DFU write-authorization filtering, CCCD gate, and authorize reply");

        String nordicExact = "exact Nordic SDK 17.1.0 source/control-flow correlation and immutable body hash";
        add(names, 0x000fa178L, "ble_dfu_transport_init", "high", nordicExact);
        add(names, 0x000fa40cL, "boot_validation_extract", "high", nordicExact);
        add(names, 0x000fad38L, "is_major_softdevice_update", "high", nordicExact);
        add(names, 0x000fadc8L, "main", "high", nordicExact);
        add(names, 0x000fadf8L, "nrf_atfifo_clear", "high", nordicExact);
        add(names, 0x000fae2eL, "nrf_atfifo_item_alloc", "high", nordicExact);
        add(names, 0x000fae44L, "nrf_atfifo_item_free", "high", nordicExact);
        add(names, 0x000fae5aL, "nrf_atfifo_item_get", "high", nordicExact);
        add(names, 0x000fae70L, "nrf_atfifo_item_put", "high", nordicExact);
        add(names, 0x000fae86L, "nrf_atomic_flag_clear", "high", nordicExact);
        add(names, 0x000fb6ccL, "nrf_dfu_flash_erase", "high", nordicExact);
        add(names, 0x000fb6f8L, "nrf_dfu_flash_store", "high", nordicExact);
        add(names, 0x000fbc4cL, "nrf_dfu_validation_init_cmd_append", "high", nordicExact);
        add(names, 0x000fbcc8L, "nrf_dfu_validation_init_cmd_execute", "high", nordicExact);
        add(names, 0x000fbed4L, "nrf_fstorage_erase", "high", nordicExact);
        add(names, 0x000fbf90L, "nrf_fstorage_sys_evt_handler", "high", nordicExact);
        add(names, 0x000fc030L, "nrf_fstorage_write", "high", nordicExact);
        add(names, 0x000fc070L, "nrf_nvmc_page_erase", "high", nordicExact);
        add(names, 0x000fc0a0L, "nrf_nvmc_write_word", "high", nordicExact);
        add(names, 0x000fc0d0L, "nrf_nvmc_write_words", "high", nordicExact);
        add(names, 0x000fc1e4L, "nrf_sdh_soc_evts_poll", "high", nordicExact);
        add(names, 0x000fc244L, "nrf_sdh_disable_request", "high", nordicExact);
        add(names, 0x000fc298L, "nrf_sdh_enable_request", "high", nordicExact);
        add(names, 0x000fc394L, "nrf_section_iter_init", "high", nordicExact);
        add(names, 0x000fcff0L, "postvalidate", "high", nordicExact);
        add(names, 0x000fd0f0L, "queue_free", "high", nordicExact);
        add(names, 0x000fd104L, "queue_process", "high", nordicExact);
        add(names, 0x000fd1a0L, "queue_start", "high", nordicExact);
        add(names, 0x000fd46cL, "softdevice_evt_irq_disable", "high", nordicExact);
        add(names, 0x000fd4acL, "softdevices_evt_irq_enable", "high", nordicExact);

        String nanopb = "nanopb 0.3.x source corpus, decoder cluster, and BSim";
        add(names, 0x000fc718L, "pb_dec_bytes", "high",
            "exact nanopb no-malloc bytes decoder and immutable decoder-table slot");
        add(names, 0x000fc75aL, "pb_dec_fixed32", "high",
            "exact nanopb field-ignored wrapper and immutable decoder-table slot");
        add(names, 0x000fc760L, "pb_dec_fixed64", "high",
            "exact nanopb field-ignored wrapper and immutable decoder-table slot");
        add(names, 0x000fc766L, "pb_dec_string", "high",
            "exact nanopb no-malloc string decoder and immutable decoder-table slot");
        add(names, 0x000fc7a4L, "pb_dec_submessage", "medium", nanopb);
        add(names, 0x000fc7e4L, "pb_dec_svarint", "high", nanopb);
        add(names, 0x000fc83cL, "pb_dec_uvarint", "high", nanopb);
        add(names, 0x000fc894L, "pb_dec_varint", "high", nanopb);
        add(names, 0x000fc8ecL, "pb_decode", "high",
            "exact nanopb pb_decode.c defaults-then-noinit wrapper with malloc disabled");
        add(names, 0x000fc90aL, "pb_decode_fixed32", "medium", nanopb);
        add(names, 0x000fc934L, "pb_decode_fixed64", "medium", nanopb);
        add(names, 0x000fc990L, "pb_decode_noinit", "high", nanopb);
        add(names, 0x000fcb1aL, "pb_decode_svarint", "medium", nanopb);
        add(names, 0x000fcb96L, "pb_decode_varint", "high", nanopb);
        add(names, 0x000fcbe0L, "pb_decode_varint32", "medium", nanopb);
        add(names, 0x000fcb54L, "pb_decode_tag", "high", nanopb);
        add(names, 0x000fcc2cL, "nrf_dfu_init_command_decode_callback", "high",
            "security-audit nanopb callback and over-read loop");
        add(names, 0x000fcc68L, "pb_field_iter_begin", "high", nanopb);
        add(names, 0x000fcc8aL, "pb_field_iter_find", "high", nanopb);
        add(names, 0x000fccb8L, "pb_field_iter_next", "high", nanopb);
        add(names, 0x000fcd36L, "pb_field_set_to_default", "high", nanopb);
        add(names, 0x000fcddcL, "pb_istream_from_buffer", "medium", nanopb);
        add(names, 0x000fcdf0L, "pb_make_string_substream", "high", nanopb);
        add(names, 0x000fce26L, "pb_message_set_to_defaults", "high",
            "exact nanopb pb_decode.c iterator/defaulting control flow");
        add(names, 0x000fce4cL, "pb_read", "high", nanopb);
        add(names, 0x000fcea4L, "pb_readbyte", "high",
            "exact nanopb pb_decode.c one-byte stream read helper");
        add(names, 0x000fcec4L, "pb_skip_field", "high",
            "exact nanopb pb_decode.c wire-type dispatch and skip lengths");
        add(names, 0x000fd1e0L, "read_raw_value", "high",
            "exact nanopb callback raw-value reader for varint, fixed64, and fixed32 wire types");
        String fstorage = "exact Nordic fstorage backend semantics and immutable API-table order";
        add(names, 0x000facd4L, "nrf_fstorage_nvmc_init", "high", fstorage);
        add(names, 0x000fd6e4L, "nrf_fstorage_nvmc_uninit", "high", fstorage);
        add(names, 0x000fd1c4L, "nrf_fstorage_nvmc_read", "high", fstorage);
        add(names, 0x000fd7d4L, "nrf_fstorage_nvmc_write", "high", fstorage);
        add(names, 0x000fa99cL, "nrf_fstorage_nvmc_erase", "high", fstorage);
        add(names, 0x000fd298L, "nrf_fstorage_nvmc_rmap", "high", fstorage);
        add(names, 0x000fd7ccL, "nrf_fstorage_nvmc_wmap", "high", fstorage);
        add(names, 0x000fad18L, "nrf_fstorage_nvmc_is_busy", "high", fstorage);
        add(names, 0x000face0L, "nrf_fstorage_sd_init", "high", fstorage);
        add(names, 0x000fd6f4L, "nrf_fstorage_sd_uninit", "high", fstorage);
        add(names, 0x000fd1d2L, "nrf_fstorage_sd_read", "high", fstorage);
        add(names, 0x000fd818L, "nrf_fstorage_sd_write", "high", fstorage);
        add(names, 0x000fa9e4L, "nrf_fstorage_sd_erase", "high", fstorage);
        add(names, 0x000fd29cL, "nrf_fstorage_sd_rmap", "high", fstorage);
        add(names, 0x000fd7d0L, "nrf_fstorage_sd_wmap", "high", fstorage);
        add(names, 0x000fad28L, "nrf_fstorage_sd_is_busy", "high", fstorage);
        add(names, 0x000fae8cL, "nrf_atomic_u32_fetch_or", "high",
            "exact Nordic atomic API wrapper over recovered internal OR primitive");
        add(names, 0x000faea8L, "nrf_atomic_u32_fetch_store", "high",
            "exact Nordic atomic API wrapper over recovered internal MOV primitive");
        add(names, 0x000fa978L, "__NVIC_SystemReset", "high",
            "exact CMSIS Cortex-M4 AIRCR reset sequence from the pinned Nordic SDK");
        add(names, 0x000fa118L, "ble_dfu_transport_close", "high",
            "exact Nordic BLE DFU shutdown, disconnect delay, advertising stop, and SDH disable flow");
        add(names, 0x000fb73cL, "nrf_dfu_init_user", "high",
            "exact weak Nordic user-init default in its nrf_bootloader_init call-site slot");
        add(names, 0x000fbb00L, "nrf_dfu_softdevice_start_address", "high",
            "exact Nordic DFU utility returning the 0x1000 MBR_SIZE constant");
        add(names, 0x000fcf20L, "nrf_dfu_validation_postvalidate_impl", "high",
            "security-audit full-image hash gate and firmware dispatch");
        add(names, 0x000fd2a0L, "nrf_bootloader_sd_activate", "high",
            "security-audit SoftDevice activation target");
        add(names, 0x000fd242L, "response_crc_add", "high",
            "exact Nordic BLE DFU two-word offset/CRC response encoder");
        add(names, 0x000fd264L, "response_send", "high",
            "exact Nordic BLE DFU HVX notification parameter construction and SoftDevice call");
        add(names, 0x000fd2f4L, "sd_req_check", "high",
            "exact Nordic SoftDevice FWID and optional any-version request-table scan");
        add(names, 0x000fd338L, "sd_req_ok", "high",
            "exact Nordic init-command SoftDevice requirement and overwrite policy");
        add(names, 0x000fd3a0L, "sdh_request_observer_notify", "high", "BSim and observer iteration");
        add(names, 0x000fd3d0L, "sdh_state_observer_notify", "high", "BSim and observer iteration");
        add(names, 0x000fd3fcL, "settings_backup", "high",
            "exact Nordic static backup wrapper with backup page, source, callback, and buffer");
        add(names, 0x000fd410L, "settings_crc_get", "high",
            "exact Nordic settings CRC range excluding the stored CRC and init command");
        add(names, 0x000fd41aL, "settings_write", "high", "BSim 0.805 and flash erase/store flow");
        add(names, 0x000fd504L, "stored_init_cmd_decode", "high",
            "exact Nordic stored init-command nanopb decode and signed/unsigned command selection");
        add(names, 0x000fd5ccL, "timer_activate", "high", "BSim and RTC timer insertion flow");
        add(names, 0x000fd62cL, "timer_init", "high",
            "exact Nordic one-time LFCLK/RTC initialization sequence");
        add(names, 0x000fd6a0L, "timer_start", "high",
            "exact Nordic DFU timer initialization/callback/activation helper");
        add(names, 0x000fd6bcL, "timer_stop", "high",
            "exact Nordic RTC compare interrupt-disable helper");
        add(names, 0x000fd6d0L, "uint32_encode", "high",
            "exact Nordic little-endian four-byte integer encoder used by BLE DFU responses");
        add(names, 0x000fd78cL, "wdt_feed", "high",
            "exact Nordic seven-channel enabled-reload watchdog feed loop");
        add(names, 0x000fd76cL, "verify_context", "high",
            "exact Nordic nrf_crypto hash context null/init-marker validation");
        add(names, 0x000fd7c8L, "wdt_feed_timer_handler", "high",
            "immutable watchdog callback pointer and exact tail call to wdt_feed");
        add(names, 0x000fd8b0L, "nrfx_coredep_delay_machine_code_dfu_timers", "high",
            "exact Nordic nrfx_coredep_delay_us three-cycle machine-code array used by DFU timers");
        add(names, 0x000fdaa0L, "nrfx_coredep_delay_machine_code_ble_dfu", "high",
            "exact Nordic nrfx_coredep_delay_us three-cycle machine-code array used by BLE DFU");
        add(names, 0x000fd714L, "update_data_size_get", "medium", "BSim and bank-size calculation");
        return names;
    }

    private String subsystem(long address) {
        if (address < 0x000f83c4L) return "atomic_fifo";
        if (address < 0x000f8510L) return "startup_runtime";
        if (address < 0x000f9a10L) return "cc310_crypto";
        if (address < 0x000fb198L) return "boot_core_ble";
        if (address < 0x000fb4d0L) return "crypto_api";
        if (address < 0x000fbb76L) return "dfu_flash_settings";
        if (address < 0x000fc400L) return "dfu_validation_sdh";
        if (address < 0x000fc900L) return "dfu_object_decode";
        if (address < 0x000fcee0L) return "nanopb";
        if (address < 0x000fd400L) return "validation_transport";
        if (address < 0x000fd800L) return "settings_timer";
        return "runtime_tables";
    }

    private String role(Function function) throws Exception {
        if (function.isThunk()) return "thunk";
        Set<Function> callees = function.getCalledFunctions(monitor);
        long bytes = function.getBody().getNumAddresses();
        if (callees.isEmpty() && bytes <= 8) return "stub";
        if (callees.isEmpty()) return "leaf";
        if (callees.size() == 1 && bytes <= 40) return "wrapper";
        if (callees.size() >= 4) return "dispatcher";
        return "helper";
    }

    private String syntheticName(Function function) throws Exception {
        long address = function.getEntryPoint().getOffset();
        return String.format(
            Locale.ROOT,
            "r1_%s_%s_%08x",
            subsystem(address),
            role(function),
            address
        );
    }

    private String csv(String value) {
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }

    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 1) {
            throw new IllegalArgumentException("expected absolute function-name ledger path");
        }
        File output = new File(arguments[0]);
        if (!output.isAbsolute()) {
            throw new IllegalArgumentException("function-name ledger path must be absolute");
        }
        File parent = output.getParentFile();
        if (parent != null && !parent.exists() && !parent.mkdirs()) {
            throw new IllegalStateException("could not create output directory " + parent);
        }

        Map<Long, RecoveredName> recovered = recoveredNames();
        int actual = 0;
        int synthetic = 0;
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(output))) {
            writer.write(
                "entry,previous_name,applied_name,name_kind,confidence,evidence\n"
            );
            FunctionIterator iterator = currentProgram.getFunctionManager()
                .getFunctions(toAddr(IMAGE_BASE), true);
            while (iterator.hasNext()) {
                Function function = iterator.next();
                long address = function.getEntryPoint().getOffset();
                if (address >= IMAGE_END) break;
                String previous = function.getName();
                RecoveredName item = recovered.get(address);
                String applied;
                String kind;
                String confidence;
                String evidence;
                if (item != null) {
                    applied = item.name;
                    kind = "recovered";
                    confidence = item.confidence;
                    evidence = item.evidence;
                    actual++;
                }
                else {
                    applied = syntheticName(function);
                    kind = "synthetic_descriptive";
                    confidence = "structural";
                    evidence = "address subsystem, body size, thunk state, and direct-call count";
                    synthetic++;
                }
                function.setName(applied, SourceType.USER_DEFINED);
                writer.write(
                    String.format(Locale.ROOT, "0x%08x", address) + "," +
                    csv(previous) + "," + csv(applied) + "," + csv(kind) + "," +
                    csv(confidence) + "," + csv(evidence) + "\n"
                );
            }
        }
        println(
            "R1_NAME_LEDGER recovered=" + actual + " synthetic=" + synthetic +
            " output=" + output
        );
    }
}
