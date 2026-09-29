
int FUN_004c399e(int param_1,char *param_2)

{
  bool bVar1;
  bool bVar2;
  int *piVar3;
  char *pcVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  undefined4 local_24;
  int iStack_20;
  int iStack_1c;
  
  iVar8 = 0;
  if (((param_1 == 0) || (param_1 == DAT_004c44a4)) &&
     ((*DAT_004c44a8 == 0 || (*DAT_004c44a8 == DAT_004c44a4)))) {
    bVar1 = true;
  }
  else {
    bVar1 = false;
  }
  local_24 = *DAT_004c44ac;
  iStack_20 = DAT_004c44ac[1];
  iStack_1c = DAT_004c44ac[2];
  if (((param_1 != 0) && (param_1 != DAT_004c44b0)) && (param_1 != DAT_004c44a4)) {
    return 5;
  }
  if (param_1 != 0) {
    if (param_2 == (char *)0x0) {
      local_24._1_3_ = (uint3)((uint)local_24 >> 8);
      if (*(int *)(DAT_004c43e8 + 4) == 0) {
        if (*(int *)(DAT_004c43e8 + 0x10) == 0) {
          return 7;
        }
        local_24 = CONCAT31(local_24._1_3_,1);
        uVar5 = *(undefined4 *)(DAT_004c43e8 + 0x10);
      }
      else {
        local_24 = (uint)local_24._1_3_ << 8;
        uVar5 = *(undefined4 *)(DAT_004c43e8 + 4);
      }
      iVar8 = FUN_004d38ea(uVar5,param_1,local_24._1_1_,&iStack_20,param_1);
      param_2 = (char *)&local_24;
    }
    else {
      if ((*param_2 == '\0') && (*(int *)(DAT_004c43e8 + 4) == 0)) {
        return 7;
      }
      if ((*param_2 == '\x01') && (*(int *)(DAT_004c43e8 + 0x10) == 0)) {
        return 7;
      }
    }
  }
  if (iVar8 == 0) {
    bVar2 = false;
    uVar6 = FUN_00473940();
    iVar7 = FUN_004c37ca(5);
    if (iVar7 != 0) {
      if (bVar1) {
        bVar2 = true;
      }
      else {
        iVar8 = 3;
      }
    }
    if (iVar8 == 0) {
      if (param_1 != 0) {
        FUN_00439be4(DAT_004c44b4,param_2,0xc);
      }
      *DAT_004c44a8 = param_1;
      *DAT_004c44b8 = 1;
    }
    pcVar4 = DAT_004c44b4;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar6 & 1) == 1);
    }
    if (bVar2) {
      if (*DAT_004c44b4 == '\0') {
        FUN_004c3d9e(0x36);
      }
      else {
        FUN_004c3cd4(0x36);
      }
      uVar6 = FUN_00473940();
      iVar7 = FUN_004c37ca(5);
      piVar3 = DAT_004c44a8;
      if (iVar7 == 0) {
        FUN_004c3e9a(0x36);
        FUN_004c3d28(0x36);
      }
      else {
        if (*DAT_004c44a8 == 0) {
          iVar8 = FUN_004d39e4();
        }
        else {
          iVar8 = FUN_004d3992(pcVar4);
          if (iVar8 == 0) {
            if (*pcVar4 == '\0') {
              FUN_004c3d28(0x36);
            }
            else {
              FUN_004c3e9a(0x36);
            }
          }
        }
        if ((iVar8 != 0) || (*piVar3 == 0)) {
          FUN_004c3d28(0x36);
          FUN_004c3e9a(0x36);
        }
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar6 & 1) == 1);
      }
    }
  }
  return iVar8;
}

