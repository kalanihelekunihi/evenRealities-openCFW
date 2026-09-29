
undefined4 FUN_0044895e(void)

{
  int iVar1;
  undefined4 in_r3;
  int iVar2;
  
  for (iVar2 = 0; iVar1 = DAT_00448f40, iVar2 < 0xfe; iVar2 = iVar2 + 1) {
    FUN_0043c0e4(DAT_00448f40 + iVar2 * 0x110,0x110,0);
    FUN_004488ec(iVar2 * 0x110 + iVar1 + 4,0);
    FUN_00448930(iVar1 + iVar2 * 0x110,iVar2 * 0x110 + iVar1 + 0x110);
  }
  FUN_004488ec(DAT_00448f78 + DAT_00448f40,0);
  FUN_00448930(DAT_00448f90 + iVar1,0);
  FUN_004488ec(DAT_00448f94 + iVar1,0);
  FUN_00448930(DAT_00448fac + iVar1,0);
  FUN_00448930(DAT_00448fb0,iVar1);
  return in_r3;
}

