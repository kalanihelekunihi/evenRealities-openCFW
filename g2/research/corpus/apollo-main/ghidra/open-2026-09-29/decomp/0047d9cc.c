
undefined8 FUN_0047d9cc(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = central_is_ring_owner_side_004a2914();
  if (iVar1 == 0) {
    iVar1 = UX_GetPeerRingStatus();
  }
  else {
    iVar1 = UX_GetSelfRingStatus();
  }
  return CONCAT44(unaff_r7,(uint)(iVar1 != 0));
}

