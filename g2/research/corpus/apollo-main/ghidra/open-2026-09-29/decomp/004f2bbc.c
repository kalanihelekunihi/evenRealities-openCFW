
undefined4 FUN_004f2bbc(undefined4 param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_38;
  undefined4 local_34;
  undefined1 auStack_30 [24];
  undefined1 auStack_18 [4];
  undefined1 auStack_14 [4];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar1 = FUN_0043e2ea(param_1);
  if (iVar1 != 0) {
    FUN_0044d878(param_1);
  }
  uVar2 = FUN_0043de82(param_1);
  FUN_0043f4c0(uVar2,0x3fffffff);
  FUN_0044129e(uVar2,0,0);
  FUN_0044131c(uVar2,0,0);
  FUN_004effa8(uVar2,0,0);
  FUN_0048ba78(uVar2,0);
  FUN_0048ba92(uVar2,2,2,2);
  FUN_00441254(uVar2,8,0);
  FUN_0043f6b8(uVar2,9,0,0);
  FUN_00439c04(auStack_30,DAT_004f33a4,0x20);
  local_38 = FUN_00441094();
  FUN_00439be4(auStack_18,&local_38,3);
  local_38 = FUN_004410a6();
  FUN_00439be4(auStack_14,&local_38,3);
  iVar1 = FUN_00463c68(uVar2,auStack_30);
  *param_2 = iVar1;
  if (*param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_34 = DAT_004f33a8;
      local_38 = 0x618;
      FUN_0043d574(1,DAT_004f2eb4,DAT_004f2eb0,DAT_004f33ac);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004f33b0,DAT_004f33b0);
    }
    uVar2 = 0xffffffff;
  }
  else {
    FUN_00463ea6(*param_2);
    *DAT_004f33b4 = 1;
    *DAT_004f33b8 = 600;
    *DAT_004f33bc = 0;
    uVar2 = 0;
  }
  return uVar2;
}

