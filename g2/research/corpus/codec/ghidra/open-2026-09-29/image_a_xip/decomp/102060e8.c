
void gx8002_device_list_init(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = iRam102060f8;
  iVar2 = iRam102060f8 + 8;
  *(int *)iRam102060f8 = iRam102060f8;
  *(int *)(iVar1 + 4) = iVar1;
  *(int *)(iVar1 + 8) = iVar2;
  *(int *)(iVar1 + 0xc) = iVar2;
  return;
}

