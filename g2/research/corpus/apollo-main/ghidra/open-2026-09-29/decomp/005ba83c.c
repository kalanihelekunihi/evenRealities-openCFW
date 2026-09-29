
void FUN_005ba83c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_28 [16];
  undefined4 uStack_18;
  
  piVar1 = DAT_005baaa4;
  if ((*DAT_005baaa4 != 0) && (uStack_18 = param_4, iVar2 = FUN_0043e2ea(*DAT_005baaa4), iVar2 != 0)
     ) {
    FUN_0043c0e4(auStack_28,0x10,0);
    iVar2 = DAT_005baaec;
    uVar3 = FUN_00460084(*(undefined4 *)(DAT_005baaec + param_1 * 4));
    uVar3 = FUN_0045fffe(*(undefined4 *)(iVar2 + param_1 * 4),uVar3);
    FUN_004b4728(auStack_28,DAT_005baaf0,uVar3,param_3);
    FUN_0049942e(*piVar1,auStack_28);
  }
  return;
}

