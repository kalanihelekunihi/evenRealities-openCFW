/*
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
 * $Id: SPI_BITBANG.h,v 1.702 2019/07/12 08:54:16 mxclldb1 Exp $
 */
#ifndef    __BITBANG_H__
#define    __BITBANG_H__

#include    "MX25U25643G_DEF.h"

//--- define your platform information ---//
#define MCU_Platform  1

/* Basic functions */
void CS_High();
void CS_Low();
void InsertDummyCycle( uint8 dummy_cycle );
void SendByte( uint8 byte_value, uint8 transfer_type );
uint8 GetByte( uint8 transfer_type );
void Initial_Spi();
void HAL_Delay_Us( uint32 delay_us );
void SendHalfWord( uint16 half_word_value );
uint16 GetHalfWord( );


/*
  Compiler Option
*/


//--- insert your MCU information ---//
#define    CLK_PERIOD                // unit: ns
#define    Min_Cycle_Per_Inst        // cycle count of one instruction
#define    One_Loop_Inst             // instruction count of one loop (estimate)

#endif
