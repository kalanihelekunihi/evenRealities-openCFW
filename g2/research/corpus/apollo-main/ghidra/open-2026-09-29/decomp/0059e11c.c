
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong translate_ui_0059e11c(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  
  uVar2 = _DAT_0059e66c;
  puVar1 = PTR_s_ID_GENERAL_BLUETOOTH_DISCONNECT_0059e664;
  if (param_2 == 1) {
    uVar2 = FUN_00460084(PTR_s_ID_GENERAL_BLUETOOTH_DISCONNECT_0059e664);
    uVar2 = FUN_0045fffe(puVar1,uVar2);
    uVar4 = 5000;
    common_exit_prompt_show(*_DAT_0059e668,uVar2,5,0,5000,param_4);
  }
  else {
    uVar3 = FUN_00460084(_DAT_0059e66c);
    uVar2 = FUN_0045fffe(uVar2,uVar3);
    uVar4 = 0;
    common_exit_prompt_show(*_DAT_0059e668,uVar2,5,0);
  }
  return (ulonglong)uVar4 << 0x20;
}

