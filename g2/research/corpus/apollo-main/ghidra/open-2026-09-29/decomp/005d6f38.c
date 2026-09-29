
undefined8 FUN_005d6f38(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = FUN_005d6e44(param_1);
  if (param_2 < uVar2) {
    cVar1 = *(char *)(*(int *)(param_1 + 8) + param_2 * 8 + 4);
    if (cVar1 == '\x01') {
      if (*(int *)(*(int *)(param_1 + 8) + param_2 * 8) < 0) {
        iVar3 = -(0x2000 - *(int *)(*(int *)(param_1 + 8) + param_2 * 8) >> 0xe);
      }
      else {
        iVar3 = *(int *)(*(int *)(param_1 + 8) + param_2 * 8) + 0x2000 >> 0xe;
      }
    }
    else if (cVar1 == '\x02') {
      iVar3 = *(int *)(*(int *)(param_1 + 8) + param_2 * 8) << 0x10;
    }
    else {
      iVar3 = *(int *)(*(int *)(param_1 + 8) + param_2 * 8);
    }
  }
  else {
    FUN_005d2a0a(*(undefined4 *)(param_1 + 4),0x82);
    iVar3 = 0;
  }
  return CONCAT44(param_4,iVar3);
}

