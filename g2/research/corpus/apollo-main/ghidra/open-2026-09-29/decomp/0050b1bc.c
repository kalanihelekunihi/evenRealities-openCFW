
undefined8 FUN_0050b1bc(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  if ((param_1 != (undefined4 *)0x0) && (param_2 != 0)) {
    uVar2 = FUN_0043de82(param_2);
    *param_1 = uVar2;
    FUN_0043f4c0(*param_1,0x240,0x120);
    FUN_0043f09a(*param_1,0,param_3);
    uVar2 = FUN_0044104c(0);
    FUN_0044127e(*param_1,uVar2,0);
    FUN_0044129e(*param_1,0,0);
    FUN_00509fdc(*param_1,0,0);
    FUN_0044131c(*param_1,0,0);
    FUN_0043dfa4(*param_1,2);
    uVar2 = FUN_0043de82(*param_1);
    param_1[1] = uVar2;
    FUN_0043f4c0(param_1[1],0x240,0x120);
    FUN_0043f09a(param_1[1],0,0);
    FUN_0044129e(param_1[1],0,0);
    FUN_00509fdc(param_1[1],0,0);
    FUN_0044131c(param_1[1],0,0);
    FUN_0044e3ca(param_1[1],0xc);
    FUN_0044e368(param_1[1],0);
    uVar2 = FUN_0044104c(0xffffff);
    FUN_0044127e(param_1[1],uVar2,0x10000);
    FUN_0044129e(param_1[1],0xb4,0x10000);
    FUN_00441164(param_1[1],4,0x10000);
    uVar2 = FUN_00498668(param_1[1]);
    param_1[2] = uVar2;
    FUN_00498680(param_1[2],DAT_0050b718);
    FUN_0043f4c0(param_1[2],0x18,0x18);
    FUN_0043f09a(param_1[2],0x14,0x10);
    FUN_0043ded4(param_1[2],0x10000);
    FUN_0043dfa4(param_1[2],0x10);
    uVar2 = FUN_00499416(param_1[1]);
    param_1[3] = uVar2;
    FUN_0043f4c0(param_1[3],0x1b8,0x1c);
    FUN_0043f09a(param_1[3],0x34,0x10);
    FUN_00499678(param_1[3],1);
    uVar2 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[3],uVar2,0);
    puVar1 = DAT_0050b720;
    FUN_0044143e(param_1[3],*DAT_0050b720,0);
    uVar2 = FUN_00499416(param_1[1]);
    param_1[4] = uVar2;
    FUN_0043f4c0(param_1[4],0x3fffffff,0x1c);
    FUN_0043f6d6(param_1[4],param_1[1],3,0xfffffff0,0x10);
    FUN_00499678(param_1[4],1);
    uVar2 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[4],uVar2,0);
    FUN_0044143e(param_1[4],*puVar1,0);
    FUN_0044145a(param_1[4],3,0);
    uVar2 = FUN_00499416(param_1[1]);
    param_1[5] = uVar2;
    FUN_0043f4c0(param_1[5],0x168,0x3fffffff);
    FUN_0043f09a(param_1[5],0x14,0x38);
    uVar2 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[5],uVar2,0);
    FUN_0044143e(param_1[5],*puVar1,0);
    FUN_00499678(param_1[5],0);
    uVar2 = FUN_00499416(param_1[1]);
    param_1[6] = uVar2;
    FUN_0043f4c0(param_1[6],0x21b,0x3fffffff);
    uVar3 = 0x1c;
    FUN_0043f6d6(param_1[6],param_1[5],0xd,0);
    uVar2 = FUN_0044104c(0xffffff);
    FUN_0044140e(param_1[6],uVar2,0);
    FUN_0044143e(param_1[6],*puVar1,0);
    FUN_00499678(param_1[6],0);
    param_1[7] = 0;
    param_1[8] = param_3;
    *(undefined1 *)(param_1 + 9) = 0;
    *(undefined1 *)((int)param_1 + 0x25) = 1;
    *(undefined1 *)((int)param_1 + 0x26) = 1;
    *(undefined1 *)((int)param_1 + 0x27) = 0;
    *(undefined1 *)(param_1 + 10) = 0;
    *(undefined1 *)((int)param_1 + 0x29) = 0;
    param_1[0xb] = 0;
    param_3 = uVar3;
  }
  return CONCAT44(param_4,param_3);
}

