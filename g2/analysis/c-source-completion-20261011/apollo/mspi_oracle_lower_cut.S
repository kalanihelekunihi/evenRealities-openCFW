.syntax unified
.thumb
.text
.macro CUT name
.global \name
.thumb_func
\name:
    bx lr
.endm
CUT opencfw_boot_mspi_cmdq_get_status
CUT opencfw_hal_mspi_cq_disable
CUT opencfw_boot_mspi_cmdq_error_resume
CUT opencfw_boot_mspi_cq_enable
CUT opencfw_boot_mspi_program_dma
CUT clock_release
