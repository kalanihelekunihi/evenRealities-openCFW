#!/usr/bin/env python3
"""Exercise the maintained, production-routable ANCC protocol core."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_ancc_profile_core.c"


class RuntimeAnccProfileCoreTests(unittest.TestCase):
    def test_protocol_state_machine_and_bounds(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <string.h>
            #include "runtime_ancc_profile_core.h"

            struct capture {
                unsigned writes;
                unsigned attributes;
                unsigned completes;
                unsigned removals;
                uint8_t connection_id;
                uint16_t handle;
                uint16_t length;
                uint8_t value[128];
                uint8_t attribute_ids[8];
                uint16_t attribute_lengths[8];
                uint8_t attribute_values[8][16];
                uint32_t complete_uid;
                uint32_t removed_uid;
                int write_result;
            };

            static int capture_write(
                void *context, uint8_t connection_id, uint16_t handle,
                const uint8_t *value, uint16_t length
            ) {
                struct capture *capture = context;
                assert(length <= sizeof(capture->value));
                capture->writes++;
                capture->connection_id = connection_id;
                capture->handle = handle;
                capture->length = length;
                memcpy(capture->value, value, length);
                return capture->write_result;
            }

            static void capture_attribute(
                void *context, const struct open_cfw_ancc_state *state
            ) {
                struct capture *capture = context;
                const struct open_cfw_ancc_active *active = &state->active;
                unsigned index = capture->attributes++;
                assert(index < 8U);
                assert(active->attribute_length <= 16U);
                capture->attribute_ids[index] = active->attribute_id;
                capture->attribute_lengths[index] = active->attribute_length;
                memcpy(
                    capture->attribute_values[index],
                    state->data + active->parse_index,
                    active->attribute_length
                );
            }

            static void capture_complete(
                void *context, const struct open_cfw_ancc_state *state,
                uint32_t uid
            ) {
                struct capture *capture = context;
                assert(state->active.attribute_count == (
                    state->active.command_id == 1U ? 1U : 8U
                ));
                capture->completes++;
                capture->complete_uid = uid;
            }

            static void capture_remove(
                void *context,
                const struct open_cfw_ancc_notification *notification
            ) {
                struct capture *capture = context;
                capture->removals++;
                capture->removed_uid = notification->uid;
            }

            static const struct open_cfw_ancc_hooks hooks_template = {
                0, capture_write, capture_attribute,
                capture_complete, capture_remove
            };

            static void initialize(
                struct open_cfw_ancc_state *state,
                struct open_cfw_ancc_hooks *hooks,
                struct capture *capture,
                uint16_t handles[5]
            ) {
                memset(capture, 0, sizeof(*capture));
                capture->write_result = 1;
                *hooks = hooks_template;
                hooks->context = capture;
                open_cfw_ancc_state_initialize(state, 9U);
                assert(state->handler_id == 9U);
                assert(open_cfw_ancc_no_connection_active(state));
                open_cfw_ancc_connection_open(state, 7U, handles);
                assert(!open_cfw_ancc_no_connection_active(state));
            }

            static uint16_t make_response(
                uint8_t *response, uint8_t command, const char *app_id
            ) {
                uint16_t length = 0U;
                response[length++] = command;
                if (command == 0U) {
                    response[length++] = 0x78U;
                    response[length++] = 0x56U;
                    response[length++] = 0x34U;
                    response[length++] = 0x12U;
                } else {
                    while (*app_id != '\0') {
                        response[length++] = (uint8_t)*app_id++;
                    }
                    response[length++] = 0U;
                }
                for (uint8_t id = 0U; id < (command == 1U ? 1U : 8U); ++id) {
                    response[length++] = id;
                    response[length++] = 2U;
                    response[length++] = 0U;
                    response[length++] = (uint8_t)(0xA0U + id);
                    response[length++] = (uint8_t)(0xB0U + id);
                }
                return length;
            }

            static void check_response_capture(
                const struct open_cfw_ancc_state *state,
                const struct capture *capture, uint32_t uid,
                unsigned expected_attributes
            ) {
                assert(capture->attributes == expected_attributes);
                assert(capture->completes == 1U);
                assert(capture->complete_uid == uid);
                for (uint8_t id = 0U; id < expected_attributes; ++id) {
                    assert(capture->attribute_ids[id] == id);
                    assert(capture->attribute_lengths[id] == 2U);
                    assert(capture->attribute_values[id][0] == 0xA0U + id);
                    assert(capture->attribute_values[id][1] == 0xB0U + id);
                }
                assert(state->active.parse_state == OPEN_CFW_ANCC_PARSE_COMMAND);
                assert(state->active.buffer_length == 0U);
                assert(state->active.parse_index == 0U);
            }

            int main(void) {
                struct open_cfw_ancc_state state;
                struct open_cfw_ancc_hooks hooks;
                struct open_cfw_ancc_notification notification = {0};
                struct capture capture;
                uint16_t handles[5] = {0x101U, 0x102U, 0x103U, 0x104U, 0x105U};
                uint8_t response[128];
                uint16_t response_length;

                assert(open_cfw_ancc_no_connection_active(0));
                initialize(&state, &hooks, &capture, handles);

                assert(open_cfw_ancc_request_notification_attributes(
                    &state, &hooks, 0x12345678U));
                { const uint8_t expected[19] = {
                    0U,0x78U,0x56U,0x34U,0x12U,
                    0U,1U,0U,1U,2U,0U,1U,3U,0U,1U,4U,5U,6U,7U
                };
                  assert(capture.writes == 1U && capture.connection_id == 7U);
                  assert(capture.handle == 0x103U && capture.length == 19U);
                  assert(memcmp(capture.value, expected, sizeof(expected)) == 0); }

                assert(open_cfw_ancc_perform_action(
                    &state, &hooks, 0xA1B2C3D4U, 1U));
                { const uint8_t expected[6] = {2U,0xD4U,0xC3U,0xB2U,0xA1U,1U};
                  assert(capture.length == 6U);
                  assert(memcmp(capture.value, expected, sizeof(expected)) == 0); }

                assert(open_cfw_ancc_request_app_attributes(
                    &state, &hooks, (const uint8_t *)"com.example.app"));
                assert(capture.value[0] == 1U);
                assert(strcmp((const char *)(capture.value + 1), "com.example.app") == 0);
                assert(capture.value[capture.length - 1U] == 0U);
                { uint8_t maximum[62]; memset(maximum, 'x', 61U); maximum[61] = 0U;
                  assert(open_cfw_ancc_request_app_attributes(&state, &hooks, maximum));
                  assert(capture.length == 64U); }
                { uint8_t too_long[63]; memset(too_long, 'x', sizeof(too_long));
                  assert(!open_cfw_ancc_request_app_attributes(&state, &hooks, too_long)); }
                assert(!open_cfw_ancc_request_app_attributes(&state, &hooks, 0));
                capture.write_result = 0;
                assert(!open_cfw_ancc_perform_action(&state, &hooks, 1U, 0U));
                capture.write_result = 1;
                handles[2] = 0U;
                assert(!open_cfw_ancc_perform_action(&state, &hooks, 1U, 0U));
                handles[2] = 0x103U;

                for (uint32_t index = 0U; index < 64U; ++index) {
                    notification.uid = index + 1U;
                    notification.event_id = (uint8_t)(index & 1U);
                    assert(open_cfw_ancc_notification_push(&state, &notification));
                }
                notification.uid = 65U;
                assert(!open_cfw_ancc_notification_push(&state, &notification));
                notification.uid = 23U;
                notification.category_id = 9U;
                assert(open_cfw_ancc_notification_push(&state, &notification));
                assert(state.list[22].category_id == 9U);
                assert(open_cfw_ancc_notification_pop(&state));
                assert(state.active.handle == 63U && state.list[63].valid == 0U);
                for (unsigned index = 0U; index < 63U; ++index)
                    assert(open_cfw_ancc_notification_pop(&state));
                assert(!open_cfw_ancc_notification_pop(&state));

                { const uint8_t removed[8] = {2U,3U,4U,5U,0x44U,0x33U,0x22U,0x11U};
                  assert(open_cfw_ancc_feed_value(
                      &state, &hooks, handles[0], removed, sizeof(removed)));
                  assert(capture.removals == 1U && capture.removed_uid == 0x11223344U);
                  assert(!open_cfw_ancc_feed_value(
                      &state, &hooks, handles[0], removed, 7U));
                  assert(!open_cfw_ancc_feed_value(
                      &state, &hooks, handles[0], removed, 9U));
                  assert(!open_cfw_ancc_feed_value(
                      &state, &hooks, 0x999U, removed, sizeof(removed))); }

                response_length = make_response(response, 0U, "");
                for (uint16_t split = 1U; split < response_length; ++split) {
                    open_cfw_ancc_parser_reset(&state);
                    capture.attributes = capture.completes = 0U;
                    assert(open_cfw_ancc_feed_value(
                        &state, &hooks, handles[3], response, split));
                    assert(!open_cfw_ancc_feed_value(
                        &state, &hooks, handles[3], response + split,
                        (uint16_t)(response_length - split)));
                    check_response_capture(&state, &capture, 0x12345678U, 8U);
                }
                open_cfw_ancc_parser_reset(&state);
                capture.attributes = capture.completes = 0U;
                for (uint16_t index = 0U; index < response_length; ++index) {
                    int result = open_cfw_ancc_feed_value(
                        &state, &hooks, handles[3], response + index, 1U);
                    assert(result == (index + 1U < response_length));
                }
                check_response_capture(&state, &capture, 0x12345678U, 8U);

                response_length = make_response(response, 1U, "com.split.app");
                for (uint16_t split = 1U; split < 15U; ++split) {
                    open_cfw_ancc_parser_reset(&state);
                    capture.attributes = capture.completes = 0U;
                    assert(open_cfw_ancc_feed_value(
                        &state, &hooks, handles[3], response, split));
                    assert(!open_cfw_ancc_feed_value(
                        &state, &hooks, handles[3], response + split,
                        (uint16_t)(response_length - split)));
                    assert(strcmp((const char *)state.app_id, "") == 0);
                    check_response_capture(&state, &capture, 0U, 1U);
                }

                { uint8_t prefix[8] = {0U,1U,2U,3U,4U,0U,0xFFU,1U};
                  uint8_t excess[505] = {0};
                  assert(open_cfw_ancc_feed_value(
                      &state, &hooks, handles[3], prefix, sizeof(prefix)));
                  assert(!open_cfw_ancc_feed_value(
                      &state, &hooks, handles[3], excess, sizeof(excess)));
                  assert(state.active.buffer_length == 0U);
                  assert(state.active.parse_state == OPEN_CFW_ANCC_PARSE_COMMAND); }

                open_cfw_ancc_connection_close(&state);
                assert(open_cfw_ancc_no_connection_active(&state));
                assert(state.handles == 0);
                assert(!open_cfw_ancc_feed_value(
                    &state, &hooks, 0x101U, response, 1U));
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            harness_path = temporary / "harness.c"
            executable = temporary / "ancc-test"
            harness_path.write_text(harness)
            subprocess.run(
                ["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                 "-I", str(SOURCE_DIR), str(SOURCE), str(harness_path),
                 "-o", str(executable)], check=True
            )
            subprocess.run([str(executable)], check=True)

    def test_freestanding_thumb_build_has_no_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            object_path = Path(directory) / "runtime_ancc_profile_core.o"
            subprocess.run(
                ["clang", "--target=thumbv7em-none-eabi", "-mthumb",
                 "-mcpu=cortex-m55", "-std=c11", "-O2", "-ffreestanding",
                 "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                 "-Wall", "-Wextra", "-Werror", "-I", str(SOURCE_DIR),
                 "-c", str(SOURCE), "-o", str(object_path)], check=True
            )
            undefined = subprocess.run(
                ["nm", "-u", str(object_path)], check=True,
                capture_output=True, text=True
            ).stdout.strip()
            self.assertEqual(undefined, "")


if __name__ == "__main__":
    unittest.main()
