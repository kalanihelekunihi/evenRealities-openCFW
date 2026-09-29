
void even_ai_dialogs_refresh(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_004e74fc;
  if (*(int *)(DAT_004e74fc + 0x10) != 0) {
    iVar2 = *(int *)(DAT_004e74fc + 0x10);
    *(undefined4 *)(DAT_004e74fc + 0x10) = *(undefined4 *)(iVar2 + 0x20);
    if (*(int *)(iVar1 + 0x10) == 0) {
      *(undefined4 *)(iVar1 + 0x14) = 0;
    }
    even_ai_dialog_node_apply(iVar2,1);
    *(char *)(iVar1 + 0x18) = *(char *)(iVar1 + 0x18) + -1;
  }
  return;
}

