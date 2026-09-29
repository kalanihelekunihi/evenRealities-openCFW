
void FUN_005c27b8(int param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int local_38;
  int local_34;
  int local_30;
  int local_2c;
  int local_28;
  int local_24;
  
  if ((param_2 != 0xffff) && (param_2 < *(uint *)(param_1 + 0x38))) {
    FUN_005c15e8(&local_38,param_2 * 0x10 + *(int *)(param_1 + 0x30));
    FUN_0043fc2a(param_1,&local_28);
    iVar1 = FUN_005c162e(param_1,0);
    iVar2 = FUN_005c1638(param_1,0);
    FUN_0044dc0a(param_1);
    iVar3 = FUN_0044fbe6();
    if (iVar1 <= iVar3 / 10) {
      iVar1 = iVar3 / 10;
    }
    if (iVar2 <= iVar3 / 10) {
      iVar2 = iVar3 / 10;
    }
    local_38 = (local_28 + local_38) - iVar1;
    local_34 = (local_24 + local_34) - iVar2;
    local_30 = iVar1 + local_28 + local_30;
    local_2c = iVar2 + local_24 + local_2c;
    if ((param_2 == *(uint *)(param_1 + 0x40)) &&
       ((int)((uint)*(ushort *)(*(int *)(param_1 + 0x34) + param_2 * 2) << 0x15) < 0)) {
      iVar1 = FUN_004515a4(&local_38);
      local_34 = local_34 - iVar1;
    }
    FUN_004405d4(param_1,&local_38);
  }
  return;
}

