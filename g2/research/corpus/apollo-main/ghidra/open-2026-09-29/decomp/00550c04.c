
void FUN_00550c04(int param_1,undefined1 param_2)

{
  byte *pbVar1;
  int iVar2;
  int local_70;
  undefined4 local_6c;
  uint local_68;
  undefined1 *local_60;
  undefined4 local_50;
  undefined4 local_40;
  
  pbVar1 = DAT_00550d38;
  if (param_1 != 0) {
    if (*DAT_00550d38 == 0) {
      *DAT_00550d38 = 4;
      FUN_004503d6(&local_70);
      local_70 = param_1;
      FUN_004506ce(&local_70,0xff,0);
      local_40 = 0xfa;
      local_6c = DAT_00551808;
      local_50 = DAT_0055180c;
      local_60 = &LAB_00550cc4_1;
      FUN_00450408(&local_70);
      FUN_00550f8c(param_2);
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_68 = (uint)*pbVar1;
        local_6c = DAT_00551310;
        local_70 = 0x459;
        FUN_0043d574(2,DAT_005514b8,DAT_0055148c,DAT_005514ec);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_00551318,DAT_00551318,*pbVar1);
      }
    }
  }
  return;
}

