
undefined4 * FUN_004199bc(void)

{
  undefined4 *puVar1;
  
  puVar1 = (undefined4 *)FUN_00419730(0x20);
  if (puVar1 != (undefined4 *)0x0) {
    *puVar1 = 0;
    FUN_0041b53c(puVar1 + 1);
    *(undefined1 *)(puVar1 + 7) = 0;
  }
  return puVar1;
}

