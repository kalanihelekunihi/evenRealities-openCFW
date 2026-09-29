
void at_core_register_callback(byte param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = DAT_00541580;
  if (param_1 < 3) {
    *(undefined4 *)(DAT_00541580 + (uint)param_1 * 4 + 0x18) = param_2;
    *(uint *)(iVar1 + 0x10) = 1 << (uint)param_1 | *(uint *)(iVar1 + 0x10);
  }
  return;
}

