
undefined4 translate_ui_0059db80(byte param_1)

{
  undefined4 uVar1;
  
  uVar1 = DAT_0059e5dc;
  if (param_1 < 10) {
    uVar1 = *(undefined4 *)(DAT_0059e5e0 + (uint)param_1 * 4);
  }
  return uVar1;
}

