
void tt_apply_mvar(int param_1)

{
  short sVar1;
  short *psVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  
  iVar3 = *(int *)(param_1 + 700);
  if (*(int *)(param_1 + 0x2c0) << 0x17 < 0) {
    puVar4 = *(undefined4 **)(*(int *)(iVar3 + 0x38) + 0x18);
    puVar5 = puVar4 + (uint)**(ushort **)(iVar3 + 0x38) * 3;
    for (; puVar4 < puVar5; puVar4 = puVar4 + 3) {
      psVar2 = (short *)ft_var_get_value_pointer(param_1,*puVar4);
      sVar1 = ft_var_get_item_delta
                        (param_1,*(int *)(iVar3 + 0x38) + 4,*(undefined2 *)(puVar4 + 1),
                         *(undefined2 *)((int)puVar4 + 6));
      if (psVar2 != (short *)0x0) {
        *psVar2 = sVar1 + *(short *)(puVar4 + 2);
      }
    }
    if (*(short *)(param_1 + 0x174) != -1) {
      if ((*(short *)(param_1 + 0x1ba) == 0) && (*(short *)(param_1 + 0x1bc) == 0)) {
        *(undefined2 *)(param_1 + 0x46) = *(undefined2 *)(param_1 + 0x1c0);
        *(short *)(param_1 + 0x48) = -*(short *)(param_1 + 0x1c2);
        *(short *)(param_1 + 0x4a) = *(short *)(param_1 + 0x46) - *(short *)(param_1 + 0x48);
      }
      else {
        *(undefined2 *)(param_1 + 0x46) = *(undefined2 *)(param_1 + 0x1ba);
        *(undefined2 *)(param_1 + 0x48) = *(undefined2 *)(param_1 + 0x1bc);
        *(short *)(param_1 + 0x4a) =
             *(short *)(param_1 + 0x1be) + (*(short *)(param_1 + 0x46) - *(short *)(param_1 + 0x48))
        ;
      }
    }
    *(short *)(param_1 + 0x50) = *(short *)(param_1 + 0x1e4) - *(short *)(param_1 + 0x1e6) / 2;
    *(undefined2 *)(param_1 + 0x52) = *(undefined2 *)(param_1 + 0x1e6);
    FT_List_Iterate(param_1 + 0x6c,DAT_005f2fd8,0);
  }
  return;
}

