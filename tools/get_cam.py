import cv2

def listar_camaras(max_index=10):
    disponibles = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            disponibles.append(i)
            cap.release()
    return disponibles

print("Cámaras disponibles:", listar_camaras(10))
