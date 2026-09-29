
int af_cjk_hints_apply(undefined4 param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 local_5c;
  undefined4 local_58;
  undefined1 auStack_54 [60];
  
  iVar1 = af_glyph_hints_reload(param_2,param_3);
  if (iVar1 == 0) {
    if (-1 < (int)((uint)*(byte *)(param_2 + 0xab4) << 0x1f)) {
      iVar1 = af_cjk_hints_detect_features(param_2,0);
      if (iVar1 != 0) {
        return iVar1;
      }
      af_cjk_hints_compute_blue_edges(param_2,param_4,0);
      iVar1 = 0;
    }
    if (-1 < (int)((uint)*(byte *)(param_2 + 0xab4) << 0x1e)) {
      iVar1 = af_cjk_hints_detect_features(param_2,1);
      if (iVar1 != 0) {
        return iVar1;
      }
      af_cjk_hints_compute_blue_edges(param_2,param_4,1);
      iVar1 = 0;
    }
    for (uVar2 = 0; (int)uVar2 < 2; uVar2 = uVar2 + 1) {
      if (((uVar2 == 0) && (-1 < (int)((uint)*(byte *)(param_2 + 0xab4) << 0x1f))) ||
         ((uVar2 == 1 && (-1 < (int)((uint)*(byte *)(param_2 + 0xab4) << 0x1e))))) {
        if (((uVar2 == 0) && (*(char *)(param_4 + 0x18) == '\0')) &&
           (-1 < (int)((uint)*(byte *)(param_2 + 0xab4) << 0x1c))) {
          af_warper_compute(auStack_54,param_2,0,&local_58,&local_5c);
          af_glyph_hints_scale_dim(param_2,0,local_58,local_5c);
        }
        else {
          af_cjk_hint_edges(param_2,uVar2 & 0xff);
          af_cjk_align_edge_points(param_2,uVar2 & 0xff);
          af_glyph_hints_align_strong_points(param_2,uVar2 & 0xff);
          af_glyph_hints_align_weak_points(param_2,uVar2 & 0xff);
        }
      }
    }
    af_glyph_hints_save(param_2,param_3);
  }
  return iVar1;
}

