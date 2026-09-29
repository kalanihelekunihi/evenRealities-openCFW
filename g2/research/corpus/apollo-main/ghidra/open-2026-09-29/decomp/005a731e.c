
undefined1 af_cjk_align_linked_edge(undefined4 param_1,undefined1 param_2,int param_3,int param_4)

{
  undefined1 uVar1;
  int iVar2;
  
  uVar1 = *(undefined1 *)(param_4 + 0xc);
  iVar2 = af_cjk_compute_stem_width
                    (param_1,param_2,*(int *)(param_4 + 4) - *(int *)(param_3 + 4),
                     *(undefined1 *)(param_3 + 0xc));
  *(int *)(param_4 + 8) = iVar2 + *(int *)(param_3 + 8);
  return uVar1;
}

