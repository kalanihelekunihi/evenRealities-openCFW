
undefined8 FUN_00584bc0(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 in_r3;
  undefined4 local_10;
  
  piVar1 = DAT_00584e54;
  local_10 = in_r3;
  if (*DAT_00584e54 == 0) {
    iVar2 = osSemaphoreNew(1,0,0);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      uVar3 = 1;
      goto LAB_00584c8a;
    }
  }
  piVar1 = DAT_00584e74;
  if (*DAT_00584e74 == 0) {
    iVar2 = osMutexNew(0);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      uVar3 = 1;
      goto LAB_00584c8a;
    }
  }
  piVar1 = DAT_00584e48;
  iVar2 = FUN_0058dae4(0,DAT_00584e48);
  if ((iVar2 == 0) && (*piVar1 != 0)) {
    iVar2 = FUN_00480f0c(0,*DAT_00584e78);
    iVar4 = FUN_00480f0c(2,*DAT_00584e7c);
    iVar5 = FUN_0058dbb8(*piVar1,0,0);
    iVar6 = FUN_0058e09e(*piVar1,DAT_00584e80);
    local_10 = 0;
    iVar7 = FUN_0058ddd6(*piVar1,0,0,0);
    FUN_005849f2(0xf);
    FUN_00584a10(0xf,3);
    FUN_005849d4(0xf);
    iVar8 = FUN_0058e782(*piVar1,0x1fd0);
    *DAT_00584e4c = 1;
    FUN_00584df4();
    if (((((iVar2 == 0 && iVar4 == 0) && iVar5 == 0) && iVar6 == 0) && iVar7 == 0) && iVar8 == 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
    }
  }
  else {
    uVar3 = 1;
  }
LAB_00584c8a:
  return CONCAT44(local_10,uVar3);
}

