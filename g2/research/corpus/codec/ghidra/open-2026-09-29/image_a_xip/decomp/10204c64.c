
undefined4 gx8002_aout_config_i2s(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == (undefined4 *)0x0) {
    uVar1 = 0xffffffff;
  }
  else {
    iVar2 = *(int *)(param_1 + 0x30);
    *(undefined4 *)(iVar2 + 0x14) = param_2[1];
    *(undefined4 *)(iVar2 + 0x18) = param_2[2];
    *(undefined4 *)(iVar2 + 0x20) = *param_2;
    aout_i2s_config(0,iVar2 + 8);
    gx8002_aout_set_lodac();
    uVar1 = 0;
  }
  return uVar1;
}

