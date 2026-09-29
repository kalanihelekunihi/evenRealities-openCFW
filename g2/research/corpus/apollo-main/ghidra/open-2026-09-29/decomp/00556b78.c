
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_00556b78(char param_1,int param_2,undefined4 param_3,uint param_4)

{
  undefined *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uStack_10;
  
  *(undefined4 *)(_DAT_00556cbc + 0x24) = 0;
  teleprompt_page_data_deinit();
  puVar1 = PTR_s_ID_TELEPROMPT_CLOSED_00557408;
  uVar4 = _DAT_00557400;
  if (param_1 == '\x01') {
    iVar2 = FUN_0045a568();
    uStack_10 = param_4;
    if (iVar2 == 1) {
      FUN_00464c36(6,0,0,0);
    }
  }
  else if (param_2 == 1) {
    uVar3 = FUN_00460084(_DAT_00557400);
    uVar4 = FUN_0045fffe(uVar4,uVar3);
    uStack_10 = 5000;
    common_exit_prompt_show(*_DAT_00557404,uVar4,6,0);
  }
  else {
    uVar4 = FUN_00460084(PTR_s_ID_TELEPROMPT_CLOSED_00557408);
    uVar4 = FUN_0045fffe(puVar1,uVar4);
    uStack_10 = 0;
    common_exit_prompt_show(*_DAT_00557404,uVar4,6,0);
  }
  return (ulonglong)uStack_10 << 0x20;
}

