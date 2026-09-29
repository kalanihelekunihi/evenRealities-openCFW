
undefined4 * FUN_0047ebd8(void)

{
  undefined4 *puVar1;
  
  puVar1 = (undefined4 *)pvPortMalloc(0x20);
  if (puVar1 != (undefined4 *)0x0) {
    *puVar1 = 0;
    vListInitialise(puVar1 + 1);
    *(undefined1 *)(puVar1 + 7) = 0;
  }
  return puVar1;
}

