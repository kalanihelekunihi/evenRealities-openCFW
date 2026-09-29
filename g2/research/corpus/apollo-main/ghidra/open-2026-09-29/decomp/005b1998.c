
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005b1998(char param_1,int param_2,uint param_3,undefined4 param_4)

{
  undefined *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  uVar3 = _DAT_005b1b44;
  puVar1 = PTR_s_ID_GENERAL_BLUETOOTH_DISCONNECT_005b1b3c;
  if (param_1 == '\x03') {
    iVar2 = FUN_0045a568();
    if (iVar2 == 1) {
      FUN_00464c36(0xb,0,0,0,param_3,param_4);
    }
  }
  else if (param_2 == 1) {
    uVar3 = FUN_00460084(PTR_s_ID_GENERAL_BLUETOOTH_DISCONNECT_005b1b3c);
    uVar3 = FUN_0045fffe(puVar1,uVar3);
    param_3 = 5000;
    common_exit_prompt_show(*_DAT_005b1b40,uVar3,0xb,0);
  }
  else {
    uVar4 = FUN_00460084(_DAT_005b1b44);
    uVar3 = FUN_0045fffe(uVar3,uVar4);
    param_3 = 0;
    common_exit_prompt_show(*_DAT_005b1b40,uVar3,0xb,0);
  }
  return (ulonglong)param_3 << 0x20;
}

