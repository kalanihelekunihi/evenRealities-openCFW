
undefined4 gx8002_mic_buffer(int param_1,uint param_2,uint param_3,int *param_4,uint *param_5)

{
  undefined *puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = PTR_s_ERR__invalid_param_for_gx_audio__10208efc;
  if ((((param_1 != 0) && (param_4 != (int *)0x0)) && (param_5 != (uint *)0x0)) &&
     (param_2 < *(uint *)(param_1 + 8))) {
    uVar2 = (uint)(*(int *)(param_1 + 0x20) *
                  *(int *)(param_1 + 0x1c) * *(int *)(param_1 + 0x24) * 2) / 1000;
    uVar3 = *(uint *)(param_1 + 0x54) / *(uint *)(param_1 + 8);
    uVar4 = uVar3 / uVar2;
    puVar1 = PTR_s_ERR__buf_len_per_ctx_too_large_f_10208f00;
    if (uVar4 != 0) {
      *param_4 = uVar3 * param_2 + (param_3 - (param_3 / uVar4) * uVar4) * uVar2 +
                 *(int *)(param_1 + 0x50);
      *param_5 = uVar2;
      return 0;
    }
  }
  gx8002_printf(puVar1);
  return 0xffffffff;
}

