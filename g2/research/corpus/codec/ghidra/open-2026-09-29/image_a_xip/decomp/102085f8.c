
undefined4 LvpModeTick(void)

{
  undefined4 *puVar1;
  uint uVar2;
  
  puVar1 = puRam10208614;
  uVar2 = *(uint *)(*(int *)(iRam10208618 + puRam10208614[1] * 4) + 0xc);
  if (uVar2 != 0) {
    (*(code *)(uVar2 & 0xfffffffe))();
  }
  return *puVar1;
}

