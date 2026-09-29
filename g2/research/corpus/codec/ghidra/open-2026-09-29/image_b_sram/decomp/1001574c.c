
undefined4 FUN_1001574c(uint param_1)

{
  undefined4 uVar1;
  
  if (param_1 < 10) {
                    /* WARNING: Could not recover jumptable at 0x10015756. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uVar1 = (*(code *)(*(uint *)(PTR_PTR_10015764 + param_1 * 4) & 0xfffffffe))();
    return uVar1;
  }
  return 0xffffffff;
}

