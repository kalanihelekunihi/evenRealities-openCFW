
undefined8 smpCcbByHandle(undefined2 param_1)

{
  byte bVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  bVar1 = DmConnIdByHandle(param_1);
  if (bVar1 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = DAT_00537ebc + (uint)bVar1 * 0x4c + -0x4c;
  }
  return CONCAT44(unaff_r7,iVar2);
}

