/* SPDX-License-Identifier: MIT
 * These four locked-stock entries each consist solely of Thumb bx lr.
 * They are genuine native empty callbacks, not placeholder success stubs.
 */
.syntax unified
.thumb
.text

.global opencfw_boot_empty_leaf_416028
.type opencfw_boot_empty_leaf_416028,%function
.thumb_func
opencfw_boot_empty_leaf_416028:
    bx lr
.size opencfw_boot_empty_leaf_416028, .-opencfw_boot_empty_leaf_416028

.global opencfw_boot_empty_leaf_41b5f4
.type opencfw_boot_empty_leaf_41b5f4,%function
.thumb_func
opencfw_boot_empty_leaf_41b5f4:
    bx lr
.size opencfw_boot_empty_leaf_41b5f4, .-opencfw_boot_empty_leaf_41b5f4

.global opencfw_boot_empty_leaf_424976
.type opencfw_boot_empty_leaf_424976,%function
.thumb_func
opencfw_boot_empty_leaf_424976:
    bx lr
.size opencfw_boot_empty_leaf_424976, .-opencfw_boot_empty_leaf_424976

.global opencfw_boot_empty_leaf_42e276
.type opencfw_boot_empty_leaf_42e276,%function
.thumb_func
opencfw_boot_empty_leaf_42e276:
    bx lr
.size opencfw_boot_empty_leaf_42e276, .-opencfw_boot_empty_leaf_42e276
