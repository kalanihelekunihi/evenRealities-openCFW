
/* WARNING: Heritage AFTER dead removal. Example location: s1 : 0x004e13fc */
/* WARNING: Restarted to delay deadcode elimination for space: register */

uint FUN_004e1192(int param_1,byte *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  double in_d0;
  float local_20;
  float local_1c;
  float local_18;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004e1464,DAT_004e1460,DAT_004e198c,0xd9,DAT_004e1988,param_1);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    uVar2 = iVar1 << 0x1d;
    if (-1 < (int)uVar2) goto LAB_004e11de;
  }
  uVar2 = compress_log_output(0x10400000,DAT_004e1990,DAT_004e1990,param_1);
LAB_004e11de:
  if (param_1 == 0) {
    uVar2 = FUN_004da834(param_2,param_3);
  }
  else if (param_1 == 5) {
    if (((param_2 == (byte *)0x0) || (param_3 == 0)) &&
       ((iVar1 = FUN_00443484(), iVar1 == 0 || (iVar1 = FUN_004434d0(0xe0), iVar1 == 0)))) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004e1464,DAT_004e1460,DAT_004e198c,0xdf,DAT_004e1994);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004e1998,DAT_004e1998);
      }
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = (uint)*param_2;
      if (uVar2 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004e1464,DAT_004e1460,DAT_004e198c,0xe5,DAT_004e199c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004e19a0,DAT_004e19a0);
        }
        FUN_004da16a(0,0,0,6,0,0);
        uVar2 = FUN_00464c36(0xe0,0,0,0);
      }
      else if (uVar2 == 1) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e1464,DAT_004e1460,DAT_004e198c,0xea,DAT_004e19a4);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004e19a8,DAT_004e19a8);
        }
        if (param_3 < 0xd) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004e1464,DAT_004e1460,DAT_004e198c,0xec,DAT_004e19ac);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004e19b0,DAT_004e19b0);
          }
          uVar2 = 0xffffffff;
        }
        else {
          FUN_00439be4(&local_18,param_2 + 1,4);
          FUN_00439be4(&local_1c,param_2 + 5,4);
          FUN_00439be4(&local_20,param_2 + 9,4);
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            in_d0 = (double)local_18;
            FUN_0043d574(4,DAT_004e1464,DAT_004e1460,DAT_004e198c,0xf3,DAT_004e19b4,in_d0,
                         (double)local_1c,(double)local_20);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x10c00000,DAT_004e19b8,DAT_004e19b8);
          }
          uVar2 = FUN_004d9f6e(local_18,(int)((ulonglong)in_d0 >> 0x20),local_20);
        }
      }
    }
  }
  return uVar2;
}

