"""
A pure TensorFlow implementation of a neural network. This can be
used as a drop-in replacement for a Keras model.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools

import tensorflow as tf

from cleverhans import initializers
from cleverhans.model import Model
from cleverhans.picklable_model import MLP, Conv2D, ReLU, Flatten, Linear
from cleverhans.picklable_model import Softmax


class ModelBasicCNN(Model):
  def __init__(self, scope, nb_classes, nb_filters, **kwargs):
    del kwargs
    Model.__init__(self, scope, nb_classes, locals())
    self.nb_filters = nb_filters

    # Do a dummy run of fprop to make sure the variables are created from
    # the start
    self.fprop(self.make_input_placeholder())
    # Put a reference to the params in self so that the params get pickled
    self.params = self.get_params()

  def make_input_placeholder(self):
    return tf.placeholder(tf.float32, [128, 28, 28, 1])

  def get_layer_names(self):
    return ["conv1","conv2","conv3","logits"]

  def fprop(self, x, **kwargs):
    del kwargs
    my_conv = functools.partial(
        tf.layers.conv2d, activation=tf.nn.relu,
        kernel_initializer=initializers.HeReLuNormalInitializer)
    with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE):
      conv1 = my_conv(x, self.nb_filters, 8, strides=2, padding='same')
      conv2 = my_conv(conv1, 2 * self.nb_filters, 6, strides=2, padding='valid')
      conv3 = my_conv(conv2, 2 * self.nb_filters, 5, strides=1, padding='valid',)
      logits = tf.layers.dense(
          tf.layers.flatten(conv3), self.nb_classes,
          kernel_initializer=initializers.HeReLuNormalInitializer,name="logits")
      return {self.O_LOGITS: logits,
              self.O_PROBS: tf.nn.softmax(logits=logits),
              "conv1":conv1,
              "conv2":conv2,
              "conv3":conv3}


def make_basic_picklable_cnn(nb_filters=64, nb_classes=10,
                             input_shape=(None, 28, 28, 1)):
  """The model for the picklable models tutorial.
  """
  layers = [Conv2D(nb_filters, (8, 8), (2, 2), "SAME"),
            ReLU(),
            Conv2D(nb_filters * 2, (6, 6), (2, 2), "VALID"),
            ReLU(),
            Conv2D(nb_filters * 2, (5, 5), (1, 1), "VALID"),
            ReLU(),
            Flatten(),
            Linear(nb_classes),
            Softmax()]
  model = MLP(layers, input_shape)
  return model
