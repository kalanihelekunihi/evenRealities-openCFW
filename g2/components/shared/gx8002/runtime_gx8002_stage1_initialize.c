/* SPDX-License-Identifier: MIT */
/* Complete BINH stage-one dispatcher, package 0x39744..0x39774.
 * Helper names retain package addresses until their roles are established. */
extern void open_cfw_gx8002_stage1_39678(void);
extern void open_cfw_gx8002_stage1_39c44(void);
extern void open_cfw_gx8002_stage1_3912c(void);
extern void open_cfw_gx8002_stage1_38a88(void);
extern void open_cfw_gx8002_stage1_39c34(unsigned int, unsigned int);
extern int open_cfw_gx8002_backup_loader(void);
void open_cfw_gx8002_stage1_initialize(void)
{
    open_cfw_gx8002_stage1_39678();
    open_cfw_gx8002_stage1_39c44();
    open_cfw_gx8002_stage1_3912c();
    open_cfw_gx8002_stage1_38a88();
    open_cfw_gx8002_stage1_39c34(1, 0);
    if (*(volatile unsigned int *)0x20001720 == 2)
        (void)open_cfw_gx8002_backup_loader();
}
