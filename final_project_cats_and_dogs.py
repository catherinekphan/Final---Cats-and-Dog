# -*- coding: utf-8 -*-
"""Final Project Cats and Dogs

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ew2kNGYQHv0O-EspjQa2QHD1sbe7DRJJ

# Final : Cats and Dogs

This project focuses on classifying images of cats and dogs, which is part of a Kaggle competition (Cukierski, 2013). Image classification tasks like this one are vital for a wide range of applications, from automating content moderation to improving user experience in image-based applications. By developing a model that accurately distinguishes between cats and dogs, we aim to contribute to this field by leveraging machine learning techniques to solve a practical problem.

Our project involves working with a dataset of images featuring cats and dogs. Specifically, we have a dataset of images that will be used to train and evaluate our model. The primary goal is to create a computer program that can correctly identify whether an image contains a cat or a dog.

To achieve this, we will build a specialized computer model known as a Convolutional Neural Network (CNN). CNNs are particularly effective at analyzing visual information and are commonly used for image classification tasks. We will train this model using the dataset, iterating on it to enhance its performance.

The project will begin with importing the dataset from Kaggle, a popular platform for data science competitions and datasets. Given the size of the dataset, we will use Kaggle’s tools to streamline the process. Our initial step will be to explore the data, which involves examining the structure and content of the images and labels to understand the dataset better.

After familiarizing ourselves with the data, we’ll train our model to recognize patterns and features in the images that differentiate between cats and dogs. This involves feeding the images into the model, tuning its parameters, and improving its accuracy. Once trained, we will evaluate the model’s performance on a separate test set of images that it hasn’t seen before. This will help us assess how effectively the model can classify new images in real-world scenarios.

Let's dive into the analysis and start building our classifier!
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import glob
import random

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Activation, BatchNormalization, ReLU, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from PIL import Image
import matplotlib.image as img
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.optimizers import Adam

"""# Project Setup and Data Preparation

First, we mount Google Drive to access files stored there. This is done using the drive.mountcommand, which allows us to interact with our files in Google Drive from within the Google Colab environment. Next, we configure Kaggle API access by creating a .kaggle directory and copying the kaggle.json file, which contains our Kaggle credentials. This setup ensures we can use Kaggle’s tools for downloading competition datasets.

After setting up Kaggle access, we use the Kaggle API to download the dataset for the "Dogs vs. Cats" competition. The dataset is contained in ZIP files, which we extract using Python’s zipfile module. We then check the contents of the extracted directories to confirm that the files are correctly unzipped.

Examining the contents of the train directory, we can observe that it contains 25,000 images. This is a significant dataset that will be used to train our classification model, allowing us to build and evaluate an effective image classifier.
"""

from google.colab import drive
import os
drive.mount('/content/drive')

!mkdir -p ~/.kaggle
!cp /content/drive/MyDrive/Last\ Class\ Material/Final\ Project\ Cats\ and\ Dogs/kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

print(os.listdir('/root/.kaggle'))

!kaggle competitions download -c dogs-vs-cats

import zipfile

zip_files = ['test1', 'train']

for zip_file in zip_files:
    with zipfile.ZipFile("/content/drive/MyDrive/Last Class Material/Final Project Cats and Dogs/{}.zip".format(zip_file), "r") as z:
        z.extractall(".")
        print("{} unzipped".format(zip_file))

TRAIN_DIR_PATH = './train'
file_names = os.listdir(TRAIN_DIR_PATH)
print('There are {} number of images in directory.'.format(len(file_names)))

sample_submission = pd.read_csv('/content/drive/MyDrive/Last Class Material/Final Project Cats and Dogs/sampleSubmission (1).csv')

def to_dataframe(file_names):
    files = file_names
    labels = [file[:3] for file in file_names]

    df = pd.DataFrame({'filename': files, 'label': labels})

    return df

df = to_dataframe(file_names)

df.head()

sample_submission.head()

print('Data set label distribution:\n', df['label'].value_counts())

sns.set_style("whitegrid")

plt.figure(figsize=(10, 6))

ax = sns.countplot(x='label', data=df, palette='viridis')

ax.set_title('Distribution of Cat and Dog Images', fontsize=16, weight='bold')
ax.set_xlabel('Label', fontsize=14)
ax.set_ylabel('Count', fontsize=14)

for p in ax.patches:
    height = p.get_height()
    ax.annotate(f'{height}', (p.get_x() + p.get_width() / 2., height),
                ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                textcoords='offset points')
plt.show()

sample_submission.shape

"""# Organizing Images and Visualizing Samples

