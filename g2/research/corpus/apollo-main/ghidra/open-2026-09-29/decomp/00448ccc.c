
undefined4 FUN_00448ccc(int param_1,uint param_2,byte param_3)

{
  int iVar1;
  int iVar2;
  
  if (((*DAT_00448fc4 != '\0') && (param_1 != 0)) && (param_2 != 0)) {
    if (param_3 == 0) {
      param_3 = *DAT_00448fc8;
    }
    if (0xff < param_2) {
      param_2 = 0xff;
    }
    iVar1 = FUN_00448a0c();
    if (iVar1 != 0) {
      FUN_00439be4(iVar1 + 0xd,param_1,param_2);
      *(undefined1 *)(iVar1 + param_2 + 0xd) = 0;
      *(short *)(iVar1 + 8) = (short)param_2;
      *(ushort *)(iVar1 + 10) = (ushort)param_3;
      iVar2 = FUN_00448af0(iVar1);
      if (iVar2 == 0) {
        FUN_00448a8e(iVar1);
        FUN_004733ee(DAT_00448fd0);
      }
    }
  }
  return 0;
}

