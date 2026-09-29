
int FUN_004216d4(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  uint local_28;
  uint local_24;
  uint uStack_20;
  uint uStack_1c;
  undefined4 uStack_18;
  
  iVar3 = 0;
  local_24 = *DAT_00422214;
  uStack_20 = DAT_00422214[1];
  uStack_1c = DAT_00422214[2];
  if ((param_1 == 0) || (param_1 == DAT_00422218)) {
    uStack_18 = param_4;
    if (param_1 != 0) {
      if (*(int *)(DAT_0042221c + 0xc) == 0) {
        return 7;
      }
      if (param_2 == (uint *)0x0) {
        iVar3 = clkmgr_hfrc_integer_divider_426c4e
                          (*(undefined4 *)(DAT_0042221c + 0xc),param_1,&local_28);
        local_24 = local_24 & 0xfff000ff | (local_28 & 0xfff) << 8;
        param_2 = &local_24;
      }
    }
    if (iVar3 == 0) {
      local_28 = critical_save();
      iVar2 = FUN_004215fe(4);
      if (iVar2 == 0) {
        if (param_1 != *DAT_00422290) {
          clkgen_hfadj_disable_426c7e();
          *DAT_00422298 = 0;
          *DAT_0042229c = 0;
        }
      }
      else {
        iVar3 = 3;
        if (((param_1 == 0) || (param_1 == DAT_00422218)) &&
           ((*DAT_00422290 == 0 || (*DAT_00422290 == DAT_00422218)))) {
          if (param_1 == 0) {
            iVar3 = clkgen_hfadj_disable_426c7e();
          }
          else {
            iVar3 = clkgen_hfadj_config_426c72(*param_2);
            if (iVar3 != 0) {
              clkgen_hfadj_config_426c72(*DAT_00422294);
            }
          }
        }
      }
      if (iVar3 == 0) {
        if (param_1 != 0) {
          FUN_0041568c(DAT_00422294,param_2,0xc);
        }
        *DAT_00422290 = param_1;
        *DAT_004222d4 = 1;
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_28 & 1) == 1);
      }
    }
  }
  else {
    iVar3 = 5;
  }
  return iVar3;
}

