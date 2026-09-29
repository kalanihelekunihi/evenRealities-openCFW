
undefined8 FUN_0058e534(int param_1,undefined4 param_2,uint param_3,uint param_4)

{
  bool bVar1;
  bool bVar2;
  char cVar3;
  int iVar4;
  uint uVar5;
  uint local_18;
  uint local_14;
  
  local_18 = param_3;
  local_14 = param_4;
  if (*(char *)(param_1 + 0x119) != '\0') {
    bVar2 = false;
    local_14 = FUN_00473940();
    uVar5 = *(int *)(param_1 + 0xa4) - *(int *)(param_1 + 0xd8);
    iVar4 = *(int *)(param_1 + 0xa0) + *(int *)(param_1 + 0xd8);
    if (*(char *)(param_1 + 0xdc) == '\0') {
      FUN_0058e31e(param_1,iVar4,uVar5,&local_18);
    }
    else {
      local_18 = *(int *)(param_1 + 0x40) - *(int *)(param_1 + 0x3c);
      if (uVar5 < local_18) {
        local_18 = uVar5;
      }
      cVar3 = FUN_00530084(param_1 + 0x34,iVar4,local_18);
      if ((cVar3 == '\0') && (*(undefined1 *)(param_1 + 0x119) = 0, *(int *)(param_1 + 0xb0) != 0))
      {
        (**(code **)(param_1 + 0xb0))(1,*(undefined4 *)(param_1 + 0xb4));
        bVar2 = true;
      }
    }
    if (!bVar2) {
      *(uint *)(param_1 + 0xd8) = local_18 + *(int *)(param_1 + 0xd8);
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_14 & 1) == 1);
    }
    if (bVar2) goto LAB_0058e616;
    if (*(int *)(param_1 + 0xa8) != 0) {
      **(undefined4 **)(param_1 + 0xa8) = *(undefined4 *)(param_1 + 0xd8);
    }
    if (((*(int *)(param_1 + 0xd8) == *(int *)(param_1 + 0xa4)) &&
        (*(char *)(param_1 + 0x119) != '\0')) &&
       (*(undefined1 *)(param_1 + 0x119) = 0, *(int *)(param_1 + 0xb0) != 0)) {
      (**(code **)(param_1 + 0xb0))(0,*(undefined4 *)(param_1 + 0xb4));
    }
  }
  if (*(char *)(param_1 + 0xdc) != '\0') {
    FUN_0058e3a0(param_1);
  }
LAB_0058e616:
  return CONCAT44(local_14,local_18);
}

