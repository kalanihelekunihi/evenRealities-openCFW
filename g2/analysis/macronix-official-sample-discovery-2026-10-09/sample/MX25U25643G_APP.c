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
 * Application program of SPI flash
 * This sample code provides a reference, not recommand for directing using.
 *
 * $Id: MX25U25643G_APP.c,v 1.1.1.1 2019/10/29 05:43:38 mxclldb1 Exp $
 */


#include    <stdlib.h>
#include    "MX25U25643G_CMD.h"

#define  TRANS_LENGTH  16
#define  RANDOM_SEED   106
#define  FLASH_TARGET_ADDR  0x00000000

#define  Error_inc(x)  x = x + 1;

/* function prototype */
uint8  FlashID_Test( uint8 QPI_Enable );
uint8  FlashReadWrite_Test( uint8 QPI_Enable );

/*
 * Main Program
 */
void main()
{
    /* Setting flash access mode: SPI or QPI */
    uint8 QPI_Enable = TRUE;

    Initial_Spi();
    FlashID_Test( QPI_Enable );    // Simple test : flash ID
    FlashReadWrite_Test( QPI_Enable );   // Simple test : flash read / write
}

/*
 * Simple flash id test
 */
uint8 FlashID_Test( uint8 QPI_Enable )
{
    uint32  flash_id = 0;
    uint16  error_cnt = 0;
    FlashStatus  flash_state = {0};
    ReturnMsg  msg;

    if( QPI_Enable )
        CMD_EQIO( &flash_state );    // Enter QPI mode

    /* Read flash ID */
    if( QPI_Enable ){    // Call QPI command
        msg = CMD_QPIID( &flash_id ,&flash_state );
    }
    else{
        msg = CMD_RDID( &flash_id, &flash_state );
    }

    if( msg != (ReturnMsg)FlashOperationSuccess )  // Check returen message
        return FALSE;

    if( QPI_Enable )
        CMD_RSTQIO( &flash_state );  // Exit QPI mode

    if( flash_id != FlashID )  // Compare to expected value
        Error_inc( error_cnt );

    if( error_cnt != 0 )
        return FALSE;
    else
        return TRUE;

}
/*
 * Simple flash read/write test
 */
uint8 FlashReadWrite_Test( uint8 QPI_Enable )
{
    FlashStatus  flash_state = {0};
    uint32  flash_addr;
    uint32  trans_len = 0;
    uint16  i=0, error_cnt = 0;
    uint16  seed = 0;
    uint8   st_reg = 0;
    uint8   memory_addr[TRANS_LENGTH] = {0};
    uint8   memory_addr_cmp[TRANS_LENGTH] = {0};

    /* Assign initial condition */
    flash_addr = FLASH_TARGET_ADDR;
    trans_len = TRANS_LENGTH;
    seed = RANDOM_SEED;

    if( QPI_Enable )
        CMD_EQIO( &flash_state );    // Enter QPI mode

    /* Prepare data to transfer */
    srand( seed );
    for( i=0; i< (trans_len); i=i+1 ){
        memory_addr[i] = rand()%256;    // generate random byte data
    }

    
    /* Mmarked these code when not using quad IO mode (except QPI mode)
     * Enable Quad IO mode
     * Read status register value */
    CMD_RDSR( &st_reg, &flash_state );
    st_reg = st_reg | FLASH_QE_MASK;    // set QE bit to 1
    CMD_WRSR( st_reg, &flash_state );    // write setting to flash
    HAL_Delay_Us(TW/1000);

    /* Check QE value */
    CMD_RDSR( &st_reg, &flash_state );    
    if( (st_reg & FLASH_QE_MASK) != FLASH_QE_MASK )
        Error_inc( error_cnt );
    

    /* Erase 4K sector of flash memory
       Note: It needs to erase dirty sector before program */
    CMD_SE( flash_addr, &flash_state );
    HAL_Delay_Us(TSE/1000);

    /* Program data to flash */
    if( QPI_Enable == 1){
        CMD_PP( flash_addr, memory_addr, trans_len, &flash_state );
        HAL_Delay_Us(TPP/1000);}

    else{
        //CMD_PP( flash_addr, memory_addr, trans_len, &flash_state );
        CMD_4PP( flash_addr, memory_addr, trans_len, &flash_state ); 
        HAL_Delay_Us(TPP/1000);
   // need set QE bit
    }

    /* Read flash data to memory buffer */
    if ( QPI_Enable == 1){    
        CMD_4READ( flash_addr, memory_addr_cmp, trans_len, &flash_state );
    }else{
        //Non-QPI mode have different read instruction options:
        CMD_READ( flash_addr, memory_addr_cmp, trans_len, &flash_state );
        //CMD_FASTREAD( flash_addr, memory_addr_cmp, trans_len, &flash_state );
        //CMD_2READ( flash_addr, memory_addr_cmp, trans_len, &flash_state );
        //CMD_4READ( flash_addr, memory_addr_cmp, trans_len, &flash_state );    // need set QE bit
    }

    /* Compare flash data and patten data */
    for( i=0; i < trans_len; i=i+1 ){
        if( memory_addr[i] != memory_addr_cmp[i] )
            Error_inc( error_cnt );
    }

    /* Erase 4K sector of flash memory */
    CMD_SE( flash_addr, &flash_state );
    HAL_Delay_Us(TSE/1000);

    if( QPI_Enable )
        CMD_RSTQIO( &flash_state );    // Exit QPI mode

    if( error_cnt != 0 )
        return FALSE;
    else
        return TRUE;

}



