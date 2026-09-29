
void mspi_cq_init(int param_1)

{
  am_hal_cmdq_init(param_1 + 8U & 0xff,&stack0xfffffff0,DAT_00424aec + param_1 * 0x8d0 + 0x828);
  return;
}

