
undefined8 semantic_range_ready(undefined4 param_1,undefined4 param_2,uint param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint local_10;
  uint local_c;
  
  local_10 = param_3;
  local_c = param_4;
  semantic_ensure_range(&local_10,&local_c);
  uVar3 = local_10;
  do {
    if (local_c < uVar3) {
      uVar1 = 1;
LAB_0058af4c:
      return CONCAT44(local_10,uVar1);
    }
    uVar1 = semantic_page_to_slot(uVar3);
    iVar2 = semantic_slot_loaded(uVar1,uVar3);
    if (iVar2 == 0) {
      uVar1 = 0;
      goto LAB_0058af4c;
    }
    uVar3 = uVar3 + 1;
  } while( true );
}

