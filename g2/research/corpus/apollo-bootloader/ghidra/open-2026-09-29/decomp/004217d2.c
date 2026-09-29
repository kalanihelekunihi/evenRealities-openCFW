
int FUN_004217d2(int param_1,char *param_2)

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
  if (((param_1 == 0) || (param_1 == DAT_004222d8)) &&
     ((*DAT_004222dc == 0 || (*DAT_004222dc == DAT_004222d8)))) {
    bVar1 = true;
  }
  else {
    bVar1 = false;
  }
  local_24 = *DAT_004222e0;
  iStack_20 = DAT_004222e0[1];
  iStack_1c = DAT_004222e0[2];
  if (((param_1 != 0) && (param_1 != DAT_004222e4)) && (param_1 != DAT_004222d8)) {
    return 5;
  }
  if (param_1 != 0) {
    if (param_2 == (char *)0x0) {
      local_24._1_3_ = (uint3)((uint)local_24 >> 8);
      if (*(int *)(DAT_0042221c + 4) == 0) {
        if (*(int *)(DAT_0042221c + 0x10) == 0) {
          return 7;
        }
        local_24 = CONCAT31(local_24._1_3_,1);
        uVar5 = *(undefined4 *)(DAT_0042221c + 0x10);
      }
      else {
        local_24 = (uint)local_24._1_3_ << 8;
        uVar5 = *(undefined4 *)(DAT_0042221c + 4);
      }
      iVar8 = clkmgr_hfrc2_uq15_divider_426c24(uVar5,param_1,local_24._1_1_,&iStack_20,param_1);
      param_2 = (char *)&local_24;
    }
    else {
      if ((*param_2 == '\0') && (*(int *)(DAT_0042221c + 4) == 0)) {
        return 7;
      }
      if ((*param_2 == '\x01') && (*(int *)(DAT_0042221c + 0x10) == 0)) {
        return 7;
      }
    }
  }
  if (iVar8 == 0) {
    bVar2 = false;
    uVar6 = critical_save();
    iVar7 = FUN_004215fe(5);
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
        FUN_0041568c(DAT_004222e8,param_2,0xc);
      }
      *DAT_004222dc = param_1;
      *DAT_004222ec = 1;
    }
    pcVar4 = DAT_004222e8;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar6 & 1) == 1);
    }
    if (bVar2) {
      if (*DAT_004222e8 == '\0') {
        FUN_00421bd2(0x36);
      }
      else {
        FUN_00421b08(0x36);
      }
      uVar6 = critical_save();
      iVar7 = FUN_004215fe(5);
      piVar3 = DAT_004222dc;
      if (iVar7 == 0) {
        FUN_00421cce(0x36);
        FUN_00421b5c(0x36);
      }
      else {
        if (*DAT_004222dc == 0) {
          iVar8 = clkgen_disable_426d1e();
        }
        else {
          iVar8 = clkgen_config_426ccc(pcVar4);
          if (iVar8 == 0) {
            if (*pcVar4 == '\0') {
              FUN_00421b5c(0x36);
            }
            else {
              FUN_00421cce(0x36);
            }
          }
        }
        if ((iVar8 != 0) || (*piVar3 == 0)) {
          FUN_00421b5c(0x36);
          FUN_00421cce(0x36);
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

