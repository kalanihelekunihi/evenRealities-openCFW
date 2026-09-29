
undefined4 hub_role_init(void)

{
  char cVar1;
  undefined4 unaff_r7;
  
  cVar1 = FUN_0045a568();
  if (cVar1 == '\x01') {
    *DAT_004a73b0 = 3;
  }
  else if (cVar1 == '\x02') {
    *DAT_004a73b0 = 2;
  }
  return unaff_r7;
}

