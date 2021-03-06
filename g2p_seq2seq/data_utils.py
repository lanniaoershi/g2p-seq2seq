# Copyright 2016 AC Technology LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Utilities for tokenizing, creation vocabularies."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#import gzip
import os
#import re
#import tarfile
import codecs

#from six.moves import urllib

#from tensorflow.python.platform import gfile

# Special vocabulary symbols - we always put them at the start.
_PAD = "_PAD"
_GO = "_GO"
_EOS = "_EOS"
_UNK = "_UNK"
_START_VOCAB = [_PAD, _GO, _EOS, _UNK]

PAD_ID = 0
GO_ID = 1
EOS_ID = 2
UNK_ID = 3


def create_vocabulary(data):
  """Create vocabulary from input data.
  Input data is assumed to contain one word per line.

  Args:
    data: word list that will be used to create vocabulary.

  Rerurn:
    vocab: vocabulary dictionary. In this dictionary keys are symbols
           and values are their indexes.
  """
  vocab = {}
  for line in data:
    for item in line:
      if item in vocab:
        vocab[item] += 1
      else:
        vocab[item] = 1
  vocab_list = _START_VOCAB + sorted(vocab)
  vocab = dict([(x, y) for (y, x) in enumerate(vocab_list)])
  return vocab


def save_vocabulary(vocab, vocabulary_path):
  """Save vocabulary file in vocabulary_path.
  We write vocabulary to vocabulary_path in a one-token-per-line format,
  so that later token in the first line gets id=0, second line gets id=1,
  and so on.

  Args:
    vocab: vocabulary dictionary.
    vocabulary_path: path where the vocabulary will be created.

  """
  print("Creating vocabulary %s" % (vocabulary_path))
  with codecs.open(vocabulary_path, "w", "utf-8") as vocab_file:
    for symbol in sorted(vocab, key=vocab.get):
      vocab_file.write(symbol + '\n')


def load_vocabulary(vocabulary_path, reverse=False):
  """Load vocabulary from file.
  We assume the vocabulary is stored one-item-per-line, so a file:
    d
    c
  will result in a vocabulary {"d": 0, "c": 1}, and this function may
  also return the reversed-vocabulary [0, 1].

  Args:
    vocabulary_path: path to the file containing the vocabulary.
    reverse: flag managing what type of vocabulary to return.

  Returns:
    the vocabulary (a dictionary mapping string to integers), or
    if set reverse to True the reversed vocabulary (a list, which reverses
    the vocabulary mapping).

  Raises:
    ValueError: if the provided vocabulary_path does not exist.
  """
  rev_vocab = []
  with codecs.open(vocabulary_path, "r", "utf-8") as vocab_file:
    rev_vocab.extend(vocab_file.readlines())
  rev_vocab = [line.strip() for line in rev_vocab]
  if reverse:
    return rev_vocab
  else:
    return dict([(x, y) for (y, x) in enumerate(rev_vocab)])


def symbols_to_ids(symbols, vocab):
  """Turn symbols into ids sequence using given vocabulary file.

  Args:
    symbols: input symbols sequence.
    vocab: vocabulary.

  Returns:
    ids: output sequence of ids.
  """
  ids = [vocab.get(s, UNK_ID) for s in symbols]
  return ids


def split_to_grapheme_phoneme(inp_dictionary):
  """Split input dictionary into two separate lists with graphemes and phonemes.

  Args:
    inp_dictionary: input dictionary.
  """
  graphemes, phonemes = [], []
  for line in inp_dictionary:
    split_line = line.strip().split()
    if len(split_line) > 1:
      graphemes.append(list(split_line[0]))
      phonemes.append(split_line[1:])
  return graphemes, phonemes


def prepare_g2p_data(model_dir, train_gr, train_ph, valid_gr, valid_ph):
  """Create vocabularies into model_dir, create ids data lists.

  Args:
    model_dir: directory in which the data sets will be stored.

  Returns:
    A tuple of 6 elements:
      (1) Token-ids for Grapheme training data-set,
      (2) Token-ids for Phoneme training data-set,
      (3) Token-ids for Grapheme development data-set,
      (4) Token-ids for Phoneme development data-set,
      (5) Grapheme vocabulary,
      (6) Phoneme vocabulary.
  """
  # Create vocabularies of the appropriate sizes.
  ph_vocab_path = os.path.join(model_dir, "vocab.phoneme")
  gr_vocab_path = os.path.join(model_dir, "vocab.grapheme")
  print("Creating vocabularies in %s" %model_dir)
  ph_vocab = create_vocabulary(train_ph)
  gr_vocab = create_vocabulary(train_gr)
  save_vocabulary(ph_vocab, ph_vocab_path)
  save_vocabulary(gr_vocab, gr_vocab_path)

  # Create ids for the training data.
  train_ph_ids = []
  for line in train_ph:
    train_ph_ids.append(symbols_to_ids(line, ph_vocab))

  train_gr_ids = []
  for line in train_gr:
    train_gr_ids.append(symbols_to_ids(line, gr_vocab))

  # Create ids for the development data.
  valid_ph_ids = []
  for line in valid_ph:
    valid_ph_ids.append(symbols_to_ids(line, ph_vocab))

  valid_gr_ids = []
  for line in valid_gr:
    valid_gr_ids.append(symbols_to_ids(line, gr_vocab))

  return (train_gr_ids, train_ph_ids,
          valid_gr_ids, valid_ph_ids,
          gr_vocab, ph_vocab)
