
undefined8 FUN_005eb47a(byte param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar5 = DAT_005ebc34;
  if ((*(int *)(DAT_005ebc34 + 0x214) == 0) || (*(int *)(DAT_005ebc34 + 0x21c) == 0)) {
    uVar2 = 0;
  }
  else {
    bVar1 = FUN_005eb30c();
    if (param_1 < bVar1) {
      iVar3 = FUN_0044dce2(*(undefined4 *)(iVar5 + 0x21c),param_1);
      if (iVar3 == 0) {
        uVar2 = 0;
      }
      else {
        iVar4 = FUN_005eb438(iVar5);
        iVar5 = FUN_0043fce0(*(undefined4 *)(iVar5 + 0x21c));
        iVar6 = FUN_0043fce0(iVar3);
        iVar3 = FUN_0043fdda(iVar3);
        if ((param_2 < iVar3 + iVar6 + iVar5) && (iVar6 + iVar5 < iVar4 + param_2)) {
          bVar1 = 1;
        }
        else {
          bVar1 = 0;
        }
        uVar2 = (uint)bVar1;
      }
    }
    else {
      uVar2 = 0;
    }
  }
  return CONCAT44(param_4,uVar2);
}

