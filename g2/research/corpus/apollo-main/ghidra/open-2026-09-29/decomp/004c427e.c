
undefined8 FUN_004c427e(undefined1 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  char *pcVar4;
  int *piVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint local_20;
  
  bVar2 = false;
  bVar3 = false;
  iVar8 = 0;
  iVar6 = FUN_004c37a8(6,param_1);
  if (iVar6 == 0) {
    uVar7 = FUN_00473940();
    iVar6 = FUN_004c37ca(6);
    if (iVar6 == 0) {
      *DAT_004c4698 = '\x01';
    }
    FUN_004c37fe(6,param_1,1);
    pcVar4 = DAT_004c4674;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar7 & 1) == 1);
    }
    if (*DAT_004c4674 != '\0') {
      if (*DAT_004c4654 == '\0') {
        iVar8 = FUN_004c3d9e(0x35);
        FUN_004c3cd4(0x35);
      }
      else {
        iVar8 = FUN_004c3cd4(0x35);
        FUN_004c3d9e(0x35);
      }
    }
    local_20 = FUN_00473940();
    if (iVar8 == 0) {
      if (*pcVar4 == '\0') {
        iVar8 = 1;
      }
      bVar3 = bVar2;
      if ((iVar8 == 0) && (*DAT_004c4698 != '\0')) {
        *DAT_004c4698 = '\0';
        piVar5 = DAT_004c469c;
        if (*DAT_004c469c == 0) {
          iVar8 = FUN_005398e0(0,DAT_004c469c);
        }
        if (iVar8 == 0) {
          iVar8 = FUN_00539a40(*piVar5,DAT_004c4654);
        }
        if (iVar8 == 0) {
          iVar8 = FUN_00539994(*piVar5);
        }
        if (iVar8 == 0) {
          bVar3 = true;
        }
        else if (*piVar5 != 0) {
          FUN_00539944(*piVar5);
          *piVar5 = 0;
        }
      }
      if (iVar8 != 0) {
        FUN_004c37fe(6,param_1,0);
      }
    }
    else {
      FUN_004c37fe(6,param_1,0);
    }
    bVar2 = (bool)isCurrentModePrivileged();
    if (bVar2) {
      enableIRQinterrupts((local_20 & 1) == 1);
    }
    if (*pcVar4 != '\0') {
      if (iVar8 == 0) {
        if (*DAT_004c4654 == '\0') {
          FUN_004c3d28(0x35);
        }
        else {
          FUN_004c3e9a(0x35);
        }
      }
      else {
        FUN_004c3e9a(0x35);
        FUN_004c3d28(0x35);
      }
    }
    if (bVar3) {
      iVar8 = FUN_00539b56(*DAT_004c469c);
    }
  }
  else {
    iVar8 = 0;
    local_20 = param_3;
  }
  return CONCAT44(local_20,iVar8);
}

