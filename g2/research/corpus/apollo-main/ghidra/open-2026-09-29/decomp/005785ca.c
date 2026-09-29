
undefined4 semantic_CodecGetPackageVersion(undefined4 *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int local_20;
  undefined4 local_1c;
  
  if (param_1 == (undefined4 *)0x0) {
    iVar1 = FUN_0043d0ce(0);
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_00578c9c,0x10a,DAT_00578c98);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00578ca0,DAT_00578ca0);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = FUN_0043d0ce(0);
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005787e8,DAT_005787e4,DAT_00578c9c,0x10e,DAT_00579134,DAT_005787d8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00579138,DAT_00579138,DAT_005787d8);
    }
    uVar2 = DAT_005787d8;
    iVar1 = file_open(DAT_005787d8,&DAT_005787d4);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_00578c9c,0x113,DAT_00579140,uVar2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00579144,DAT_00579144,uVar2);
      }
      uVar2 = 0xffffffff;
    }
    else {
      iVar3 = file_read(&local_20,1,0x10,iVar1);
      if (iVar3 == 0x10) {
        if (iVar1 != 0) {
          file_close(iVar1);
        }
        iVar1 = DAT_00578804;
        if (local_20 == DAT_00578804) {
          *param_1 = local_1c;
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,DAT_005787e8,DAT_005787e4,DAT_00578c9c,0x128,DAT_00579150,*param_1);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_00579154,DAT_00579154,*param_1);
          }
          uVar2 = 0;
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_00578c9c,0x123,DAT_00578808,local_20,iVar1)
            ;
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_0057880c,DAT_0057880c,local_20,iVar1);
          }
          uVar2 = 0xffffffff;
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_00578c9c,0x11a,DAT_00579148,iVar3);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0057914c,DAT_0057914c,iVar3);
        }
        if (iVar1 != 0) {
          file_close(iVar1);
        }
        uVar2 = 0xffffffff;
      }
    }
  }
  return uVar2;
}

