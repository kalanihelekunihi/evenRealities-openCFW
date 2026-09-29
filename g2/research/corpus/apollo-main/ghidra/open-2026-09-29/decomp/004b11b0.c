
undefined4 FUN_004b11b0(void)

{
  int *piVar1;
  int iVar2;
  
  iVar2 = FUN_0051403c(0x1ec);
  piVar1 = DAT_004b178c;
  if (iVar2 != DAT_004b1790) {
    *(uint *)(*DAT_004b178c + 0x20) = *(uint *)(*DAT_004b178c + 0x20) | 2;
    return 0xffffffff;
  }
  FUN_005144ba();
  FUN_0048949c(*piVar1,0x100);
  FUN_00523c88();
  FUN_00514046(0xe8,0);
  FUN_00514046(0xfc,0);
  FUN_00514046(0x388,1);
  FUN_00523304(0);
  FUN_005138a4();
  FUN_00514846(0x200,0);
  FUN_00514846(0x204,0xffffffff);
  iVar2 = FUN_00522602();
  if (iVar2 << 0xd < 0) {
    FUN_0052296a(7);
    *(undefined1 *)(*piVar1 + 9) = 0;
    FUN_0052262e(*(byte *)(*piVar1 + 8) | *(byte *)(*piVar1 + 9));
  }
  else {
    *(undefined1 *)(*piVar1 + 10) = 0;
  }
  iVar2 = *piVar1;
  *(undefined4 *)(iVar2 + 0x14) = 0;
  *(uint *)(iVar2 + 0x18) =
       *(uint *)(iVar2 + 0xc) | *(uint *)(iVar2 + 0x10) | *(uint *)(iVar2 + 0x1c);
  iVar2 = FUN_0052261a();
  if (iVar2 << 0x16 < 0) {
    FUN_00514046(0x374,0);
    FUN_00514046(0x368,0);
  }
  return 0;
}

