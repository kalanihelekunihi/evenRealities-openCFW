// SPDX-License-Identifier: MIT
/*
 * FreeRTOS+CLI V1.0.4 (Amazon/Real Time Engineers, MIT) as linked in G2 2.2.6.10.
 *
 * Stock: FreeRTOS_CLIRegisterCommand 0x5847AC, FreeRTOS_CLIProcessCommand
 * 0x5847FE, FreeRTOS_CLIGetParameter 0x5848FC (names below are the openCFW
 * address-suffixed symbols used by first-party callers). Verified against headless-decomp
 * 12.1.4 decompilation and disassembly (g2c campaign): 8-byte list items from
 * pvPortMalloc, critical section around the list append, both stock strings at
 * 0x6E3568/0x6ED568, and the only G2 delta, the blank-input suppression patch
 * g2/config-recovered/freertos-plus-cli/g2-patches/0001-*.patch.
 * Stock RAM: xRegisteredCommands 0x20000BE8, pxLastCommandInList 0x20000BF0,
 * pxCommand (static in ProcessCommand) 0x200745E4.
 * The submodule third-party/upstream/freertos-plus-cli is not populated in this
 * checkout, so the upstream body is carried here.
 */
#include <stddef.h>
#include <stdint.h>

typedef long BaseType_t;
typedef int (*pdCOMMAND_LINE_CALLBACK)(char *pcWriteBuffer, size_t xWriteBufferLen, const char *pcCommandString);

typedef struct xCOMMAND_LINE_INPUT {
    const char *const pcCommand;
    const char *const pcHelpString;
    const pdCOMMAND_LINE_CALLBACK pxCommandInterpreter;
    int8_t cExpectedNumberOfParameters;
} CLI_Command_Definition_t;

typedef struct xCOMMAND_INPUT_LIST {
    const CLI_Command_Definition_t *pxCommandLineDefinition;
    struct xCOMMAND_INPUT_LIST *pxNext;
} CLI_Definition_List_Item_t;

extern void *pvPortMalloc(size_t);
extern void vPortEnterCritical(void);
extern void vPortExitCritical(void);
extern size_t strlen(const char *);
extern int strncmp(const char *, const char *, size_t);
extern char *strncpy(char *, const char *, size_t);

#define pdFALSE 0
#define pdTRUE  1
#define configASSERT(x) do { if (!(x)) { for (;;) { } } } while (0)

static int prvHelpCommand(char *pcWriteBuffer, size_t xWriteBufferLen, const char *pcCommandString);
static int8_t prvGetNumberOfParameters(const char *pcCommandString);

static const CLI_Command_Definition_t xHelpCommand = {
    "help",
    "\r\nhelp:\r\n Lists all the registered commands\r\n\r\n",
    prvHelpCommand,
    0
};

static CLI_Definition_List_Item_t xRegisteredCommands = { &xHelpCommand, NULL };
static CLI_Definition_List_Item_t *pxLastCommandInList = &xRegisteredCommands;

BaseType_t freertos_cli_register_command_5847ac(const CLI_Command_Definition_t *const pxCommandToRegister)
{
    CLI_Definition_List_Item_t *pxNewListItem;
    BaseType_t xReturn = pdFALSE;

    configASSERT(pxCommandToRegister);
    pxNewListItem = (CLI_Definition_List_Item_t *)pvPortMalloc(sizeof(CLI_Definition_List_Item_t));
    configASSERT(pxNewListItem);
    if (pxNewListItem != NULL) {
        vPortEnterCritical();
        pxNewListItem->pxCommandLineDefinition = pxCommandToRegister;
        pxNewListItem->pxNext = NULL;
        pxLastCommandInList->pxNext = pxNewListItem;
        pxLastCommandInList = pxNewListItem;
        vPortExitCritical();
        xReturn = pdTRUE;
    }
    return xReturn;
}

