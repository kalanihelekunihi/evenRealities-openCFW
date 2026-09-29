
void even_ai_dialog_index_set(int param_1)

{
  int iVar1;
  
  if (param_1 != 0) {
    *(undefined4 *)(param_1 + 0x20) = 0;
    iVar1 = DAT_004e74fc;
    if (*(int *)(DAT_004e74fc + 0x10) == 0) {
      *(int *)(DAT_004e74fc + 0x10) = param_1;
      *(int *)(iVar1 + 0x14) = param_1;
    }
    else {
      *(int *)(*(int *)(DAT_004e74fc + 0x14) + 0x20) = param_1;
      *(int *)(iVar1 + 0x14) = param_1;
    }
  }
  return;
}

