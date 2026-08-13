// Inventory every application call into the S140 7.2 BLE SVC ranges.
// Import application.bin as raw ARM:LE:32:Cortex at 0x00027000 first.
// @category Firmware

import java.util.LinkedHashMap;
import java.util.HashSet;
import java.util.Arrays;
import java.util.Map;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;

public class R1SoftDeviceCallCensus extends GhidraScript {
    private static final int BLE_SVC_MIN = 0x60;
    private static final int BLE_SVC_MAX = 0xbf;

    // These are real Thumb SVC instructions in indirectly reached SDK helpers that a clean
    // raw-binary auto-analysis does not place in functions. Each was retained only after its
    // surrounding basic block was disassembled and distinguished from literal/string data.
    private static final Set<Long> RECOVERED_CALLS = new HashSet<>(Arrays.asList(
        0x4c90cL, 0x4cc6cL,
        0x4d4deL, 0x4d4f6L, 0x4d50cL, 0x4d524L, 0x4d53cL, 0x4d55cL, 0x4d56aL, 0x4d574L,
        0x4df68L, 0x4f166L, 0x52312L, 0x529daL, 0x529f2L, 0x52f96L, 0x57916L,
        0x7a3a8L, 0x7c552L, 0x7cd1eL, 0x7cd3aL, 0x7cdf0L, 0x7ce14L
    ));

    // Exact-image non-code matches. Keeping this list explicit prevents a contaminated Ghidra
    // project with an accidentally created data function from turning a coincidence into an API.
    private static final Set<Long> DATA_COINCIDENCES = new HashSet<>(Arrays.asList(
        0x4ccc8L, 0x4dd38L, 0x995fcL, 0x9c068L, 0x9c0aaL, 0x9d6c6L, 0x9eb18L,
        0x9f000L, 0x9f992L, 0xa0070L, 0xa03bcL, 0xa2a04L, 0xa4ff4L, 0xa5f32L,
        0xa60a8L, 0xa7176L, 0xa7284L, 0xa7400L, 0xa828cL, 0xaab9cL, 0xab1e6L,
        0xac014L, 0xac334L, 0xac9f4L, 0xae858L, 0xaee38L, 0xb07f6L, 0xb0cb8L,
        0xb16fcL, 0xb17bcL, 0xb2fb6L, 0xb84f6L, 0xb85f4L, 0xbd46cL, 0xbd630L
    ));

    @Override
    protected void run() throws Exception {
        Map<Integer, String> names = svcNames();
        Map<Integer, Integer> instructionCounts = new LinkedHashMap<>();
        Map<Integer, Integer> dataCoincidenceCounts = new LinkedHashMap<>();
        Map<Integer, Integer> unclassifiedCounts = new LinkedHashMap<>();
        for (int svc = BLE_SVC_MIN; svc <= BLE_SVC_MAX; svc++) {
            instructionCounts.put(svc, 0);
            dataCoincidenceCounts.put(svc, 0);
            unclassifiedCounts.put(svc, 0);
        }

        FunctionManager functions = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();
        Address address = currentProgram.getMemory().getMinAddress();
        Address max = currentProgram.getMemory().getMaxAddress();

        println("kind\tsvc\tname\taddress\tfunction");
        while (address.compareTo(max) < 0) {
            int first = currentProgram.getMemory().getByte(address) & 0xff;
            int second = currentProgram.getMemory().getByte(address.add(1)) & 0xff;
            if (first >= BLE_SVC_MIN && first <= BLE_SVC_MAX && second == 0xdf) {
                Instruction instruction = listing.getInstructionAt(address);
                Function function = functions.getFunctionContaining(address);
                boolean knownData = DATA_COINCIDENCES.contains(address.getOffset());
                boolean discovered = !knownData && instruction != null
                    && "svc".equalsIgnoreCase(instruction.getMnemonicString())
                    && function != null;
                boolean recovered = RECOVERED_CALLS.contains(address.getOffset());
                boolean real = discovered || recovered;
                String kind = discovered ? "CALL" : recovered ? "CALL_RECOVERED"
                    : knownData ? "DATA" : "UNCLASSIFIED";
                Map<Integer, Integer> counts = real ? instructionCounts
                    : knownData ? dataCoincidenceCounts : unclassifiedCounts;
                counts.put(first, counts.get(first) + 1);
                println(kind + "\t" + hex(first) + "\t" + name(names, first) + "\t"
                    + address + "\t" + describe(function));
            }
            address = address.add(2);
        }

        println("\nsummary\tsvc\tname\tcalls\tdata_coincidences\tunclassified");
        for (Map.Entry<Integer, String> entry : names.entrySet()) {
            int svc = entry.getKey();
            println("API\t" + hex(svc) + "\t" + entry.getValue() + "\t"
                + instructionCounts.get(svc) + "\t" + dataCoincidenceCounts.get(svc) + "\t"
                + unclassifiedCounts.get(svc));
        }

        println("\nunknown_svc\tsvc\tcalls\tdata_coincidences");
        for (int svc = BLE_SVC_MIN; svc <= BLE_SVC_MAX; svc++) {
            if (!names.containsKey(svc)
                    && (instructionCounts.get(svc) != 0 || dataCoincidenceCounts.get(svc) != 0
                        || unclassifiedCounts.get(svc) != 0)) {
                println("UNKNOWN\t" + hex(svc) + "\t" + instructionCounts.get(svc)
                    + "\t" + dataCoincidenceCounts.get(svc) + "\t"
                    + unclassifiedCounts.get(svc));
            }
        }
    }

