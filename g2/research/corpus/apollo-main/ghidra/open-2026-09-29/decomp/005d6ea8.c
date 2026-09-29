
undefined8 FUN_005d6ea8(int param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (*(int *)(param_1 + 0xc) == *(int *)(param_1 + 8)) {
    FUN_005d2a0a(*(undefined4 *)(param_1 + 4),0xa1);
    uVar1 = 0;
  }
  else if (*(char *)(*(int *)(param_1 + 0xc) + -4) == '\x02') {
    *(int *)(param_1 + 0xc) = *(int *)(param_1 + 0xc) + -8;
    uVar1 = **(undefined4 **)(param_1 + 0xc);
  }
  else {
    FUN_005d2a0a(*(undefined4 *)(param_1 + 4),0xa0);
    uVar1 = 0;
  }
  return CONCAT44(unaff_r7,uVar1);
}

