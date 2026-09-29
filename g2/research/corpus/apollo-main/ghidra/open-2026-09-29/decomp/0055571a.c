
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0055571a(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = FUN_00450286();
  if (iVar1 == 0xc) {
    *(undefined1 *)(_DAT_00556260 + 0x21) = 1;
  }
  else if (iVar1 == 0xe) {
    *(undefined1 *)(_DAT_00556260 + 0x21) = 0;
  }
  return unaff_r7;
}

