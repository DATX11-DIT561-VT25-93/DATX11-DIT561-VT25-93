from feature_extraction import init_facenet, is_face_aligned
from detection import detect_face
from performance_log import evaluate_georgia_tech_faces
import tensorflow as tf
import os
import cv2
import numpy as np
from collections import defaultdict


rec_model = init_facenet()

for layer in rec_model.layers[:-30]:
    layer.trainable = False
for layer in rec_model.layers[-30:]:
    layer.trainable = True
rec_model.trainable = True

for layer in rec_model.layers:
    if isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = False


optimizer = tf.keras.optimizers.Adam(learning_rate=1e-6)

def triplet_loss_fn(anchor, positive, negative, margin=0.1):
    pos_dist = tf.reduce_sum(tf.square(anchor - positive), axis=1)
    neg_dist = tf.reduce_sum(tf.square(anchor - negative), axis=1)
    loss = tf.maximum(pos_dist - neg_dist + margin, 0.0)
    return tf.reduce_mean(loss)

def detect_face_no_base64(image_array):
    model_path = os.path.join(os.path.dirname(__file__), "face_detection_yunet_2023mar.onnx")

    detector = cv2.FaceDetectorYN.create(
        model_path,
        "",
        (320, 320),
        0.9,
        0.1,
        10
    )

    h, w = image_array.shape[:2]
    detector.setInputSize((w, h))

    faces = detector.detect(image_array)[1]
    image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

    if faces is not None:
        return faces, None, image_rgb
    return None, None, None


base_dir = os.path.dirname(__file__)
data_dir = os.path.join(base_dir, "gt_db")
person_images = defaultdict(list)

for person_folder in sorted(os.listdir(data_dir)):
    person_path = os.path.join(data_dir, person_folder)
    if not os.path.isdir(person_path):
        continue
    for file in os.listdir(person_path):
        if file.lower().endswith(".jpg"):
            img_path = os.path.join(person_path, file)
            faces, _, rgb = detect_face_no_base64(cv2.imread(img_path))
            if is_face_aligned(faces[0]):
                person_images[person_folder].append(img_path)
            
print(f"Loaded {len(person_images)} people from dataset.")

def load_and_preprocess(img_path):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (160, 160))
    img = img / 255.0
    return img.astype(np.float32)


def compute_embeddings(image_paths, model):
    embeddings = []
    for img_path in image_paths:
        img = load_and_preprocess(img_path)
        img = np.expand_dims(img, axis=0)
        embed = model(img, training=False).numpy()
        # embed = embed / np.linalg.norm(embed)  # L2 normalize
        embeddings.append(embed[0])
    return np.array(embeddings)

def semi_hard_triplet_miner(person_images, model, batch_size=32, margin=1):
    person_ids = list(person_images.keys())
    all_triplets = []

    image_data = []
    labels = []
    for pid in person_ids:
        for path in person_images[pid]:
            image_data.append(path)
            labels.append(pid)

    embeddings = compute_embeddings(image_data, model)
    label_to_indices = defaultdict(list)
    for idx, label in enumerate(labels):
        label_to_indices[label].append(idx)

    while True:
        anchors, positives, negatives = [], [], []
        while len(anchors) < batch_size:
            anchor_idx = np.random.randint(0, len(image_data))
            anchor_embed = embeddings[anchor_idx]
            anchor_label = labels[anchor_idx]

            positive_idx = np.random.choice([i for i in label_to_indices[anchor_label] if i != anchor_idx])
            positive_embed = embeddings[positive_idx]

            pos_dist = np.sum((anchor_embed - positive_embed)**2)

            neg_candidates = [i for i in range(len(image_data)) if labels[i] != anchor_label]
            np.random.shuffle(neg_candidates)
            found = False
            for neg_idx in neg_candidates:
                negative_embed = embeddings[neg_idx]
                neg_dist = np.sum((anchor_embed - negative_embed)**2)
                if pos_dist < neg_dist < pos_dist + margin:
                    anchors.append(load_and_preprocess(image_data[anchor_idx]))
                    positives.append(load_and_preprocess(image_data[positive_idx]))
                    negatives.append(load_and_preprocess(image_data[neg_idx]))
                    found = True
                    break

            if not found:
                neg_idx = np.random.choice(neg_candidates)
                anchors.append(load_and_preprocess(image_data[anchor_idx]))
                positives.append(load_and_preprocess(image_data[positive_idx]))
                negatives.append(load_and_preprocess(image_data[neg_idx]))

        yield (np.array(anchors), np.array(positives), np.array(negatives))



initial_weights = rec_model.get_weights()[0].copy()

batch_size = 32
steps_per_epoch = 100
print_interval = 5  

for epoch in range(1):
    print(f"\nEpoch {epoch + 1}")

    triplet_ds = tf.data.Dataset.from_generator(
        lambda: semi_hard_triplet_miner(person_images, rec_model, batch_size=batch_size),
        output_signature=(
            tf.TensorSpec(shape=(None, 160, 160, 3), dtype=tf.float32),
            tf.TensorSpec(shape=(None, 160, 160, 3), dtype=tf.float32),
            tf.TensorSpec(shape=(None, 160, 160, 3), dtype=tf.float32),
        )
    ).prefetch(1)

    total_loss = 0
    for step, (a, p, n) in enumerate(triplet_ds.take(steps_per_epoch)):
        with tf.GradientTape() as tape:
            a_embed = tf.nn.l2_normalize(rec_model(a, training=True), axis=1)
            p_embed = tf.nn.l2_normalize(rec_model(p, training=True), axis=1)
            n_embed = tf.nn.l2_normalize(rec_model(n, training=True), axis=1)
            loss = triplet_loss_fn(a_embed, p_embed, n_embed)
        grads = tape.gradient(loss, rec_model.trainable_weights)
        optimizer.apply_gradients(zip(grads, rec_model.trainable_weights))
        total_loss += loss.numpy()

        if (step + 1) % print_interval == 0 or (step + 1) == steps_per_epoch:
            print(f"  Step {step + 1}/{steps_per_epoch}, Batch Loss: {loss.numpy():.4f}")

    print(f"Average Loss for Epoch {epoch + 1}: {total_loss / steps_per_epoch:.4f}")


results = evaluate_georgia_tech_faces(rec_model)
for k, v in results.items():
    print(f"{k}: {v}")

new_weights = rec_model.get_weights()[0]
change = np.linalg.norm(initial_weights - new_weights)
print(f"Weight change after training: {change:.6f}")

rec_model.save_weights(os.path.join(base_dir, "facenet_finetuned_weights.h5"))