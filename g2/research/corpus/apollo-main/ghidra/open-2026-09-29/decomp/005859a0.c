
uint FUN_005859a0(undefined4 param_1,uint param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  char cVar4;
  char local_40 [32];
  undefined4 uStack_20;
  
  cVar4 = '\0';
  uVar2 = param_2;
  uStack_20 = param_4;
  for (; param_2 < param_3; param_2 = param_2 + 0x20) {
    if (param_2 + 0x20 < param_3) {
      uVar3 = 0x20;
    }
    else {
      uVar3 = param_3 - param_2;
    }
    FUN_00585a12(param_1,param_2,local_40,uVar3);
    for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1) {
      if ((cVar4 != -1) && (local_40[uVar1] == -1)) {
        uVar2 = uVar1 + param_2;
      }
      cVar4 = local_40[uVar1];
    }
  }
  if (cVar4 == -1) {
    param_3 = uVar2;
  }
  return param_3;
}

