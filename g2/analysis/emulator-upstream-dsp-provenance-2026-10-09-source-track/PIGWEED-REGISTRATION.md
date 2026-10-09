# Pigweed registration completed

The renewed explicit delegation authorizes narrow .gitmodules/gitlink changes and supersedes the earlier source-track write restriction for this operation. Earlier proposal-only notes are historical and no longer describe the final state.

Registered official https://pigweed.googlesource.com/pigweed/pigweed at `third-party/reference/pigweed-hci`, submodule name `reference/pigweed-hci`, immutable pin `e175383a07c5b811a98924fc662d1001f1d220d0`. Entry follows existing reference layout with `update = none` and `shallow = true`. Checkout is detached and clean; the Git directory was absorbed into `.git/modules/reference/pigweed-hci` using standard git submodule tooling.

Only .gitmodules and the new mode-160000 gitlink were added to staging. Existing .gitmodules bytes were preserved verbatim before the appended five-line entry. All 16 pre-existing staged entries compare unchanged; staged count is now 18. See PIGWEED-REGISTRATION.json. No commit/push, source reconstruction, device operation or seal edit occurred.

The three HCI schemas and Apache-2.0 LICENSE in this checkout match every hash in the earlier acquisition receipt: {"pw_bluetooth/public/pw_bluetooth/hci_events.emb": true, "pw_bluetooth/public/pw_bluetooth/hci_common.emb": true, "pw_bluetooth/public/pw_bluetooth/hci_commands.emb": true, "LICENSE": true} .
