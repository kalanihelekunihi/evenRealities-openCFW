
undefined8 FUN_0041f558(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int local_18;
  undefined4 uStack_14;
  
  iVar1 = DAT_0041f9c8;
  local_18 = 0;
  uStack_14 = param_4;
  FUN_0042372a(*(undefined4 *)((uint)param_1 * 0x1c + DAT_0041f9c8 + 4),&local_18,1);
  FUN_00423700(*(undefined4 *)((uint)param_1 * 0x1c + iVar1 + 4),local_18);
  FUN_0042377c(*(undefined4 *)((uint)param_1 * 0x1c + iVar1 + 4),local_18);
  if (local_18 << 0x1b < 0) {
    FUN_0041f776(param_1,0xf,0);
  }
  if (local_18 << 0x19 < 0) {
    FUN_0041f776(param_1,0x10,1);
  }
  if (local_18 << 0x1f < 0) {
    *(undefined1 *)(iVar1 + (uint)param_1 * 0x1c + 0x19) = 1;
  }
  return CONCAT44(uStack_14,local_18);
}

