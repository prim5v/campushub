# import cv2
# import numpy as np
# import pickle
# import torch
# from facenet_pytorch import MTCNN, InceptionResnetV1
# from PIL import Image

# mtcnn = MTCNN(image_size=160, margin=20)
# facenet = InceptionResnetV1(pretrained="vggface2").eval()


# def is_blurry(image_path, threshold=100):
#     img = cv2.imread(image_path, 0)
#     lap = cv2.Laplacian(img, cv2.CV_64F).var()
#     return lap < threshold


# def extract_face_embedding(image_path):
#     img = Image.open(image_path).convert("RGB")
#     face = mtcnn(img)
#     if face is None:
#         return None
#     embedding = facenet(face.unsqueeze(0)).detach().numpy()
#     return embedding


# def compare_faces(emb1, emb2):
#     emb1 = torch.tensor(emb1)
#     emb2 = torch.tensor(emb2)
#     return torch.nn.functional.cosine_similarity(emb1, emb2).item()
