/*
 * Security Level: Macronix Proprietary
 * COPYRIGHT (c) 2010-2024 MACRONIX INTERNATIONAL CO., LTD
 * SPI Flash Low Level Driver (LLD) Sample Code
 *
 * FOR UNRESTRICTED INTERNAL USE ONLY
 * UNAUTHORIZED REPRODUCTION AND/OR DISTRIBUTION IS STRICTLY PROHIBITED.
 * ------------------------------------------------------------------------
 * This software code and all associated documentation, comments or other 
 * information (collectively "Software") is provided "AS IS" without
 * warranty of any kind. MACRONIX INTERNATIONAL Co., LTD ("MXIC") does  
 * not warrant the functions contained in the program will meet your
 * requirements or that the operation of the program will be uninterrupted
 * or error-free. IN NO EVENT, UNLESS REQUIRED BY APPLICABLE LAW OR AGREED
 * TO IN WRITING, MXIC OR ANY PERSON BE LIABLE FOR ANY LOSS, EXPENSE OR
 * DAMAGE, OF ANY TYPE OR NATURE ARISING OUT OF THE USE OF, OR INABILITY
 * TO USE THIS SOFTWARE OR PROGRAM, INCLUDING, BUT NOT LIMITED TO, CLAIMS,
 * SUITS OR CAUSES OF ACTION INVOLVING ALLEGED INFRINGEMENT OF COPYRIGHTS,
 * PATENTS, TRADEMARKS, TRADE SECRETS, OR UNFAIR COMPETITION.
 *
 * Flash device information define
 *
 * $Id: MX25U25643G_DEF.h,v 1.702 2019/07/12 08:54:16 mxclldb1 Exp $
 */

// Low Level Driver For MX25U25643GXXX

#ifndef    __MX25U25643G_DEF_H__
#define    __MX25U25643G_DEF_H__
/*
  Compiler Option
*/

#define    COCOTB  1

#include <stdio.h>
#include <Python.h>

/* Note:
   Synchronous IO     : MCU will polling WIP bit after
                        sending prgram/erase command
   Non-synchronous IO : MCU can do other operation after
                        sending prgram/erase command
   Default is synchronous IO
*/
//#define    NON_SYNCHRONOUS_IO

/*
  Type and Constant Define
*/

// define type
typedef    unsigned long     uint32;
typedef    unsigned int      uint16;
typedef    unsigned char     uint8;
typedef    unsigned char     BOOL;

// variable
#define    TRUE              1
#define    FALSE             0
#define    BYTE_LEN          8
#define    IO_MASK           0x80
#define    HALF_WORD_MASK    0x0000ffff

/*
  Flash Related Parameter Define
*/

#define    Block_Offset       0x10000     // 64K Block size
#define    Block32K_Offset    0x8000      // 32K Block size
#define    Sector_Offset      0x1000      // 4K Sector size
#define    Page_Offset        0x0100      // 256 Byte Page size
#define    Page32_Offset      0x0020      // 32 Byte Page size (some products have smaller page size)
#define    Block_Num          (FlashSize / Block_Offset)

#ifdef COCOTB
#define    CLK_PERIOD                20 // unit: ns
#define    Min_Cycle_Per_Inst         1 // cycle count of one instruction
#define    One_Loop_Inst             15 // instruction count of one loop (estimate)
#define    Test_Module               "module_spinor"
#else
//--- insert your MCU information ---//
#define    CLK_PERIOD                // unit: ns
#define    Min_Cycle_Per_Inst        // cycle count of one instruction
#define    One_Loop_Inst             // instruction count of one loop (estimate)

#endif  //end 

/*  
   Flash Information
   (The following information could get from device specification) 
*/
//Flash information
#define    FlashID                       0xC22539
#define    ElectronicID                  0x39
#define    RESID0                        0xC239
#define    RESID1                        0x39C2
#define    FlashSize                     0x2000000
#define    CE_period                     866666666
#define    TW                            40000000
#define    TDP                           10000
#define    TBP                           40000
#define    TPP                           3000000
#define    TSE                           400000000
#define    TBE32                         1000000000
#define    TBE                           2000000000
#define    TVSL                          3000000
#define    TWREAW                        40
#define    TWSR                          TBP
//Support I/O mode
#define    SIO                           0
#define    DIO                           1
#define    QIO                           2
#define    DTQIO                         6
//Register bit mask
#define    FLASH_QE_MASK                 0x40
#define    FLASH_WIP_MASK                0x01
#define    FLASH_DC_2BIT_MASK            0xc0
#define    FLASH_4BYTE_CF_MASK           0x20
#define    FLASH_WPSEL_MASK              0x80
#define    FLASH_4BYTE_MASK              0x40
#define    FLASH_OTPLOCK_MASK            0x03
#define    FLASH_LDSO_MASK               0x02
#define    BLOCK_PROTECT_MASK            0xff
#define    BLOCK_LOCK_MASK               0x01
//dummy cycle
#define    DUMMY_CONF_FASTREAD           0x08080808
#define    DUMMY_CONF_FASTREAD_QPI       0x04040404
#define    DUMMY_CONF_DREAD              0x08080808
#define    DUMMY_CONF_QREAD              0x08080808
#define    DUMMY_CONF_2READ              0x08040804
#define    DUMMY_CONF_4READ              0x0a080406
#define    DUMMY_CONF_4DTRD              0x0a080606
//spi only
#define    WPSEL_SPI_ONLY                1
#define    GBLK_SPI_ONLY                 1
//command property
#define    SUPPORT_WRSR_CR               1
#define    SUPPORT_CR_DC_2bit            1
#define    RDSFDP_QPI_DMY_8              1
#define    FASTREAD_QPI_DUMMY_FLEXIBLE   1
#define DEFAULT_SPI                    1             
// Flash information define
#define    WriteStatusRegCycleTime     TW / (CLK_PERIOD * Min_Cycle_Per_Inst * One_Loop_Inst)
#define    PageProgramCycleTime        TPP / (CLK_PERIOD * Min_Cycle_Per_Inst * One_Loop_Inst)
#define    SectorEraseCycleTime        TSE / (CLK_PERIOD * Min_Cycle_Per_Inst * One_Loop_Inst)
#define    BlockEraseCycleTime         TBE / (CLK_PERIOD * Min_Cycle_Per_Inst * One_Loop_Inst)
#define    ChipEraseCycleTime          CE_period
#define    FlashFullAccessTime         TVSL / (CLK_PERIOD * Min_Cycle_Per_Inst * One_Loop_Inst)

#ifdef TBP
#define    ByteProgramCycleTime        TBP / (CLK_PERIOD * Min_Cycle_Per_Inst * One_Loop_Inst)
#endif
#ifdef TWSR
#define    WriteSecuRegCycleTime       TWSR / (CLK_PERIOD * Min_Cycle_Per_Inst * One_Loop_Inst)
#endif
#ifdef TBE32
#define    BlockErase32KCycleTime      TBE32 / (CLK_PERIOD * Min_Cycle_Per_Inst * One_Loop_Inst)
#endif
#ifdef TWREAW
#define    WriteExtRegCycleTime        TWREAW / (CLK_PERIOD * Min_Cycle_Per_Inst * One_Loop_Inst)
#endif
#endif    /* end of __MX25U25643G_DEF_H__  */

