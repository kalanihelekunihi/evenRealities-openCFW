
void touch_product_05e0_bringup(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  uint uVar2;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = *DAT_00003938;
  uStack_c = DAT_00003938[1];
  iVar1 = touch_config_197c_initialize(DAT_0000393c,param_2,&stack0xfffffff8,DAT_00003938 + 2);
  if (iVar1 == 0) {
    Cy_SysInt_Init(&local_10,DAT_00003940);
    uVar2 = (uint)(short)local_10;
    if (-1 < (int)uVar2) {
      DAT_00003944[0x60] = 1 << (uVar2 & 0x1f);
      *DAT_00003944 = 1 << (uVar2 & 0x1f);
    }
    touch_application_17f4_run(DAT_0000393c);
  }
  return;
}

