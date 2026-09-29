
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 terminal_action_unlock(void)

{
  undefined4 unaff_r7;
  
  if (*_DAT_005e4768 != 0) {
    osMutexRelease(*_DAT_005e4768);
  }
  return unaff_r7;
}

