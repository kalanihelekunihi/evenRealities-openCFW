
undefined4 FUN_0041b6fa(void)

{
  uint *puVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  
  puVar1 = DAT_0041b82c;
  *DAT_0041b82c = 0x20;
  *DAT_0041b834 = 0xffffffff / *puVar1 - 4;
  FUN_0041f4ac(1);
  FUN_0041b64c(0x20,0xff);
  FUN_0041b614(0x20);
  uVar2 = FUN_0041f358(0x80000000);
  uVar3 = FUN_0041f424();
  *DAT_0041b828 = uVar3;
  FUN_0041f440(0,*puVar1);
  FUN_0041f358(uVar2 & DAT_0041b838 | 0x103);
  return in_r3;
}

