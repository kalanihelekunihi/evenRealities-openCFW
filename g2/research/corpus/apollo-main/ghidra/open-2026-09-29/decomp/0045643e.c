
undefined4 FUN_0045643e(void)

{
  uint *puVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  
  puVar1 = DAT_00456570;
  *DAT_00456570 = 0x20;
  *DAT_00456578 = 0xffffffff / *puVar1 - 4;
  FUN_0048d6dc(1);
  FUN_00456390(0x20,0xff);
  FUN_00456358(0x20);
  uVar2 = FUN_0048d588(0x80000000);
  uVar3 = FUN_0048d654();
  *DAT_0045656c = uVar3;
  FUN_0048d670(0,*puVar1);
  FUN_0048d588(uVar2 & DAT_0045657c | 0x103);
  return in_r3;
}

