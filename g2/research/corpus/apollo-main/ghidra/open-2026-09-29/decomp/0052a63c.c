
void WsfTrace(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  undefined1 auStack_410 [1024];
  undefined4 uStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  uStack_c = param_2;
  uStack_8 = param_3;
  uStack_4 = param_4;
  FUN_00473036(auStack_410,param_1,&uStack_c);
  uVar1 = FUN_004733ee(auStack_410);
  if (0x3ff < uVar1) {
    WsfAssert(DAT_0052a678,0x89);
  }
  FUN_004733ee(&DAT_0052a674);
  return;
}

