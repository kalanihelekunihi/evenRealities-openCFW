
undefined4 FUN_005eb61e(undefined1 param_1)

{
  undefined4 uVar1;
  
  if (*(int *)(DAT_005ebc34 + 0x214) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = FUN_0044e498(*(undefined4 *)(DAT_005ebc34 + 0x214));
    uVar1 = FUN_005eb576(param_1,uVar1);
  }
  return uVar1;
}

