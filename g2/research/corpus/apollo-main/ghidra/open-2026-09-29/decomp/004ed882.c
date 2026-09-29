
void FUN_004ed882(int param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int local_78;
  undefined4 local_74;
  undefined4 local_68;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 uStack_18;
  
  piVar2 = DAT_004eda88;
  if ((*DAT_004eda88 != 0) && (0x100 < *DAT_004eda80)) {
    iVar3 = ((*DAT_004eda80 + -0xe5) / 0x1c) * -0x1c;
    if (param_1 < 1) {
      if (100 < param_2) {
        param_3 = param_3 << 1;
      }
      iVar4 = ((((param_3 + 0x1b) / 0x1c) * 0x1c + *DAT_004eda8c) / 0x1c) * 0x1c;
      if (0 < iVar4) {
        iVar4 = 0;
      }
    }
    else {
      if (100 < param_2) {
        param_3 = param_3 << 1;
      }
      iVar4 = ((*DAT_004eda8c + ((param_3 + 0x1b) / 0x1c) * -0x1c) / 0x1c) * 0x1c;
      if (iVar4 < iVar3) {
        iVar4 = iVar3;
      }
    }
    if (iVar4 != *DAT_004eda8c) {
      *DAT_004eda8c = iVar4;
      uStack_18 = param_4;
      FUN_004503d6(&local_78);
      puVar1 = DAT_004eda84;
      local_78 = *piVar2;
      local_74 = DAT_004eda90;
      FUN_004506ce(&local_78,*DAT_004eda84,iVar4);
      local_48 = 200;
      local_58 = DAT_004eda94;
      local_68 = DAT_004eda98;
      *DAT_004eda78 = 1;
      FUN_00450408(&local_78);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004edaa8,DAT_004edaa4,DAT_004edaa0,0xe7,DAT_004eda9c,*puVar1,iVar4,
                     param_2,param_3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x11000000,DAT_004edaac,DAT_004edaac,*puVar1,iVar4,param_2,param_3);
      }
    }
  }
  return;
}

