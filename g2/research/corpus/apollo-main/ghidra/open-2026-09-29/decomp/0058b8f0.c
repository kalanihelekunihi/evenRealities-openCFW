
undefined8 semantic_page_in_ensure_window(uint param_1,undefined4 param_2,uint param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  byte bVar3;
  uint uStack_10;
  uint uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  iVar1 = page_data_lock(0);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else if ((*(int *)(DAT_0058bc08 + 0x5190) == 0) || (*(char *)(DAT_0058bc08 + 0x51a1) == '\0')) {
    semantic_page_data_unlock();
    uVar2 = 0;
  }
  else if (param_1 < *(uint *)(DAT_0058bc08 + 0x5190)) {
    semantic_ensure_range(&uStack_c,&uStack_10);
    if ((param_1 < uStack_c) || (uStack_10 < param_1)) {
      bVar3 = 0;
    }
    else {
      bVar3 = 1;
    }
    semantic_page_data_unlock();
    uVar2 = (uint)bVar3;
  }
  else {
    semantic_page_data_unlock();
    uVar2 = 0;
  }
  return CONCAT44(uStack_10,uVar2);
}

