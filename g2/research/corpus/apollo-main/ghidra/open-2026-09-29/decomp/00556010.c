
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00556010(void)

{
  undefined4 *puVar1;
  short *psVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uStack_58;
  undefined4 uStack_54;
  
  puVar1 = _DAT_00556260;
  psVar2 = (short *)teleprompt_file_list_get();
  if ((psVar2 == (short *)0x0) || (*psVar2 == 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uStack_54 = _DAT_00556b24;
      uStack_58 = 0x5d0;
      FUN_0043d574(1,PTR_s_teleprompt_ui_0055648c,PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                   _DAT_00556b28);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,_DAT_00556ca8,_DAT_00556ca8);
    }
    uVar4 = 0xffffffff;
  }
  else {
    FUN_0044d878(*puVar1);
    iVar3 = FUN_0045a568();
    if (iVar3 == 1) {
      FUN_0043c0e4(&uStack_58,0x42,0);
      FUN_00439be4((int)&uStack_58 + 2,psVar2 + puVar1[3] * 0x62 + 2,psVar2[puVar1[3] * 0x62 + 1]);
      uStack_58 = CONCAT22(uStack_58._2_2_,psVar2[puVar1[3] * 0x62 + 1]);
      APP_PbTxEncodeFileSelect(&uStack_58);
    }
    teleprompt_file_list_reset();
    uVar4 = 0;
  }
  return uVar4;
}

