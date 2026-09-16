/* SPDX-License-Identifier: MIT */
/* Stock package 0x38a88 is a complete single-return hook. */
void open_cfw_gx8002_stage1_38a88(void)
{
}

extern void open_cfw_gx8002_stage1_39bb4(unsigned int, unsigned int);
/* Stock package 0x39c34 ignores incoming arguments and configures the
 * underlying helper with fixed values 115200 and zero. */
void open_cfw_gx8002_stage1_39c34(unsigned int ignored0, unsigned int ignored1)
{
    (void)ignored0;
    (void)ignored1;
    (void)open_cfw_gx8002_stage1_39bb4(115200, 0);
}