BaseType_t freertos_cli_process_command_5847fe(const char *const pcCommandInput, char *pcWriteBuffer, size_t xWriteBufferLen)
{
    static const CLI_Definition_List_Item_t *pxCommand = NULL;
    BaseType_t xReturn = pdTRUE;
    const char *pcRegisteredCommandString;
    size_t xCommandStringLength;

    if (pxCommand == NULL) {
        for (pxCommand = &xRegisteredCommands; pxCommand != NULL; pxCommand = pxCommand->pxNext) {
            pcRegisteredCommandString = pxCommand->pxCommandLineDefinition->pcCommand;
            xCommandStringLength = strlen(pcRegisteredCommandString);
            if ((pcCommandInput[xCommandStringLength] == ' ') || (pcCommandInput[xCommandStringLength] == 0x00)) {
                if (strncmp(pcCommandInput, pcRegisteredCommandString, xCommandStringLength) == 0) {
                    if (pxCommand->pxCommandLineDefinition->cExpectedNumberOfParameters >= 0) {
                        if (prvGetNumberOfParameters(pcCommandInput) != pxCommand->pxCommandLineDefinition->cExpectedNumberOfParameters)
                            xReturn = pdFALSE;
                    }
                    break;
                }
            }
        }
    }

    if ((pxCommand != NULL) && (xReturn == pdFALSE)) {
        strncpy(pcWriteBuffer, "Incorrect command parameter(s).  Enter \"help\" to view a list of available commands.\r\n\r\n", xWriteBufferLen);
        pxCommand = NULL;
    } else if (pxCommand != NULL) {
        xReturn = pxCommand->pxCommandLineDefinition->pxCommandInterpreter(pcWriteBuffer, xWriteBufferLen, pcCommandInput);
        if (xReturn == pdFALSE)
            pxCommand = NULL;
    } else {
        /* G2 delta: blank input ("\r" or "") prints nothing. */
        if (!((strlen(pcCommandInput) == 1) && (pcCommandInput[0] == '\r')) &&
            !((strlen(pcCommandInput) == 0) && (pcCommandInput[0] == '\0')))
            strncpy(pcWriteBuffer, "Command not recognised.  Enter 'help' to view a list of available commands.\r\n\r\n", xWriteBufferLen);
        xReturn = pdFALSE;
    }
    return xReturn;
}

const char *freertos_cli_get_parameter_5848fc(const char *pcCommandString, BaseType_t uxWantedParameter, BaseType_t *pxParameterStringLength)
{
    BaseType_t uxParametersFound = 0;
    const char *pcReturn = NULL;

    *pxParameterStringLength = 0;
    while (uxParametersFound < uxWantedParameter) {
        while (((*pcCommandString) != 0x00) && ((*pcCommandString) != ' '))
            pcCommandString++;
        while (((*pcCommandString) != 0x00) && ((*pcCommandString) == ' '))
            pcCommandString++;
        if (*pcCommandString != 0x00) {
            uxParametersFound++;
            if (uxParametersFound == uxWantedParameter) {
                pcReturn = pcCommandString;
                while (((*pcCommandString) != 0x00) && ((*pcCommandString) != ' ')) {
                    (*pxParameterStringLength)++;
                    pcCommandString++;
                }
                if (*pxParameterStringLength == 0)
                    pcReturn = NULL;
                break;
            }
        } else {
            break;
        }
    }
    return pcReturn;
}

static int prvHelpCommand(char *pcWriteBuffer, size_t xWriteBufferLen, const char *pcCommandString)
{
    static const CLI_Definition_List_Item_t *pxCommand = NULL;
    (void)pcCommandString;
    if (pxCommand == NULL)
        pxCommand = &xRegisteredCommands;
    strncpy(pcWriteBuffer, pxCommand->pxCommandLineDefinition->pcHelpString, xWriteBufferLen);
    pxCommand = pxCommand->pxNext;
    return pxCommand == NULL ? pdFALSE : pdTRUE;
}

static int8_t prvGetNumberOfParameters(const char *pcCommandString)
{
    int8_t cParameters = 0;
    BaseType_t xLastCharacterWasSpace = pdFALSE;
    while (*pcCommandString != 0x00) {
        if ((*pcCommandString) == ' ') {
            if (xLastCharacterWasSpace != pdTRUE) {
                cParameters++;
                xLastCharacterWasSpace = pdTRUE;
            }
        } else {
            xLastCharacterWasSpace = pdFALSE;
        }
        pcCommandString++;
    }
    if (xLastCharacterWasSpace == pdTRUE)
        cParameters--;
    return cParameters;
}
