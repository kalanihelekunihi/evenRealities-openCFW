
undefined4 FUN_0052e854(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  
  FUN_00480f0c(0xf,*DAT_0052f21c);
  FUN_00480fd6(0xf,0);
  for (uVar1 = 0; uVar1 < (uint)(param_1 * 1000) / 0x21; uVar1 = uVar1 + 1) {
    FUN_00480fd6(0xf,0);
    FUN_00491102(0x10);
    FUN_00480fd6(0xf,1);
    FUN_00491102(0x10);
  }
  return param_4;
}

