
void conversate_tag_compute_animation_rect(int param_1)

{
  int iVar1;
  
  iVar1 = FUN_005b0b58();
  if (*(int *)(param_1 + 0x84) != -1) {
    *(int *)(param_1 + 0x84) = *(int *)(param_1 + 0x84) + 1;
  }
  if ((iVar1 < 0) || (*(int *)(param_1 + 0x80) == 0)) {
    if (*(int *)(param_1 + 0x80) != 0) {
      FUN_0044ea2e(*(undefined4 *)(param_1 + 0x80),0);
    }
  }
  else {
    FUN_0044ea04(*(undefined4 *)(param_1 + 100),(*(int *)(param_1 + 0x84) - iVar1) * 0x28,0);
  }
  return;
}

