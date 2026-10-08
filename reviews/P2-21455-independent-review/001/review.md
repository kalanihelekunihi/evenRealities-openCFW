# Independent review — P2-21455

Status: partial; accepted: false.

Fresh replay passed for the 102-byte range. Regenerated instruction and reference files match the candidate exactly, including tiling and PC-relative references.

The type-7 branch uses the child resource pointer and a record pointer loaded from context+28. If the record is present, the resource+8 halfword is zero-extended, multiplied by the 4515A4 helper result with 32-bit wrap, and compared against global+324. The count is freshly reloaded for the subtraction or reset-to-zero path. The underflow/large-count diagnostic writes its pointer to SP0, aliasing saved entry R2, and calls line 560. Both count outcomes then freshly reload the resource pointer, call 48B216, and clear record word zero. The outer pointer is independently null-checked and its +684 field loaded.

The resource helper contracts and continuation are unresolved. Review remains partial/unaccepted.
