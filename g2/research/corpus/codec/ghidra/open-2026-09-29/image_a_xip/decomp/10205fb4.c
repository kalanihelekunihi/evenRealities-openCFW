
undefined4
gx8002_gpio_enable_trigger(uint param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 < 0x20) {
    gx_gpio_set_direction(param_1,0);
    iVar2 = iRam10205fe8;
    *(uint *)(param_1 * 0xc + iRam10205fe8) = param_1;
    iVar2 = iVar2 + param_1 * 0xc;
    *(undefined4 *)(iVar2 + 4) = param_3;
    *(undefined4 *)(iVar2 + 8) = param_4;
    if (param_2 - 1U < 8) {
                    /* WARNING: Could not recover jumptable at 0x10205fe4. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      uVar1 = (*(code *)(*(uint *)(iRam10205fec + (param_2 - 1U) * 4) & 0xfffffffe))();
      return uVar1;
    }
    func_0x1002553c(1,PTR_gx8002_gpio_isr_10206070,0);
    uVar1 = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

