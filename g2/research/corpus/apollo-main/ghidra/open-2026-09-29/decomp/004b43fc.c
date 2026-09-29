
undefined4 FUN_004b43fc(byte param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  
  if (param_1 == 0) {
    for (bVar1 = 0; bVar1 < 2; bVar1 = bVar1 + 1) {
      *(undefined1 *)(DAT_004b46f4 + (uint)bVar1 + 0x57) = 3;
    }
  }
  else {
    bVar1 = 0;
    while( true ) {
      if (param_1 <= bVar1) break;
      *(undefined1 *)(DAT_004b46f4 + (uint)*(byte *)(param_2 + (uint)bVar1) + 0x57) = 3;
      bVar1 = bVar1 + 1;
    }
  }
  iVar2 = FUN_004b46a8();
  if (iVar2 == 0) {
    *(undefined1 *)(DAT_004b46f4 + 0x5d) = 0xff;
  }
  DmAdvStop(param_1,param_2);
  return param_4;
}

