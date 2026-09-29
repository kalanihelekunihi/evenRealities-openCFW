
undefined8 FUN_005d3466(int param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  FUN_0043c0e4(param_3,0x10,0);
  uVar3 = *(int *)(param_1 + 0x234) + param_2;
  if (uVar3 < *(uint *)(param_1 + 0x22c)) {
    *(undefined4 *)(param_3 + 4) = *(undefined4 *)(*(int *)(param_1 + 0x23c) + uVar3 * 4);
    if (*(char *)(param_1 + 0x30) == '\0') {
      *(undefined4 *)(param_3 + 8) = *(undefined4 *)(*(int *)(param_1 + 0x23c) + uVar3 * 4 + 4);
    }
    else if (*(int *)(param_1 + 0x260) == 0) {
      if (*(int *)(param_1 + 0x25c) < 0) {
        iVar2 = 0;
      }
      else {
        iVar2 = *(int *)(param_1 + 0x25c);
      }
      *(int *)(param_3 + 4) = iVar2 + *(int *)(param_3 + 4);
      *(undefined4 *)(param_3 + 8) = *(undefined4 *)(*(int *)(param_1 + 0x23c) + uVar3 * 4 + 4);
    }
    else {
      *(int *)(param_3 + 8) =
           *(int *)(param_3 + 4) + *(int *)(*(int *)(param_1 + 0x260) + uVar3 * 4);
    }
    *(undefined4 *)(param_3 + 0xc) = *(undefined4 *)(param_3 + 4);
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return CONCAT44(param_4,uVar1);
}