We start by categorizing the images into 'cat' and 'dog' groups based on their filenames. This is achieved by iterating through the list of file names and appending each image to the appropriate category list. This organization allows us to efficiently manage and access images based on their label.

Next, we define a function plot_random_images that randomly selects and displays a specified number of images from a given list. This function is crucial for visually inspecting the data and ensuring that the images are correctly labeled and representative of their respective categories. By displaying random samples of cat and dog images, we can confirm the quality and variety of the dataset before proceeding with model training.

We then load the image files for cats and dogs from the training directory and use the plot_random_images function to display a few random images from each category. This step helps us verify the data visually, providing a preliminary check to ensure that the images are correctly labeled and appropriately formatted for the classification task. This visual inspection is important as it helps to identify any potential issues with the dataset, such as incorrect labels or corrupted images, before training the model.
"""

categories = {'cat': [], 'dog': []}

for file in file_names:
    label = file[:3]
    if label in categories:
        categories[label].append(file)

cat_files = categories['cat']
dog_files = categories['dog']

def plot_random_images(image_list, title, num_images=4):
    plt.figure(figsize=(15, 7))
    random_indices = np.random.choice(len(image_list), num_images, replace=False)

    for i, idx in enumerate(random_indices, start=1):
        image_path = image_list[idx]
        im = img.imread(image_path)
        print(f'Image shape: {im.shape}')
        plt.subplot(2, 2, i)
        plt.imshow(im)
        plt.axis('off')

    plt.suptitle(title)
    plt.show()

# Load image files for cats and dogs
cat_image_files = glob.glob('./train/cat.*.jpg')
dog_image_files = glob.glob('./train/dog.*.jpg')

# Display random cat images
plot_random_images(cat_image_files, 'Random Cat Images')

# Display random dog images
plot_random_images(dog_image_files, 'Random Dog Images')

"""# Splitting Up the Data

In this section, we split our dataset into training and validation sets and visualize the distribution of labels within these sets.

First, we check if the DataFrame df is properly defined and not empty. If this condition is met, we split df into training and validation subsets using train_test_split. We allocate 20% of the data for validation and 80% for training. The resulting sizes of the training and validation sets are 20,000 and 5,000 images, respectively. This split is essential for evaluating our model's performance on unseen data and ensuring that it generalizes well beyond the training data.

Next, we visualize the distribution of labels within the training and validation sets. Using Seaborn, we create count plots to display the number of cat and dog images in each set. The plots help us verify that both sets are balanced and representative of the overall dataset. This balance is crucial for training an unbiased model and for evaluating its performance accurately. The visualization confirms that the label distribution is similar in both the training and validation sets, which is important for ensuring that the model is trained and tested on a representative sample of the data.

"""

if isinstance(df, pd.DataFrame) and not df.empty:
    train_set, valid_set = train_test_split(df, test_size=0.2)
    print(f"Training set size: {len(train_set)}")
    print(f"Validation set size: {len(valid_set)}")
else:
    print("DataFrame is not defined or is empty.")

print("Training set shape: {}".format(train_set.shape))
print("Validation set shape: {}".format(valid_set.shape))

def plot_label_distribution(df, title, ax):

    sns.countplot(x=df['label'], order=['dog', 'cat'], ax=ax, palette='pink')
    ax.set_title(title, fontsize=14)
    ax.set_xlabel('Label', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)

print('Train set distribution:\n', train_set['label'].value_counts())
print('\nValidation set distribution:\n', valid_set['label'].value_counts())
print()

fig, axes = plt.subplots(1, 2, figsize=(15, 5))

plot_label_distribution(train_set, 'Train Set Label Distribution', axes[0])
plot_label_distribution(valid_set, 'Validation Set Label Distribution', axes[1])

plt.tight_layout()
plt.show()

"""# Data Augmentation and Preparation for Training and Validation

In this section, we prepare our image data for training and validation using ImageDataGenerator, a powerful tool for real-time data augmentation and preprocessing.

First, we configure the ImageDataGenerator for the training data with several augmentation techniques, including rotation, zoom, horizontal flipping, and shifts in width and height. These augmentations help create variations of the images, making the model more robust and improving its ability to generalize to new data. We also normalize the pixel values to a range of [0, 1] by scaling them with rescale=1./255.

We then use this ImageDataGenerator to create a training_data generator, which loads images from the train_set DataFrame and applies the specified augmentations. We configure it to generate batches of 32 images at a time, and we shuffle the data to ensure that each epoch sees a different order of images. The generator is set to handle 20,000 images and will produce 625 batches per epoch. The class indices are mapped to 'cat' and 'dog', with respective labels 0 and 1.

