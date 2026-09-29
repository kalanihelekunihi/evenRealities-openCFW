
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005b1a14(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar2 = _DAT_005b1b48;
  uVar1 = _DAT_005b1b44;
  if (param_2 == 2) {
    uVar1 = FUN_00460084(_DAT_005b1b48);
    uVar1 = FUN_0045fffe(uVar2,uVar1);
    uVar3 = 0;
    common_exit_prompt_show(*_DAT_005b1b40,uVar1,0xb,1,0,param_4);
  }
  else {
    uVar2 = FUN_00460084(_DAT_005b1b44);
    uVar1 = FUN_0045fffe(uVar1,uVar2);
    uVar3 = 0;
    common_exit_prompt_show(*_DAT_005b1b40,uVar1,0xb,1);
  }
  return (ulonglong)uVar3 << 0x20;
}

