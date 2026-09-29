
undefined8 FUN_004f2ec0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  if (((*DAT_004f33c0 == 1) && (*DAT_004f33bc == 1)) && (*DAT_004f33b4 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x659;
      param_3 = DAT_004f33e0;
      FUN_0043d574(3,DAT_004f33ec,DAT_004f33e8,DAT_004f33e4,0x659,DAT_004f33e0,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004f33f0,DAT_004f33f0);
    }
    puVar1 = DAT_004f33f4;
    iVar2 = FUN_0043e2ea(*DAT_004f33f4);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x65d;
        param_3 = DAT_004f3400;
        FUN_0043d574(1,DAT_004f33ec,DAT_004f33e8,DAT_004f33e4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004f3404,DAT_004f3404);
      }
      goto LAB_004f3020;
    }
    FUN_0044d878(*puVar1);
    uVar3 = FUN_0043de82(*puVar1);
    FUN_0043f4c0(uVar3,0x3fffffff);
    FUN_0044129e(uVar3,0,0);
    FUN_0044131c(uVar3,0,0);
    FUN_004effa8(uVar3,0,0);
    FUN_0048ba78(uVar3,0);
    FUN_0048ba92(uVar3,2,2,2);
    FUN_00441254(uVar3,8,0);
    FUN_0043f6b8(uVar3,9,0,0);
    uVar4 = FUN_00498668(uVar3);
    FUN_00498680(uVar4,DAT_004f33f8);
    FUN_0043f506(uVar4,0x18);
    FUN_0043f568(uVar4,0x18);
    FUN_0043ded4(uVar4,0x10000);
    FUN_0043dfa4(uVar4,0x10);
    uVar4 = FUN_00499416(uVar3);
    uVar3 = DAT_004f33fc;
    uVar5 = FUN_00460084(DAT_004f33fc);
    uVar3 = FUN_0045fffe(uVar3,uVar5);
    FUN_0049942e(uVar4,uVar3);
    FUN_0044143e(uVar4,*DAT_004f339c,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar4,uVar3,0);
  }
  *DAT_004f33bc = 0;
  *DAT_004f33dc = 0;
LAB_004f3020:
  return CONCAT44(param_3,param_2);
}

