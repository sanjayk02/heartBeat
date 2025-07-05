import os
import json
from PIL import Image
from sklearn.cluster import KMeans
import numpy as np

# Set your shader-to-texture mapping here
shader_map = {
    "lambert1": "flower_diffuse.png",
    "blinn1": "rust_metal.jpg"
}

def get_dominant_color(image_path, k=3):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((64, 64))  # speedup
    data = np.array(img).reshape(-1, 3)

    kmeans = KMeans(n_clusters=k)
    kmeans.fit(data)

    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    dominant = kmeans.cluster_centers_[np.argmax(counts)]
    return [int(c) for c in dominant]

def build_shader_color_data(texture_folder, shader_map):
    result = {}

    for shader, tex_file in shader_map.items():
        tex_path = os.path.join(texture_folder, tex_file)
        if os.path.exists(tex_path):
            try:
                dom_color = get_dominant_color(tex_path)
                result[shader] = {
                    "file": tex_file,
                    "dominant_color": dom_color
                }
            except Exception as e:
                print("Failed:", tex_file, "Reason:", str(e))

    with open(os.path.join(texture_folder, "shader_texture_colors.json"), "w") as f:
        json.dump(result, f, indent=2)

    print("✔️ Saved to shader_texture_colors.json")

# Example usage
texture_folder = r"C:\path\to\textures"
build_shader_color_data(texture_folder, shader_map)
