
undefined8 FUN_005514f0(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  if ((param_1 == 0) || (param_2 == (undefined4 *)0x0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x642;
      FUN_0043d574(1,DAT_0055221c,DAT_00552218,DAT_00551ed0,0x642,DAT_00551ecc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00551ed4);
    }
    param_2 = (undefined4 *)0x0;
  }
  else {
    FUN_0043c0e4(param_2,0x1c,0,param_4,param_3,param_4);
    uVar3 = FUN_0043de82(param_1);
    *param_2 = uVar3;
    FUN_0043f506(*param_2,0x1d9);
    FUN_0043f568(*param_2,0x3fffffff);
    FUN_004411aa(*param_2,0xa6,0);
    FUN_0043f09a(*param_2,0x2e,0);
    FUN_0044131c(*param_2,0,0);
    FUN_0054fa24(*param_2,0,0);
    uVar3 = FUN_0044104c(0);
    FUN_0044127e(*param_2,uVar3,0);
    FUN_0044129e(*param_2,0xff,0);
    FUN_0043dfa4(*param_2,0x12);
    uVar3 = FUN_00499416(*param_2);
    param_2[1] = uVar3;
    FUN_0043f506(param_2[1],0x15b);
    FUN_0043f568(param_2[1],0x1e);
    FUN_0043f6b8(param_2[1],1,0,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_2[1],uVar3,0);
    puVar1 = DAT_00552220;
    FUN_0044143e(param_2[1],*DAT_00552220,0);
    FUN_0044131c(param_2[1],0,0);
    FUN_0054fa24(param_2[1],0,0);
    FUN_00499678(param_2[1],1);
    FUN_0049942e(param_2[1],DAT_00552224);
    uVar3 = FUN_00499416(*param_2);
    param_2[5] = uVar3;
    FUN_0043f506(param_2[5],0x6e);
    FUN_0043f568(param_2[5],0x1e);
    FUN_0043f6b8(param_2[5],3,0,0);
    uVar3 = FUN_0044104c(DAT_00551810);
    FUN_0044140e(param_2[5],uVar3,0);
    FUN_0044143e(param_2[5],*puVar1,0);
    FUN_0044145a(param_2[5],3,0);
    FUN_0044131c(param_2[5],0,0);
    FUN_0054fa24(param_2[5],0,0);
    FUN_0049942e(param_2[5],DAT_00552228);
    uVar3 = FUN_00499416(*param_2);
    param_2[2] = uVar3;
    FUN_0043f506(param_2[2],0x3fffffff);
    FUN_0043f568(param_2[2],0x1e);
    FUN_0043f6d6(param_2[2],param_2[1],0xd,0,0xc);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_2[2],uVar3,0);
    FUN_0044143e(param_2[2],*puVar1,0);
    FUN_0044131c(param_2[2],0,0);
    FUN_0054fa24(param_2[2],0,0);
    FUN_00499678(param_2[2],1);
    FUN_0049942e(param_2[2],DAT_0055222c);
    uVar3 = FUN_00498668(*param_2);
    param_2[3] = uVar3;
    FUN_0043f4c0(param_2[3],0x18,0x18);
    FUN_00498680(param_2[3],DAT_00552230);
    FUN_0043f6d6(param_2[3],param_2[2],0x14,0,0);
    uVar3 = FUN_00499416(*param_2);
    param_2[4] = uVar3;
    FUN_0043f506(param_2[4],0x3fffffff);
    FUN_0043f568(param_2[4],0x1e);
    FUN_0043f6d6(param_2[4],param_2[3],0x14,0,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_2[4],uVar3,0);
    FUN_0044143e(param_2[4],*puVar1,0);
    FUN_0044131c(param_2[4],0,0);
    FUN_0054fa24(param_2[4],0,0);
    FUN_00499678(param_2[4],1);
    FUN_0049942e(param_2[4],DAT_00552234);
    uVar3 = FUN_00499416(*param_2);
    param_2[6] = uVar3;
    FUN_0043f506(param_2[6],0x1d9);
    FUN_00499678(param_2[6],0);
    FUN_0043f568(param_2[6],0x3fffffff);
    param_3 = 4;
    FUN_0043f6d6(param_2[6],param_2[2],0xd,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_2[6],uVar3,0);
    FUN_0044143e(param_2[6],*puVar1,0);
    FUN_0044131c(param_2[6],0,0);
    FUN_0054fa24(param_2[6],0,0);
    FUN_0049942e(param_2[6],PTR_s_detail_00552238);
  }
  return CONCAT44(param_3,param_2);
}

