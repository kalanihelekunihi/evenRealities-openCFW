# R1 C console receive and tokenization

The normal open-toolchain build compiles 805 units (723 application, 82 bootloader). The application has 69 explicit imports: `r1_eat_command_tokenize` is supplied and `r1_eat_command_dispatch` becomes the remaining dependency. Strict bootloader linking and R1 source checking pass. Global source checking still reports the unrelated G2 unlisted resident-ROM assembly source.

`native_console.c` supplies the stock manager RTT poll and tokenizer. Polling reads at most 127 bytes and removes the last received byte whenever the read is nonempty, regardless of its value. The tokenizer clears two 128-byte fields, skips repeated equals delimiters using the existing C strtok, copies at most 127 bytes per field and always dispatches. It preserves the third token fetch after filling the second field, including its cursor and input mutations. The fixed `%s` formatting call is specialized to bounded byte copying. The shared tokenizer cursor and console buffer now have relocatable source owners.

REA byte windows at 0x4f260 (92 bytes) and 0x88424 (44 bytes) match the locked application. Independent input/cursor oracles and raw-stock execution pass 372 tokenizer pairs and 216 integrated RTT-to-tokenizer pairs. Actual RTT reader, initializer, strtok and copy code execute; raw stock snprintf executes in the reference. Command dispatch alone is modeled. Cases cover continuation, repeated delimiters, truncation, embedded NUL, high bytes, ring wrapping and interrupt masks. Four compiled defects are rejected: wrong delimiter, missing third fetch, early truncation and retaining the final received byte.

The audit preserves 801 prior object hashes. In the libc unit only cursor address materialization and its four-byte source-owned cell change; all other libc code and relocations are unchanged. Generated boot objects retain allocated bytes and normalized relocations. The manifest only adds the new console unit.

The proof covers ordinary C calls with mutable NUL-terminated input and valid shared strtok continuation. Private frames and incidental void return registers are excluded. The cursor remains nonreentrant. Command dispatch, manager initialization, final startup memory placement, physical debugger/interrupt concurrency and device boot remain open. Compilation and relocatable composition do not establish a complete firmware image.

Machine-readable hashes, execution results and probe paths are in [console-c-review.json](console-c-review.json).
