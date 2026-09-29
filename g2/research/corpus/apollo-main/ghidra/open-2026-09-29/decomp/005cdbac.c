
undefined8 FUN_005cdbac(undefined4 *param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iStack_20;
  int iStack_1c;
  undefined4 uStack_18;
  
  uVar1 = *param_1;
  iStack_20 = param_2;
  iStack_1c = param_3;
  uStack_18 = param_4;
  iVar2 = FUN_00450286(param_1);
  iVar3 = FUN_0044dca2(uVar1);
  if (iVar2 == 0x33) {
    uVar1 = FUN_005cda66(iVar3);
    FUN_005cd7cc(iVar3,uVar1,0);
  }
  else if ((iVar2 == 0xe) &&
          ((iVar2 = FUN_00452ef8(), iVar2 == 0 || (*(char *)(iVar2 + 8) != '\x01')))) {
    FUN_0044e75e(uVar1,&iStack_20);
    if ((*(byte *)(iVar3 + 0x30) & 0xc) == 0) {
      iVar2 = FUN_0043fe70(uVar1);
      iVar2 = (iVar2 / 2 + iStack_1c) / iVar2;
    }
    else {
      iVar2 = FUN_0043fe16(uVar1);
      iVar4 = FUN_005cd7c0(iVar3,0);
      if (iVar4 == 1) {
        iVar2 = (iVar2 / 2 - iStack_20) / iVar2;
      }
      else {
        iVar2 = (iVar2 / 2 + iStack_20) / iVar2;
      }
    }
    if (iVar2 < 0) {
      iVar2 = 0;
    }
    iVar4 = FUN_005cda66(iVar3);
    iVar5 = FUN_00452ef8();
    if (iVar5 == 0) {
      FUN_005cd7cc(iVar3,iVar2,0);
    }
    else {
      FUN_005cd7cc(iVar3,iVar2,1);
    }
    if (iVar2 != iVar4) {
      FUN_00451670(iVar3,0x23,0);
    }
  }
  return CONCAT44(iStack_1c,iStack_20);
}

