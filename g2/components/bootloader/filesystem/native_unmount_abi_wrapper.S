/* Native 0x00414948: preserve the LittleFS internal unmount ABI.
 * r0 = filesystem; r1 receives ambient r7, r0 receives deinit result.
 * The pinned lfs.c owns the internal deinit body as a static function.
 * This wrapper is separately compilable until that lower is bound at link.
 */
.syntax unified
.thumb
.text
.align 1
.global opencfw_boot_lfs_unmount_internal_abi
.type opencfw_boot_lfs_unmount_internal_abi,%function
.thumb_func
opencfw_boot_lfs_unmount_internal_abi:
    push {r7, lr}
    bl opencfw_boot_lfs_deinit_4144dc
    pop {r1, pc}
.size opencfw_boot_lfs_unmount_internal_abi, .-opencfw_boot_lfs_unmount_internal_abi
.section .note.GNU-stack,"",%progbits
