
void FUN_00455876(void)

{
  if (*(int *)*DAT_00456050 == 0) {
    *DAT_00456060 = 0xffffffff;
  }
  else {
    *DAT_00456060 = **(undefined4 **)(*DAT_00456050 + 0xc);
  }
  return;
}

