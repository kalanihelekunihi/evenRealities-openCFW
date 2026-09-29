
undefined4 semantic_find_requestable(uint param_1,uint param_2,undefined4 param_3,uint *param_4)

{
  int iVar1;
  int iVar2;
  
  while( true ) {
    if (param_2 < param_1) {
      return 0;
    }
    iVar1 = semantic_page_to_slot(param_1);
    iVar2 = semantic_slot_loaded(iVar1,param_1);
    if ((iVar2 == 0) &&
       (((*(char *)(iVar1 * 0x414 + DAT_0058bc08 + 0x40c) != '\x01' ||
         (*(uint *)(DAT_0058bc08 + iVar1 * 0x414) != param_1)) ||
        (iVar1 = semantic_loading_timed_out(iVar1,param_1,param_3), iVar1 != 0)))) break;
    param_1 = param_1 + 1;
  }
  *param_4 = param_1;
  return 1;
}

