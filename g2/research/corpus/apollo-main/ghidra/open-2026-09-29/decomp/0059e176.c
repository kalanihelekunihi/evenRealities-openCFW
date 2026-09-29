
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong translate_ui_0059e176(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar2 = _DAT_0059e670;
  uVar1 = _DAT_0059e66c;
  if (param_2 == 1) {
    uVar1 = FUN_00460084(_DAT_0059e670);
    uVar1 = FUN_0045fffe(uVar2,uVar1);
    uVar3 = 5000;
    common_exit_prompt_show(*_DAT_0059e668,uVar1,5,0,5000,param_4);
  }
  else {
    uVar2 = FUN_00460084(_DAT_0059e66c);
    uVar1 = FUN_0045fffe(uVar1,uVar2);
    uVar3 = 0;
    common_exit_prompt_show(*_DAT_0059e668,uVar1,5,1);
  }
  return (ulonglong)uVar3 << 0x20;
}

