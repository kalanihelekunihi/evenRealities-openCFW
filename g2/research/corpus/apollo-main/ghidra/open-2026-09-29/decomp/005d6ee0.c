
undefined8 FUN_005d6ee0(int param_1)

{
  char cVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  if (*(int *)(param_1 + 0xc) == *(int *)(param_1 + 8)) {
    FUN_005d2a0a(*(undefined4 *)(param_1 + 4),0xa1);
    iVar2 = 0;
  }
  else {
    *(int *)(param_1 + 0xc) = *(int *)(param_1 + 0xc) + -8;
    cVar1 = *(char *)(*(int *)(param_1 + 0xc) + 4);
    if (cVar1 == '\x01') {
      if (**(int **)(param_1 + 0xc) < 0) {
        iVar2 = -(0x2000 - **(int **)(param_1 + 0xc) >> 0xe);
      }
      else {
        iVar2 = **(int **)(param_1 + 0xc) + 0x2000 >> 0xe;
      }
    }
    else if (cVar1 == '\x02') {
      iVar2 = **(int **)(param_1 + 0xc) << 0x10;
    }
    else {
      iVar2 = **(int **)(param_1 + 0xc);
    }
  }
  return CONCAT44(unaff_r7,iVar2);
}

