
undefined4 central_is_ring_owner_side_004a2914(void)

{
  char cVar1;
  char cVar2;
  undefined4 uVar3;
  
  cVar1 = FUN_00466518();
  cVar2 = FUN_0045a568();
  if ((cVar1 == '\x01') && (cVar2 == '\x01')) {
    uVar3 = 1;
  }
  else if ((cVar1 == '\0') && (cVar2 == '\x02')) {
    uVar3 = 1;
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}

