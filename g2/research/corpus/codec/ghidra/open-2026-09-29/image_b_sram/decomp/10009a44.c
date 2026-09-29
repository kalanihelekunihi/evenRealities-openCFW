
void FUN_10009a44(int param_1,uint param_2)

{
  uint *puVar1;
  undefined *puVar2;
  undefined2 *puVar3;
  int iVar4;
  uint uVar5;
  undefined2 *puVar6;
  uint uVar7;
  
  puVar2 = PTR_s_mem_init__heap_begin_address_0x__10009ab4;
  puVar1 = DAT_10009ab0;
  if (0x18 < (param_2 & 0xfffffffc)) {
    uVar7 = param_1 + 3U & 0xfffffffc;
    uVar5 = (param_2 & 0xfffffffc) - 0x18;
    if (uVar7 <= uVar5) {
      DAT_10009ab0[3] = uVar5 - uVar7;
      *puVar1 = uVar7;
      FUN_10009934(puVar2,uVar7);
      puVar6 = (undefined2 *)*puVar1;
      *puVar6 = 0x1ea0;
      iVar4 = puVar1[3] + 0xc;
      *(undefined4 *)(puVar6 + 4) = 0;
      puVar6[1] = 0;
      puVar3 = (undefined2 *)((int)puVar6 + iVar4);
      *(int *)(puVar6 + 2) = iVar4;
      *puVar3 = 0x1ea0;
      puVar1[1] = (uint)puVar3;
      puVar3[1] = 1;
      *(int *)(puVar3 + 2) = iVar4;
      *(int *)(puVar3 + 4) = iVar4;
      puVar1[2] = (uint)puVar6;
      return;
    }
  }
  FUN_10009934(PTR_s_mem_init__error_begin_address_0x_10009aac,param_1,param_2);
  return;
}

