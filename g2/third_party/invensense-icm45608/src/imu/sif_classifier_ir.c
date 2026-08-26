/*
 *
 * Copyright (c) [2020] by InvenSense, Inc.
 * 
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
 * SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
 * OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
 * CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 */

#include "sif_classifier_ir.h"
#include <string.h>

void SIF_Tree_Init(tree_t *tree, int32_t num_node, const int16_t decisionTreeThresholds[],
                   const uint8_t featureIDs[], const uint8_t nextNodeRight[],
                   const uint8_t decisionTreeThresholdsShift[])
{
	int32_t number_features = 0;

	memset((void *)tree->decisionTreeThresholds, 0, MAX_NODE_SIZE * sizeof(int16_t));
	memset((void *)tree->featureIDs, 0, MAX_NODE_SIZE * sizeof(uint8_t));
	memset((void *)tree->nextNodeRight, 0, MAX_NODE_SIZE * sizeof(uint8_t));
	memset((void *)tree->decisionTreeThresholdsShift, 0, MAX_FEATURE_IDS * sizeof(uint8_t));

	memcpy((void *)tree->decisionTreeThresholds, decisionTreeThresholds,
	       num_node * sizeof(int16_t));
	memcpy((void *)tree->featureIDs, featureIDs, num_node * sizeof(uint8_t));
	memcpy((void *)tree->nextNodeRight, nextNodeRight, num_node * sizeof(uint8_t));

	for (uint8_t node = 0; node < MAX_NODE_SIZE; node++) {
		if (tree->featureIDs[node] > number_features) {
			number_features = tree->featureIDs[node];
		}
	}

	number_features++;

	memcpy((void *)tree->decisionTreeThresholdsShift, decisionTreeThresholdsShift,
	       number_features * sizeof(uint8_t));
}
