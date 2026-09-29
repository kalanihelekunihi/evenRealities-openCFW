
void af_cjk_hints_detect_features
               (undefined4 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = af_cjk_hints_compute_segments(param_1,param_2,param_3,param_4,param_4);
  if (iVar1 == 0) {
    af_cjk_hints_link_segments(param_1,param_2);
    af_cjk_hints_compute_edges(param_1,param_2);
  }
  return;
}

