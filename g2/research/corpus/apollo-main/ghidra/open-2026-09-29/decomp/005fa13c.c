
undefined4 FUN_005fa13c(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 local_44 [2];
  undefined4 local_3c;
  
  if ((param_3 & 1) == 0) {
    uVar1 = param_3 >> 1;
    FUN_004b1298(2,param_2,uVar1,param_4,0x45,uVar1,0);
    FUN_004b1516(0,0,uVar1,param_4);
    FUN_004b1298(1,param_1,param_3 << 1,param_4,0x34,param_3,0);
    FUN_00561810(local_44);
    local_3c = 0xc0000000;
    local_44[0] = 0x40800000;
    FUN_005226e8(local_44);
    FUN_00513924(1,2,1,0xffffffff);
    FUN_004b146c(0xff000000);
    FUN_00522ae0(0,0,uVar1,param_4);
    FUN_004b1298(1,param_1,param_3 << 1,param_4,0x35,param_3,0);
    FUN_00561810(local_44);
    local_3c = 0;
    local_44[0] = 0x40800000;
    FUN_005226e8(local_44);
    FUN_00513924(DAT_005fa218,2,1,0xffffffff);
    FUN_00513e2e(0);
    FUN_00522ae0(0,0,uVar1,param_4);
    FUN_004b1548();
  }
  return 0;
}

