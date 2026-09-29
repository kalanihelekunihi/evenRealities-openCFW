
int FUN_0055025c(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  if ((param_1 & 0xff) < 3) {
    if (*(char *)((param_1 & 0xff) * 0xc + DAT_00550948 + 10) == '\0') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00550958,DAT_00550954,DAT_00550cbc,0x1fd,DAT_00550d34,param_1 & 0xff);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_00550eb8,DAT_00550eb8,param_1 & 0xff);
      }
      iVar1 = -1;
    }
    else {
      iVar1 = (int)(short)(ushort)*(byte *)(DAT_00550948 + (param_1 & 0xff) * 0xc + 8);
    }
  }
  else {
    uVar2 = param_1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = param_1 & 0xff;
      uVar2 = 0x1f5;
      param_2 = DAT_00550cb8;
      FUN_0043d574(2,DAT_00550958,DAT_00550954,DAT_00550cbc,0x1f5,DAT_00550cb8,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00550cc0,DAT_00550cc0,param_1 & 0xff,uVar2,param_2,param_3);
    }
    iVar1 = -1;
  }
  return iVar1;
}

