
undefined8 FUN_004ea00c(undefined4 *param_1,int param_2,undefined4 *param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  int iVar6;
  
  if ((param_1 == (undefined4 *)0x0) || (param_2 == 0)) {
    iVar2 = FUN_0043d0ce();
    puVar5 = param_1;
    iVar6 = param_2;
    if (iVar2 << 0x1e < 0) {
      puVar5 = (undefined4 *)0xc2;
      iVar6 = DAT_004eacf8;
      FUN_0043d574(1,DAT_004ea7f8,DAT_004ea7f4,DAT_004eacfc,0xc2,DAT_004eacf8,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ead00,DAT_004ead00);
    }
  }
  else {
    param_1[0x16] = param_4;
    param_1[0x15] = param_3;
    puVar5 = param_1;
    iVar6 = param_2;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puVar5 = (undefined4 *)0xca;
      iVar6 = DAT_004ead04;
      FUN_0043d574(4,DAT_004ea7f8,DAT_004ea7f4,DAT_004eacfc,0xca,DAT_004ead04,param_4,param_3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      puVar5 = param_3;
      compress_log_output(0x10800000,DAT_004ead08,DAT_004ead08,param_4);
    }
    uVar3 = FUN_0043de82(param_2);
    *param_1 = uVar3;
    FUN_0043f4c0(*param_1,0x21b,0x120);
    FUN_0043f09a(*param_1,0,param_3);
    FUN_0044129e(*param_1,0,0);
    FUN_0044131c(*param_1,0,0);
    FUN_004e9dd4(*param_1,0,0);
    uVar3 = FUN_00498668(*param_1);
    param_1[1] = uVar3;
    FUN_0043f4c0(param_1[1],0x18,0x18);
    FUN_0043f09a(param_1[1],0,3);
    FUN_0044129e(param_1[1],0,0);
    FUN_0044131c(param_1[1],0,0);
    FUN_0043ded4(param_1[1],0x10000);
    FUN_0043dfa4(param_1[1],0x10);
    uVar3 = FUN_00499416(*param_1);
    param_1[2] = uVar3;
    FUN_0043f4c0(param_1[2],0x3fffffff,0x1e);
    FUN_0043f09a(param_1[2],0x20,0);
    puVar1 = DAT_004ead0c;
    FUN_0044143e(param_1[2],*DAT_004ead0c,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[2],uVar3,0);
    FUN_0044129e(param_1[2],0,0);
    FUN_0044131c(param_1[2],0,0);
    FUN_0049942e(param_1[2],&DAT_004ea254);
    uVar3 = FUN_00499416(*param_1);
    param_1[3] = uVar3;
    FUN_0043f4c0(param_1[3],0x3fffffff,0x1c);
    FUN_0043f09a(param_1[3],0,0x22);
    FUN_0044143e(param_1[3],*puVar1,0);
    FUN_0044129e(param_1[3],0,0);
    FUN_0044131c(param_1[3],0,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[3],uVar3,0);
    FUN_0049942e(param_1[3],&DAT_004ea254);
    uVar3 = FUN_00498668(*param_1);
    param_1[4] = uVar3;
    FUN_0043f4c0(param_1[4],0x84,0x3e);
    FUN_0043f09a(param_1[4],0x102,0);
    FUN_0044129e(param_1[4],0,0);
    FUN_0044131c(param_1[4],0,0);
    FUN_0043ded4(param_1[4],0x10000);
    FUN_0043dfa4(param_1[4],0x10);
    uVar3 = FUN_00499416(*param_1);
    param_1[5] = uVar3;
    FUN_0043f4c0(param_1[5],0x84,0x1e);
    iVar2 = FUN_004ed0ec();
    if (iVar2 == 0) {
      FUN_0043f09a(param_1[5],0x197,0);
    }
    else {
      FUN_0043f09a(param_1[5],0x18d,0);
    }
    FUN_0044145a(param_1[5],3,0);
    FUN_0044143e(param_1[5],*puVar1,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[5],uVar3,0);
    FUN_0044129e(param_1[5],0,0);
    FUN_0044131c(param_1[5],0,0);
    FUN_0049942e(param_1[5],&DAT_004ea254);
    uVar3 = FUN_00499416(*param_1);
    param_1[6] = uVar3;
    FUN_0043f4c0(param_1[6],0x5d,0x1c);
    iVar2 = FUN_004ed0ec();
    if (iVar2 == 0) {
      FUN_0043f09a(param_1[6],0x1be,0x22);
    }
    else {
      FUN_0043f09a(param_1[6],0x1b4,0x22);
    }
    FUN_0044145a(param_1[6],3,0);
    FUN_0044143e(param_1[6],*puVar1,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[6],uVar3,0);
    FUN_0044129e(param_1[6],0,0);
    FUN_0044131c(param_1[6],0,0);
    FUN_0049942e(param_1[6],&DAT_004ea254);
    uVar3 = FUN_00498668(*param_1);
    param_1[7] = uVar3;
    FUN_0043f4c0(param_1[7],0x18,0x18);
    FUN_0043f09a(param_1[7],0,99);
    FUN_0044129e(param_1[7],0,0);
    FUN_0044131c(param_1[7],0,0);
    FUN_0043ded4(param_1[7],0x10000);
    FUN_0043dfa4(param_1[7],0x10);
    uVar3 = FUN_00499416(*param_1);
    param_1[8] = uVar3;
    FUN_0043f4c0(param_1[8],0x3fffffff,0x1e);
    FUN_0043f09a(param_1[8],0x20,0x60);
    FUN_0044143e(param_1[8],*puVar1,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[8],uVar3,0);
    FUN_0044129e(param_1[8],0,0);
    FUN_0044131c(param_1[8],0,0);
    FUN_0049942e(param_1[8],&DAT_004ea254);
    uVar3 = FUN_00499416(*param_1);
    param_1[9] = uVar3;
    FUN_0043f4c0(param_1[9],0x3fffffff,0x1c);
    FUN_0043f09a(param_1[9],0,0x82);
    FUN_0044143e(param_1[9],*puVar1,0);
    FUN_0044129e(param_1[9],0,0);
    FUN_0044131c(param_1[9],0,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[9],uVar3,0);
    FUN_0049942e(param_1[9],&DAT_004ea254);
    uVar3 = FUN_00498668(*param_1);
    param_1[10] = uVar3;
    FUN_0043f4c0(param_1[10],0x84,0x3e);
    FUN_0043f09a(param_1[10],0x102,0x60);
    FUN_0044129e(param_1[10],0,0);
    FUN_0044131c(param_1[10],0,0);
    FUN_0043ded4(param_1[10],0x10000);
    FUN_0043dfa4(param_1[10],0x10);
    uVar3 = FUN_00499416(*param_1);
    param_1[0xb] = uVar3;
    FUN_0043f4c0(param_1[0xb],0x84,0x1e);
    iVar2 = FUN_004ed0ec();
    if (iVar2 == 0) {
      FUN_0043f09a(param_1[0xb],0x197,0x60);
    }
    else {
      FUN_0043f09a(param_1[0xb],0x18d,0x60);
    }
    FUN_0044145a(param_1[0xb],3,0);
    FUN_0044143e(param_1[0xb],*puVar1,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[0xb],uVar3,0);
    FUN_0044129e(param_1[0xb],0,0);
    FUN_0044131c(param_1[0xb],0,0);
    FUN_0049942e(param_1[0xb],&DAT_004ea254);
    uVar3 = FUN_00499416(*param_1);
    param_1[0xc] = uVar3;
    FUN_0043f4c0(param_1[0xc],0x5d,0x1c);
    iVar2 = FUN_004ed0ec();
    if (iVar2 == 0) {
      FUN_0043f09a(param_1[0xc],0x1be,0x82);
    }
    else {
      FUN_0043f09a(param_1[0xc],0x1b4,0x82);
    }
    FUN_0044145a(param_1[0xc],3,0);
    FUN_0044143e(param_1[0xc],*puVar1,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[0xc],uVar3,0);
    FUN_0044129e(param_1[0xc],0,0);
    FUN_0044131c(param_1[0xc],0,0);
    FUN_0049942e(param_1[0xc],&DAT_004ea254);
    uVar3 = FUN_00498668(*param_1);
    param_1[0xd] = uVar3;
    FUN_0043f4c0(param_1[0xd],0x18,0x18);
    FUN_0043f09a(param_1[0xd],0,0xc3);
    FUN_0044129e(param_1[0xd],0,0);
    FUN_0044131c(param_1[0xd],0,0);
    FUN_0043ded4(param_1[0xd],0x10000);
    FUN_0043dfa4(param_1[0xd],0x10);
    uVar3 = FUN_00499416(*param_1);
    param_1[0xe] = uVar3;
    FUN_0043f4c0(param_1[0xe],0x3fffffff,0x1e);
    FUN_0043f09a(param_1[0xe],0x20,0xc0);
    FUN_0044143e(param_1[0xe],*puVar1,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[0xe],uVar3,0);
    FUN_0044129e(param_1[0xe],0,0);
    FUN_0044131c(param_1[0xe],0,0);
    FUN_0049942e(param_1[0xe],&DAT_004ea254);
    uVar3 = FUN_00499416(*param_1);
    param_1[0xf] = uVar3;
    FUN_0043f4c0(param_1[0xf],0x3fffffff,0x1c);
    FUN_0043f09a(param_1[0xf],0,0xe2);
    FUN_0044143e(param_1[0xf],*puVar1,0);
    FUN_0044129e(param_1[0xf],0,0);
    FUN_0044131c(param_1[0xf],0,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[0xf],uVar3,0);
    FUN_0049942e(param_1[0xf],&DAT_004ea254);
    uVar3 = FUN_00498668(*param_1);
    param_1[0x10] = uVar3;
    FUN_0043f4c0(param_1[0x10],0x84,0x3e);
    FUN_0043f09a(param_1[0x10],0x102,0xc0);
    FUN_0044129e(param_1[0x10],0,0);
    FUN_0044131c(param_1[0x10],0,0);
    FUN_0043ded4(param_1[0x10],0x10000);
    FUN_0043dfa4(param_1[0x10],0x10);
    uVar3 = FUN_00499416(*param_1);
    param_1[0x11] = uVar3;
    FUN_0043f4c0(param_1[0x11],0x84,0x1e);
    iVar2 = FUN_004ed0ec();
    if (iVar2 == 0) {
      FUN_0043f09a(param_1[0x11],0x197,0xc0);
    }
    else {
      FUN_0043f09a(param_1[0x11],0x18d,0xc0);
    }
    FUN_0044145a(param_1[0x11],3,0);
    FUN_0044143e(param_1[0x11],*puVar1,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[0x11],uVar3,0);
    FUN_0044129e(param_1[0x11],0,0);
    FUN_0044131c(param_1[0x11],0,0);
    FUN_0049942e(param_1[0x11],&DAT_004ea254);
    uVar3 = FUN_00499416(*param_1);
    param_1[0x12] = uVar3;
    FUN_0043f4c0(param_1[0x12],0x5d,0x1c);
    iVar2 = FUN_004ed0ec();
    if (iVar2 == 0) {
      FUN_0043f09a(param_1[0x12],0x1be,0xe2);
    }
    else {
      FUN_0043f09a(param_1[0x12],0x1b4,0xe2);
    }
    FUN_0044145a(param_1[0x12],3,0);
    FUN_0044143e(param_1[0x12],*puVar1,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[0x12],uVar3,0);
    FUN_0044129e(param_1[0x12],0,0);
    FUN_0044131c(param_1[0x12],0,0);
    FUN_0049942e(param_1[0x12],&DAT_004ea254);
    uVar3 = FUN_0043de82(*param_1);
    param_1[0x13] = uVar3;
    FUN_0043f4c0(param_1[0x13],0x218,1);
    FUN_0043f09a(param_1[0x13],0,0x4f);
    uVar3 = DAT_004eb31c;
    uVar4 = FUN_0044104c(DAT_004eb31c);
    FUN_0044127e(param_1[0x13],uVar4,0);
    FUN_0044129e(param_1[0x13],0xff,0);
    FUN_0044131c(param_1[0x13],0,0);
    FUN_004e9dd4(param_1[0x13],0,0);
    uVar4 = FUN_0043de82(*param_1);
    param_1[0x14] = uVar4;
    FUN_0043f4c0(param_1[0x14],0x218,1);
    FUN_0043f09a(param_1[0x14],0,0xaf);
    uVar3 = FUN_0044104c(uVar3);
    FUN_0044127e(param_1[0x14],uVar3,0);
    FUN_0044129e(param_1[0x14],0xff,0);
    FUN_0044131c(param_1[0x14],0,0);
    FUN_004e9dd4(param_1[0x14],0,0);
    *(undefined1 *)(param_1 + 0x17) = 0;
  }
  return CONCAT44(iVar6,puVar5);
}

