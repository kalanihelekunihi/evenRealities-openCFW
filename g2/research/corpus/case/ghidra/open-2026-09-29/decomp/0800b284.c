
uint FUN_0800b284(undefined4 *param_1)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = FUN_0800ca6c();
  iVar1 = DAT_0800b2ac;
  if (uVar2 < *(uint *)(DAT_0800b2ac + 8)) {
    FUN_0800b2b0();
    *param_1 = 1;
  }
  else {
    *param_1 = 0;
  }
  *(uint *)(iVar1 + 8) = uVar2;
  return uVar2;
}

