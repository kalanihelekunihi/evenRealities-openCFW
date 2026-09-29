
int nonblocking_transfer_call(void)

{
  int iVar1;
  int unaff_r5;
  undefined1 unaff_r6;
  
  iVar1 = mspi_cq_pause();
  if (iVar1 == 0) {
    cmdq_reset_427baa(*(undefined4 *)(unaff_r5 + 0x828));
    *(undefined4 *)(unaff_r5 + 0x1c) = 0;
    *(undefined4 *)(unaff_r5 + 0x830) = 0;
    *(undefined4 *)(unaff_r5 + 0x20) = 0;
    *(undefined1 *)(unaff_r5 + 0x82c) = unaff_r6;
    *(undefined1 *)(unaff_r5 + 0x82d) = 1;
    *(undefined4 *)(unaff_r5 + 0x85c) = 0;
  }
  return iVar1;
}

