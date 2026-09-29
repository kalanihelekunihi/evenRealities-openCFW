
void FUN_005ba8a0(void)

{
  int *piVar1;
  int iVar2;
  undefined4 in_r3;
  undefined1 auStack_50 [64];
  undefined4 uStack_10;
  
  piVar1 = DAT_005baaa0;
  if ((*DAT_005baaa0 != 0) && (uStack_10 = in_r3, iVar2 = FUN_0043e2ea(*DAT_005baaa0), iVar2 != 0))
  {
    FUN_0043c0e4(auStack_50,0x40,0);
    FUN_005b9f58(auStack_50,0x40);
    FUN_0049942e(*piVar1,auStack_50);
  }
  return;
}

