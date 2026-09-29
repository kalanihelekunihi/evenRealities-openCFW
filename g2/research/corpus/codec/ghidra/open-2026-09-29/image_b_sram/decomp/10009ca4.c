
uint FUN_10009ca4(uint param_1,int param_2)

{
  uint *puVar1;
  undefined2 *puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  
  puVar1 = DAT_10009d74;
  uVar6 = param_2 + 3U & 0xfffffffc;
  uVar9 = DAT_10009d74[3];
  if (uVar9 < uVar6) {
    FUN_10009934(PTR_s_realloc__out_of_memory_10009d78);
    uVar3 = 0;
  }
  else if (uVar6 == 0) {
    FUN_10009c2c();
    uVar3 = 0;
  }
  else if (param_1 == 0) {
    uVar3 = FUN_10009ab8(uVar6);
  }
  else {
    uVar4 = *DAT_10009d74;
    uVar3 = param_1;
    if ((uVar4 <= param_1) && (param_1 < DAT_10009d74[1])) {
      iVar10 = (param_1 - 0xc) - uVar4;
      iVar11 = *(int *)(param_1 - 8);
      uVar8 = (iVar11 + -0xc) - iVar10;
      if (uVar6 != uVar8) {
        uVar5 = uVar6 + 0x18;
        if (uVar5 < uVar8) {
          uVar5 = DAT_10009d74[4];
          iVar7 = uVar6 + iVar10 + 0xc;
          puVar2 = (undefined2 *)(uVar4 + iVar7);
          *puVar2 = 0x1ea0;
          puVar2[1] = 0;
          *(int *)(puVar2 + 2) = iVar11;
          *(int *)(puVar2 + 4) = iVar10;
          *(int *)(param_1 - 8) = iVar7;
          iVar10 = *(int *)(puVar2 + 2);
          puVar1[4] = (uVar5 + uVar6) - uVar8;
          if (iVar10 != uVar9 + 0xc) {
            *(int *)(uVar4 + iVar10 + 8) = iVar7;
          }
          if (puVar2 < (undefined2 *)puVar1[2]) {
            puVar1[2] = (uint)puVar2;
          }
          FUN_100099d4();
        }
        else {
          uVar3 = FUN_10009ab8(uVar6);
          if (uVar3 != 0) {
            FUN_10011344(uVar3,param_1,(uVar6 < uVar8) * uVar5 + (uVar6 >= uVar8) * uVar8);
            FUN_10009c2c(param_1);
          }
        }
      }
    }
  }
  return uVar3;
}

