
undefined8 FUN_005bea46(int param_1)

{
  undefined4 uVar1;
  undefined1 uVar2;
  undefined4 unaff_r7;
  
  if ((param_1 == 0) || (*(int *)(param_1 + 0x1c) == 0)) {
    uVar1 = 0xfffffffe;
  }
  else {
    *(undefined4 *)(param_1 + 0x14) = 0;
    *(undefined4 *)(param_1 + 8) = *(undefined4 *)(param_1 + 0x14);
    *(undefined4 *)(param_1 + 0x18) = 0;
    if (*(int *)(*(int *)(param_1 + 0x1c) + 0xc) == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 7;
    }
    **(undefined1 **)(param_1 + 0x1c) = uVar2;
    FUN_005bdfca(*(undefined4 *)(*(int *)(param_1 + 0x1c) + 0x14),param_1,0);
    uVar1 = 0;
  }
  return CONCAT44(unaff_r7,uVar1);
}

