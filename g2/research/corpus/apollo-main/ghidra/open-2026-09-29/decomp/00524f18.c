
undefined8 ft_hash_str_lookup(void)

{
  int *piVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  piVar1 = (int *)hash_lookup();
  if (*piVar1 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar1 + 4;
  }
  return CONCAT44(unaff_r7,iVar2);
}

