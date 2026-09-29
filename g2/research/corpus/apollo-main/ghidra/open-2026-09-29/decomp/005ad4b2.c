
undefined8 cff_parse_blend(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = *(int *)(param_1 + 0x20);
  if ((iVar3 == 0) || (*(int *)(iVar3 + 0x16c) == 0)) {
    iVar3 = 3;
  }
  else {
    iVar4 = *(int *)(iVar3 + 0x16c);
    iVar1 = cff_blend_check_vector
                      (iVar4 + 0x22c,*(undefined4 *)(iVar3 + 0x168),*(undefined4 *)(iVar4 + 0x248),
                       *(undefined4 *)(iVar4 + 0x24c));
    if ((iVar1 == 0) ||
       (iVar3 = cff_blend_build_vector
                          (iVar4 + 0x22c,*(undefined4 *)(iVar3 + 0x168),
                           *(undefined4 *)(iVar4 + 0x248),*(undefined4 *)(iVar4 + 0x24c)),
       iVar3 == 0)) {
      uVar2 = cff_parse_num(param_1,*(int *)(param_1 + 0x14) + -4);
      if (*(uint *)(param_1 + 0x18) < uVar2) {
        iVar3 = 3;
      }
      else {
        iVar3 = cff_blend_doBlend(iVar4,param_1);
        *(undefined1 *)(iVar4 + 0x22d) = 1;
      }
    }
  }
  return CONCAT44(param_4,iVar3);
}

