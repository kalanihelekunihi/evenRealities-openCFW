
undefined4 settings_apply_display_levels(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  
  iVar1 = DAT_0046bee8;
  uVar2 = system_get_brightness_level(*(undefined1 *)(DAT_0046bee8 + 8));
  uVar3 = settings_role_head_up_profile(*(undefined1 *)(iVar1 + 9));
  func_0x0046c9d0(uVar2,uVar3);
  return in_r3;
}

