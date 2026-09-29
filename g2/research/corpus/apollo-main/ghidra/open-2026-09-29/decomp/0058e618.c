
undefined8 FUN_0058e618(int param_1,undefined4 param_2,uint param_3,uint param_4)

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
  if (*(char *)(param_1 + 0xdd) != '\0') {
    FUN_0058e360(param_1);
  }
  if (*(char *)(param_1 + 0x11a) != '\0') {
    bVar2 = false;
    local_14 = FUN_00473940();
    uVar5 = *(int *)(param_1 + 0x68) - *(int *)(param_1 + 0x9c);
    iVar4 = *(int *)(param_1 + 100) + *(int *)(param_1 + 0x9c);
    local_18 = 0;
    if (*(char *)(param_1 + 0xdd) == '\0') {
      FUN_0058e2d8(param_1,iVar4,uVar5,&local_18);
    }
    else {
      local_18 = *(uint *)(param_1 + 0x54);
      if (uVar5 < local_18) {
        local_18 = uVar5;
      }
      cVar3 = FUN_005300e2(param_1 + 0x4c,iVar4,local_18);
      if ((cVar3 == '\0') && (*(undefined1 *)(param_1 + 0x11a) = 0, *(int *)(param_1 + 0x74) != 0))
      {
        (**(code **)(param_1 + 0x74))(1,*(undefined4 *)(param_1 + 0x78));
        bVar2 = true;
      }
    }
    if (!bVar2) {
      *(uint *)(param_1 + 0x9c) = local_18 + *(int *)(param_1 + 0x9c);
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_14 & 1) == 1);
    }
    if (!bVar2) {
      if (*(int *)(param_1 + 0x6c) != 0) {
        **(undefined4 **)(param_1 + 0x6c) = *(undefined4 *)(param_1 + 0x9c);
      }
      if ((*(int *)(param_1 + 0x9c) == *(int *)(param_1 + 0x68)) &&
         (*(undefined1 *)(param_1 + 0x11a) = 0, *(int *)(param_1 + 0x74) != 0)) {
        (**(code **)(param_1 + 0x74))(0,*(undefined4 *)(param_1 + 0x78));
      }
    }
  }
  return CONCAT44(local_14,local_18);
}

