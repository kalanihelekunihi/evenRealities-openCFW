
undefined4 gx8002_aout_config_dac(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == (undefined4 *)0x0) {
    uVar1 = 0xffffffff;
  }
  else {
    iVar2 = *(int *)(param_1 + 0x30);
    *(undefined4 *)(iVar2 + 0x30) = *param_2;
    *(undefined2 *)(iVar2 + 0x34) = *(undefined2 *)(param_2 + 1);
    *(undefined2 *)(iVar2 + 0x36) = *(undefined2 *)((int)param_2 + 6);
    *(undefined2 *)(iVar2 + 0x38) = *(undefined2 *)(param_2 + 2);
    *(undefined4 *)(iVar2 + 0x3c) = param_2[3];
    *(undefined2 *)(iVar2 + 0x40) = *(undefined2 *)(param_2 + 4);
    *(undefined2 *)(iVar2 + 0x42) = *(undefined2 *)((int)param_2 + 0x12);
    *(undefined2 *)(iVar2 + 0x44) = *(undefined2 *)(param_2 + 5);
    aout_dac_config(0,iVar2 + 0x30);
    uVar1 = 0;
  }
  return uVar1;
}

