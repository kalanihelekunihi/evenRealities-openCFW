
uint FUN_00452df0(undefined4 param_1,int param_2,int param_3)

{
  byte bVar1;
  uint uVar2;
  
  if (*(int *)(param_3 + 0x10) == 0) {
    uVar2 = FUN_0044c47a();
  }
  else if (param_2 == 0) {
    uVar2 = (uint)*(byte *)(*(int *)(param_3 + 0x10) + 0x38);
  }
  else {
    bVar1 = FUN_004525fe();
    uVar2 = (uint)bVar1 * (uint)*(byte *)(*(int *)(param_3 + 0x10) + 0x38) >> 8;
  }
  return uVar2;
}