    private static Map<Integer, String> svcNames() {
        Map<Integer, String> names = new LinkedHashMap<>();

        put(names, 0x60,
            "sd_ble_enable", "sd_ble_evt_get", "sd_ble_uuid_vs_add", "sd_ble_uuid_decode",
            "sd_ble_uuid_encode", "sd_ble_version_get", "sd_ble_user_mem_reply",
            "sd_ble_opt_set", "sd_ble_opt_get", "sd_ble_cfg_set", "sd_ble_uuid_vs_remove");

        put(names, 0x6c,
            "sd_ble_gap_addr_set", "sd_ble_gap_addr_get", "sd_ble_gap_whitelist_set",
            "sd_ble_gap_device_identities_set", "sd_ble_gap_privacy_set",
            "sd_ble_gap_privacy_get", "sd_ble_gap_adv_set_configure", "sd_ble_gap_adv_start",
            "sd_ble_gap_adv_stop", "sd_ble_gap_conn_param_update", "sd_ble_gap_disconnect",
            "sd_ble_gap_tx_power_set", "sd_ble_gap_appearance_set", "sd_ble_gap_appearance_get",
            "sd_ble_gap_ppcp_set", "sd_ble_gap_ppcp_get", "sd_ble_gap_device_name_set",
            "sd_ble_gap_device_name_get", "sd_ble_gap_authenticate", "sd_ble_gap_sec_params_reply",
            "sd_ble_gap_auth_key_reply", "sd_ble_gap_lesc_dhkey_reply",
            "sd_ble_gap_keypress_notify", "sd_ble_gap_lesc_oob_data_get",
            "sd_ble_gap_lesc_oob_data_set", "sd_ble_gap_encrypt", "sd_ble_gap_sec_info_reply",
            "sd_ble_gap_conn_sec_get", "sd_ble_gap_rssi_start", "sd_ble_gap_rssi_stop",
            "sd_ble_gap_scan_start", "sd_ble_gap_scan_stop", "sd_ble_gap_connect",
            "sd_ble_gap_connect_cancel", "sd_ble_gap_rssi_get", "sd_ble_gap_phy_update",
            "sd_ble_gap_data_length_update", "sd_ble_gap_qos_channel_survey_start",
            "sd_ble_gap_qos_channel_survey_stop", "sd_ble_gap_adv_addr_get",
            "sd_ble_gap_next_conn_evt_counter_get", "sd_ble_gap_conn_evt_trigger_start",
            "sd_ble_gap_conn_evt_trigger_stop");

        put(names, 0x9b,
            "sd_ble_gattc_primary_services_discover", "sd_ble_gattc_relationships_discover",
            "sd_ble_gattc_characteristics_discover", "sd_ble_gattc_descriptors_discover",
            "sd_ble_gattc_attr_info_discover", "sd_ble_gattc_char_value_by_uuid_read",
            "sd_ble_gattc_read", "sd_ble_gattc_char_values_read", "sd_ble_gattc_write",
            "sd_ble_gattc_hv_confirm", "sd_ble_gattc_exchange_mtu_request");

        put(names, 0xa8,
            "sd_ble_gatts_service_add", "sd_ble_gatts_include_add",
            "sd_ble_gatts_characteristic_add", "sd_ble_gatts_descriptor_add",
            "sd_ble_gatts_value_set", "sd_ble_gatts_value_get", "sd_ble_gatts_hvx",
            "sd_ble_gatts_service_changed", "sd_ble_gatts_rw_authorize_reply",
            "sd_ble_gatts_sys_attr_set", "sd_ble_gatts_sys_attr_get",
            "sd_ble_gatts_initial_user_handle_get", "sd_ble_gatts_attr_get",
            "sd_ble_gatts_exchange_mtu_reply");

        put(names, 0xb8,
            "sd_ble_l2cap_ch_setup", "sd_ble_l2cap_ch_release", "sd_ble_l2cap_ch_rx",
            "sd_ble_l2cap_ch_tx", "sd_ble_l2cap_ch_flow_control");
        return names;
    }

    private static void put(Map<Integer, String> names, int first, String... values) {
        for (int index = 0; index < values.length; index++) {
            names.put(first + index, values[index]);
        }
    }

    private static String name(Map<Integer, String> names, int svc) {
        String value = names.get(svc);
        return value == null ? "unallocated_or_undefined" : value;
    }

    private static String hex(int value) {
        return String.format("0x%02x", value);
    }

    private static String describe(Function function) {
        return function == null ? "<none>" : function.getName() + "@" + function.getEntryPoint();
    }
}
