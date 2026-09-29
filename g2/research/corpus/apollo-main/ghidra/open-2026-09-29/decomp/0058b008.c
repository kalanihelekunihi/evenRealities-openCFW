
undefined8
semantic_find_next_request
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  local_20 = param_2;
  local_1c = param_3;
  uStack_18 = param_4;
  semantic_ensure_range(&local_1c,&local_20);
  iVar2 = *(int *)(DAT_0058bc08 + 0x5194);
  uVar3 = iVar2 + 3;
  if (*(uint *)(DAT_0058bc08 + 0x5190) <= uVar3) {
    uVar3 = *(int *)(DAT_0058bc08 + 0x5190) - 1;
  }
  uVar1 = osKernelGetTickCount();
  iVar2 = semantic_find_requestable(iVar2,uVar3,uVar1,param_1);
  if (iVar2 == 0) {
    uVar1 = semantic_find_requestable(local_1c,local_20,uVar1,param_1);
  }
  else {
    uVar1 = 1;
  }
  return CONCAT44(local_20,uVar1);
}

