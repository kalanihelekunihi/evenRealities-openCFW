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

#ifndef SIF_CLASSIFIER_IR_
#define SIF_CLASSIFIER_IR_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#define MAX_NODE_SIZE (255) // max number of nodes in the tree
#define MAX_FEATURE_IDS                                                                            \
	(120) // max number of features IDS supported - may need to revise this number later

typedef struct {
	const int16_t decisionTreeThresholds[MAX_NODE_SIZE];
	const uint8_t featureIDs[MAX_NODE_SIZE];
	const uint8_t nextNodeRight[MAX_NODE_SIZE];
	const uint8_t decisionTreeThresholdsShift[MAX_FEATURE_IDS];
} tree_t; ///< \struct tree_t <><> \brief Tree structure including decision tree thresholds, feature index, nextNodeRight for the tree. \ingroup Classifier

/** \brief  initialize classifier tree.
	\param[in, out] tree: pointer to tree_t structure that contains the tree
	\param[in] num_node: number of tree nodes
	\param[in] decisionTreeThresholds: decision tree thresholds. This is an array of size=nb nodes
	\param[in] featureIDs: array of size=nb nodes: feature index to use for each node.
	\param[in] nextNodeRight: array of size=nb nodes.
	\param[in] decisionTreeThresholdsShift: array of size=nb features.
	\ingroup FeatureExtractionFxp
*/
void SIF_Tree_Init(tree_t *tree, int32_t num_node, const int16_t decisionTreeThresholds[],
                   const uint8_t featureIDs[], const uint8_t nextNodeRight[],
                   const uint8_t decisionTreeThresholdsShift[]);

#ifdef __cplusplus
}
#endif

#endif
