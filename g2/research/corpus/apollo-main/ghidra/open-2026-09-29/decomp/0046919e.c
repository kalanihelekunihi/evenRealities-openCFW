
undefined8 silent_mode_status_get(void)

{
  int iVar1;
  uint uVar2;
  undefined4 unaff_r7;
  
  iVar1 = settings_get_config();
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = (uint)(*(char *)(iVar1 + 0x15) != '\0');
  }
  return CONCAT44(unaff_r7,uVar2);
}

