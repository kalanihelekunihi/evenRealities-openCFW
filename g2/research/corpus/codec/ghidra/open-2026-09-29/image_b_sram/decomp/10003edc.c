
undefined4 gx8002_platform_read(uint param_1)

{
  undefined4 uVar1;
  
  if (param_1 < 10) {
                    /* WARNING: Could not recover jumptable at 0x10003ee6. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uVar1 = (*(code *)(*(uint *)(iRam10003ee8 + param_1 * 4) & 0xfffffffe))();
    return uVar1;
  }
  return 0xffffffff;
}

