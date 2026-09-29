
undefined4 * FUN_00515096(void)

{
  undefined4 *puVar1;
  
  puVar1 = (undefined4 *)FUN_0051416c(0xdc);
  if (puVar1 == (undefined4 *)0x0) {
    FUN_0051565c(1);
    return (undefined4 *)0x0;
  }
  *puVar1 = 0;
  puVar1[1] = 0;
  *(undefined1 *)(puVar1 + 0xb) = 0;
  *(undefined1 *)((int)puVar1 + 0xd5) = 0;
  *(undefined1 *)(puVar1 + 0x33) = 0;
  puVar1[0xc] = 0;
  puVar1[0x34] = 0x3f800000;
  puVar1[0x36] = 0xff000000;
  FUN_00561810(puVar1 + 0xd);
  FUN_00561810(puVar1 + 2);
  *(undefined1 *)(puVar1 + 0x35) = 0;
  return puVar1;
}