To verify the data preparation, we display a few sample images with their labels using matplotlib. This helps us confirm that the images are correctly loaded and augmented.

Similarly, we configure a valid_datagen for the validation data, which only performs rescaling without augmentation. The validation_data generator processes images from the valid_set DataFrame, producing batches of 32 images. With 5,000 images, this generator will create 156 batches per epoch. The class indices for the validation data are consistent with those used in training.

This step ensures that our training and validation data are properly prepared and ready for use in training and evaluating the machine learning model. Proper data augmentation and preprocessing are crucial for improving model performance and ensuring it generalizes well to new, unseen data.
"""

WIDTH, HEIGHT = 150, 150
BATCH_SIZE = 32

train_datagen = ImageDataGenerator(
    rotation_range=15,
    rescale=1./255,
    shear_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True,
    width_shift_range=0.1,
    height_shift_range=0.1
)

training_data = train_datagen.flow_from_dataframe(
    dataframe=train_set,
    directory='./train',
    x_col='filename',
    y_col='label',
    target_size=(WIDTH, HEIGHT),
    class_mode='categorical',
    batch_size=BATCH_SIZE,
    shuffle=True,
)

print(f"Number of batches per epoch: {training_data.n // training_data.batch_size}")
print(f"Class labels: {training_data.class_indices}")

training_data.class_indices

num_displayed = 0

while num_displayed < 6:
    images, labels = next(training_data)

    plt.figure(figsize=(4, 4))
    plt.imshow(images[0])

    label_index = np.argmax(labels[0])
    label_name = list(training_data.class_indices.keys())[list(training_data.class_indices.values()).index(label_index)]

    plt.title(f"Label: {label_name}")
    plt.axis('off')
    plt.show()
    num_displayed += 1

WIDTH, HEIGHT = 150, 150
BATCH_SIZE = 32

valid_datagen = ImageDataGenerator(rescale=1./255)
validation_data = valid_datagen.flow_from_dataframe(
    dataframe=valid_set,
    directory='./train',
    x_col='filename',
    y_col='label',
    target_size=(WIDTH, HEIGHT),
    class_mode='categorical',
    batch_size=BATCH_SIZE,
    shuffle=False
)

print(f"Number of validation batches: {validation_data.n // validation_data.batch_size}")
print(f"Class labels: {validation_data.class_indices}")

"""# Building, Training, and Evaluating a Convolutional Neural Network for Image Classification
In this segment, we focus on constructing and training a Convolutional Neural Network (CNN) for classifying images into two categories: cats and dogs.

Model Architecture:
We define a CNN using TensorFlow's Keras API, starting with a series of convolutional and pooling layers. The model begins with a convolutional layer that has 32 filters and a kernel size of 5x5, followed by max-pooling. This is followed by two convolutional blocks, each consisting of convolutional layers with increasing filter sizes (64 and 128) and subsequent max-pooling operations. After these blocks, the model is flattened and connected to two fully connected (dense) layers with dropout to reduce overfitting. Finally, a dense layer with a softmax activation function outputs the classification probabilities for the two classes.

Callbacks Configuration:
To optimize training, we employ several callbacks:

EarlyStopping halts training if validation loss does not improve, restoring the best model weights.
ReduceLROnPlateau reduces the learning rate if validation loss plateaus.
ModelCheckpoint saves the best model based on validation loss.
TensorBoard logs metrics for visualization and debugging.
Model Compilation and Training:
The model is compiled with the Stochastic Gradient Descent (SGD) optimizer and categorical cross-entropy loss function. It is then trained for 10 epochs using the training_data and validation_data generators. We track training and validation accuracy and loss, displaying graphs to monitor performance over epochs.

Transfer Learning with VGG16:
As an advanced approach, we use transfer learning by leveraging the VGG16 model, pre-trained on ImageNet. We remove the top layers of VGG16, add custom layers for our specific task, and freeze the base model's weights to prevent them from being updated during training. This allows the model to retain general features learned from ImageNet while learning specific features for our task.

