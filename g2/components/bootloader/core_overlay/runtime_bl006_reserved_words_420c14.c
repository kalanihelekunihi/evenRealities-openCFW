/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: two retained single-word islands with no
 * loader in any routed span, at 0x00420C14 and 0x00422D7A.
 *
 * The 0x00420C14 head word (0x000081F6) leads the MX25 QE literal gap;
 * the admitted suffix pool at 0x00420C18 is produced by
 * runtime_bl006_mx25_pools_42086c.c. Bounded Capstone decode of every
 * routed span (in-place leaves plus patch spans) finds no
 * PC-relative or `adr` loader targeting 0x00420C14, and no reviewed
 * consumer source names the value, so it is reproduced as a named
 * reserved word preserving layout, not as claimed data; see
 * docs/research/g2-bootloader-bl006-cluster-42086c-420f70-source-closure.md.
 *
 * The 0x00422D7A datum (0x20000002) sits between the source-owned
 * per-instance secondary register-clear leaf (ends 0x00422D7A) and
 * the source-owned per-instance status mapper (starts 0x00422D7E).
 * Bounded Capstone decode of every routed span finds no loader
 * targeting it, and no reviewed consumer source names the value, so
 * it is likewise reproduced as a named reserved word preserving
 * layout; see
 * docs/research/g2-bootloader-bl006-cluster-4220b2-422ad4-source-closure.md.
 *
 * If a future consumer is found for either word, its field must be
 * re-derived with the loader PCs and reviewed meaning.
 *
 * The trailing island words at 0x0041F9CC..0x0041F9D8 (0x0043419C,
 * 0x00434158, 0x0043415C: pointers into the retained 0x004341xx
 * read-only tables, one of which heads a small "dfu" descriptor)
 * close the 0x0041F9B6 boot-initialization island whose first 22
 * bytes are produced by runtime_bl006_boot_init_pools_41f9b6.c.
 * Bounded Capstone decode of every routed span finds no loader
 * targeting any of the three words, and no reviewed consumer source
 * names them, so they are likewise reproduced as named reserved
 * words preserving layout; see
 * docs/research/g2-bootloader-bl006-cluster-41f9b6-41fdc0-source-closure.md.
 * If a future consumer is found for any of the three, its field
 * must be re-derived with the loader PCs and reviewed meaning.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Reserved head word of the MX25 QE literal gap at 0x00420C14. */
__attribute__((used, section(".rodata.bl006_word_420c14")))
const open_cfw_bl006_u32 open_cfw_bootloader_bl006_word_420c14 = 0x000081F6u;

/* Reserved datum between the register-clear and status-mapper
 * leaves at 0x00422D7A. */
__attribute__((used, section(".rodata.bl006_word_422d7a")))
const open_cfw_bl006_u32 open_cfw_bootloader_bl006_word_422d7a = 0x20000002u;

/* Trailing boot-island word at 0x0041F9CC: pointer into the retained
 * 0x0043419C read-only table (small "dfu" descriptor head). */
__attribute__((used, section(".rodata.bl006_word_41f9cc")))
const open_cfw_bl006_u32 open_cfw_bootloader_bl006_word_41f9cc = 0x0043419Cu;

/* Trailing boot-island word at 0x0041F9D0: pointer into the retained
 * 0x00434158 read-only table. */
__attribute__((used, section(".rodata.bl006_word_41f9d0")))
const open_cfw_bl006_u32 open_cfw_bootloader_bl006_word_41f9d0 = 0x00434158u;

/* Trailing boot-island word at 0x0041F9D4: pointer into the retained
 * 0x0043415C read-only table. */
__attribute__((used, section(".rodata.bl006_word_41f9d4")))
const open_cfw_bl006_u32 open_cfw_bootloader_bl006_word_41f9d4 = 0x0043415Cu;
