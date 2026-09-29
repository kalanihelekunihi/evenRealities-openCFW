
undefined4 FUN_0047da16(void)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  
  piVar1 = DAT_0047dc30;
  if (*DAT_0047dc30 == DAT_0047dc34) {
    if (DAT_0047dc30[1] == 1) {
      if ((DAT_0047dc30[3] == 0) || (0x1194 < (uint)DAT_0047dc30[3])) {
        uVar2 = 0;
      }
      else {
        iVar3 = FUN_0047d9fc(DAT_0047dc30);
        if (iVar3 == piVar1[5]) {
          uVar2 = 1;
        }
        else {
          uVar2 = 0;
        }
      }
    }
    else {
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