Model Evaluation and Predictions:
After training, the model is evaluated on validation data to determine its loss and accuracy. Predictions are made on a separate test dataset, and the results are saved to a CSV file for submission. This process includes preprocessing test images, making predictions, and mapping the predicted class indices back to labels.
"""

from tensorflow.keras import layers, models

WIDTH, HEIGHT = 150, 150
NUM_CLASSES = 2

def DefaultConv2D(filters, kernel_size=3, activation='relu', padding='SAME'):
    return layers.Conv2D(filters=filters, kernel_size=kernel_size, activation=activation, padding=padding)

model = models.Sequential([
    DefaultConv2D(filters=32, kernel_size=5, activation='relu', padding='SAME'),
    layers.MaxPooling2D(pool_size=2),

    DefaultConv2D(filters=64),
    DefaultConv2D(filters=64),
    layers.MaxPooling2D(pool_size=2),

    DefaultConv2D(filters=128),
    DefaultConv2D(filters=128),
    layers.MaxPooling2D(pool_size=2),

    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(32, activation='relu'),
    layers.Dropout(0.2),

    layers.Dense(NUM_CLASSES, activation='softmax')
])

from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
import datetime

earlystop_cb = EarlyStopping(
    patience=10,
    restore_best_weights=True,
    monitor='val_loss',
    verbose=1
)
reduce_lr_cb = ReduceLROnPlateau(
    factor=0.5,
    patience=5,
    monitor='val_loss',
    min_lr=1e-5,
    verbose=1
)

checkpoint_cb = ModelCheckpoint(
    filepath='model.keras',
    save_best_only=True,
    monitor='val_loss',
    verbose=1
)
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%d%m%Y-%H%M")
tensorboard_cb = TensorBoard(
    log_dir=log_dir,
    histogram_freq=1,
    update_freq='epoch',
    write_graph=True,
    write_images=True
)

callbacks = [earlystop_cb, reduce_lr_cb, checkpoint_cb, tensorboard_cb]

from tensorflow.keras.optimizers import SGD

model.compile(
    loss="categorical_crossentropy",
    optimizer=SGD(learning_rate=0.01, momentum=0.9),
    metrics=['accuracy']
)

history = model.fit(
    training_data,
    epochs=10,
    validation_data=validation_data,
    steps_per_epoch=10,
    validation_steps=10,
    callbacks=callbacks
)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc))

plt.figure(figsize=(15, 6))

plt.subplot(1, 2, 1)
plt.plot(epochs, acc, 'bo-', label='Training Accuracy')
plt.plot(epochs, val_acc, 'b-', label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(epochs, loss, 'go-', label='Training Loss')
plt.plot(epochs, val_loss, 'g-', label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

base_model = VGG16(weights='imagenet', include_top=False, input_shape=(WIDTH, HEIGHT, 3))

for layer in base_model.layers:
    layer.trainable = False

x = base_model.output
x = Flatten()(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(NUM_CLASSES, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=x)

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

history = model.fit(
    training_data,
    epochs=10,
    validation_data=validation_data,
    steps_per_epoch=training_data.samples // BATCH_SIZE,
    validation_steps=validation_data.samples // BATCH_SIZE,
    callbacks=callbacks
)

eval_results = model.evaluate(validation_data)
print(f'Validation Loss: {eval_results[0]}')
print(f'Validation Accuracy: {eval_results[1]}')

train_dir = './train'
test_dir = './test1'


file_names = os.listdir(train_dir)
print('There are {} images in the train directory.'.format(len(file_names)))

test_filenames = os.listdir(test_dir)
test_df = pd.DataFrame({'filename': test_filenames})
test_datagen = ImageDataGenerator(rescale=1./255)
test_data = test_datagen.flow_from_dataframe(
    dataframe=test_df,
    directory=test_dir,
    x_col='filename',
    target_size=(WIDTH, HEIGHT),
    batch_size=1,
    shuffle=False,
    class_mode=None
)

predictions = model.predict(test_data, verbose=1)
predicted_classes = np.argmax(predictions, axis=1)

class_labels = {0: 'cat', 1: 'dog'}
predicted_labels = [class_labels[i] for i in predicted_classes]

submission_df = pd.DataFrame({
    'filename': test_df['filename'],
    'label': predicted_labels
})

submission_df.to_csv('submission.csv', index=False)

"""# Conclusion and Next Steps
Through this project, I gained valuable insights into building and optimizing Convolutional Neural Networks (CNNs) for image classification tasks. Designing the network from scratch and integrating transfer learning with VGG16 enhanced my understanding of model architecture and optimization. I learned how to effectively use data augmentation techniques to improve generalization and implemented various callbacks to monitor and refine the training process. This experience highlighted the importance of careful model evaluation and the benefits of leveraging pre-trained models to achieve better performance.

Looking ahead, I plan to delve into hyperparameter tuning to explore how different learning rates, batch sizes, and network configurations impact model performance. Experimenting with advanced data augmentation techniques and exploring other CNN architectures like ResNet or EfficientNet could further enhance the model's accuracy. Additionally, fine-tuning the pre-trained model and employing ensembling techniques are promising avenues to improve results. These steps will build on the foundation laid in this project, offering opportunities for deeper exploration and potentially achieving even greater performance.
"""