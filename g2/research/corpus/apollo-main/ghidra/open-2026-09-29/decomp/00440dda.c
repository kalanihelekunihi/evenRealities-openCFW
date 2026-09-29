
void FUN_00440dda(int param_1,undefined4 param_2,undefined4 param_3,char param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint local_2c;
  uint local_28;
  
  iVar1 = FUN_0043ef2a(param_1,0);
  iVar2 = FUN_0043f07e(param_1,0);
  iVar3 = FUN_0043f08c(param_1,0);
  if (iVar2 == 0) {
    iVar2 = 1;
  }
  if (iVar3 == 0) {
    iVar3 = 1;
  }
  if (((iVar1 != 0) || (iVar2 != 0x100)) || (iVar3 != 0x100)) {
    local_2c = FUN_0043ef34(param_1,0);
    local_28 = FUN_0043ef3e(param_1,0);
    if (((local_2c & 0x60000000) == 0x20000000) && ((int)(local_2c & 0x9fffffff) < 0x1fffffff)) {
      if ((int)(local_2c & 0x9fffffff) < 0x10000000) {
        uVar5 = local_2c & 0x9fffffff;
      }
      else {
        uVar5 = 0xfffffff - (local_2c & 0x9fffffff);
      }
      iVar4 = FUN_00451598(param_1 + 0x14);
      local_2c = (int)(iVar4 * uVar5) / 100;
    }
    if (((local_28 & 0x60000000) == 0x20000000) && ((int)(local_28 & 0x9fffffff) < 0x1fffffff)) {
      if ((int)(local_28 & 0x9fffffff) < 0x10000000) {
        uVar5 = local_28 & 0x9fffffff;
      }
      else {
        uVar5 = 0xfffffff - (local_28 & 0x9fffffff);
      }
      iVar4 = FUN_004515a4(param_1 + 0x14);
      local_28 = (int)(iVar4 * uVar5) / 100;
    }
    local_2c = local_2c + *(int *)(param_1 + 0x14);
    local_28 = local_28 + *(int *)(param_1 + 0x18);
    if (param_4 != '\0') {
      iVar1 = -iVar1;
      iVar2 = (iVar2 + 0xffff) / iVar2;
      iVar3 = (iVar3 + 0xffff) / iVar3;
    }
    FUN_004513c8(param_2,param_3,iVar1,iVar2,iVar3,&local_2c,param_4 == '\0');
  }
  return;
}

