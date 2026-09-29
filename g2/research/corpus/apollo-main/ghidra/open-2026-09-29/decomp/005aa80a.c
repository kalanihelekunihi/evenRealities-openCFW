
ulonglong af_latin_align_linked_edge(undefined4 param_1,undefined1 param_2,int param_3,int param_4)

{
  undefined1 uVar1;
  byte bVar2;
  int iVar3;
  
  uVar1 = *(undefined1 *)(param_4 + 0xc);
  bVar2 = *(byte *)(param_3 + 0xc);
  iVar3 = af_latin_compute_stem_width
                    (param_1,param_2,*(int *)(param_4 + 4) - *(int *)(param_3 + 4),
                     *(int *)(param_3 + 8) - *(int *)(param_3 + 4));
  *(int *)(param_4 + 8) = iVar3 + *(int *)(param_3 + 8);
  return (ulonglong)CONCAT14(uVar1,(uint)bVar2);
}

