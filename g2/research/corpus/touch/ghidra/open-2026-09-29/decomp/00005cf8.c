
void FUN_00005cf8(int param_1,uint param_2,uint param_3)

{
  uint *puVar1;
  
  if (7 < param_2) {
    software_bkpt(1);
  }
  if (0xf < param_3) {
    software_bkpt(1);
  }
  puVar1 = (uint *)((((uint)(param_1 + DAT_00005d2c) >> 8) + DAT_00005d30) * 0x100);
  *puVar1 = (param_3 & 0xf) << (param_2 << 2 & 0xff) | *puVar1 & ~(0xf << (param_2 << 2 & 0xff));
  return;
}

