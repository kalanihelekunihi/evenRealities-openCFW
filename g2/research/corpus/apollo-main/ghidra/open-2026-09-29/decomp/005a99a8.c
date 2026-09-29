
undefined4
af_latin_metrics_scale(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  *(undefined1 *)(param_1 + 0x18) = *(undefined1 *)(param_2 + 5);
  *(undefined4 *)(param_1 + 4) = *param_2;
  *(undefined4 *)(param_1 + 0x1c) = param_2[6];
  af_latin_metrics_scale_dim(param_1,param_2,0);
  af_latin_metrics_scale_dim(param_1,param_2,1);
  return param_4;
}

