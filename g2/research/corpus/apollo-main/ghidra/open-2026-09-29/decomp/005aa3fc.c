
void af_latin_hints_detect_features
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  
  iVar1 = af_latin_hints_compute_segments(param_1,param_4 & 0xff,param_3,param_4,param_4);
  if (iVar1 == 0) {
    af_latin_hints_link_segments(param_1,param_2,param_3,param_4 & 0xff);
    af_latin_hints_compute_edges(param_1,param_4 & 0xff);
  }
  return;
}

