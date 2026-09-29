
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void even_ai_listening_visibility_set(undefined1 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = _DAT_004e69e0;
  iVar2 = *(int *)(_DAT_004e69e0 + 0x10);
  while (iVar2 != 0) {
    iVar3 = *(int *)(iVar2 + 0x20);
    even_ai_dialog_node_apply(iVar2,param_1);
    iVar2 = iVar3;
  }
  *(undefined4 *)(iVar1 + 0x10) = 0;
  *(undefined4 *)(iVar1 + 0x14) = 0;
  *(undefined1 *)(iVar1 + 0x18) = 0;
  *(undefined2 *)(iVar1 + 0x1a) = 0;
  *(undefined2 *)(iVar1 + 0x1c) = 0;
  *(undefined2 *)(iVar1 + 0x1e) = 0;
  return;
}

