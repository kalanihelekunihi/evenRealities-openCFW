
undefined4 setting_respond_to_app(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  byte *pbVar1;
  undefined4 uVar2;
  int iVar3;
  uint local_40;
  undefined4 local_3c;
  int local_34;
  undefined1 auStack_2c [20];
  undefined4 uStack_18;
  
  pbVar1 = DAT_0049bdf0;
  if (((param_1 == 0) || (param_2 == (int *)0x0)) || (*param_2 == 0)) {
    uVar2 = 0;
  }
  else {
    uStack_18 = param_4;
    FUN_0043c0e4(DAT_0049bdf0,0x68,0);
    FUN_00439c04(pbVar1,DAT_0049bdf4,0x68);
    *pbVar1 = 1;
    *(undefined4 *)(pbVar1 + 4) = *DAT_0049bbf4;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_3c = *(undefined4 *)(pbVar1 + 4);
      local_40 = (uint)*pbVar1;
      FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bdfc,0x97,DAT_0049bdf8);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0049be00,DAT_0049be00,*pbVar1,*(undefined4 *)(pbVar1 + 4));
    }
    FUN_004905f4(auStack_2c,param_1,*param_2);
    FUN_00439c04(&local_40,auStack_2c,0x14);
    iVar3 = FUN_00490c32(&local_40,DAT_0049bbd0,pbVar1);
    if (iVar3 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bdfc,0x9c,DAT_0049bea8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0049bf9c,DAT_0049bf9c);
      }
      uVar2 = 0;
    }
    else {
      *param_2 = local_34;
      uVar2 = 1;
    }
  }
  return uVar2;
}

