
undefined4 gx8002_flash_getinfo(uint param_1)

{
  undefined4 uVar1;
  
  if (param_1 < 0xe) {
                    /* WARNING: Could not recover jumptable at 0x10023862. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uVar1 = (*(code *)(*(uint *)(DAT_10023864 + param_1 * 4) & 0xfffffffe))();
    return uVar1;
  }
  return 0xffffffff;
}

