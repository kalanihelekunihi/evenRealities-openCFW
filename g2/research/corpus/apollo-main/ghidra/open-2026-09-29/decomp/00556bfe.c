
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_00556bfe(void)

{
  undefined *puVar1;
  undefined4 uVar2;
  undefined4 in_r3;
  uint uVar3;
  
  *(undefined4 *)(_DAT_00556cbc + 0x24) = 0;
  teleprompt_page_data_deinit();
  puVar1 = PTR_s_ID_TELEPROMPT_CLOSED_00557408;
  uVar2 = FUN_00460084(PTR_s_ID_TELEPROMPT_CLOSED_00557408);
  uVar2 = FUN_0045fffe(puVar1,uVar2);
  uVar3 = 0;
  common_exit_prompt_show(*_DAT_00557404,uVar2,6,1,0,in_r3);
  return (ulonglong)uVar3 << 0x20;
}

