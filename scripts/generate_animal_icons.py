import os
from PIL import Image, ImageDraw

icons_dir = r"E:\koreader\plugins\animalchess.koplugin\icons"
os.makedirs(icons_dir, exist_ok=True)

# Generate crisp 128x128 black and white PNGs for each animal
# 1 = Rat, 2 = Cat, 3 = Wolf, 4 = Dog, 5 = Leopard, 6 = Tiger, 7 = Lion, 8 = Elephant

def create_animal_icons():
    # Common helper to draw both black-on-transparent (for white piece) and white-on-transparent (for black piece)
    for rank in range(1, 9):
        for color_name, fill_color, line_color in [("b", (255, 255, 255, 255), (0, 0, 0, 0)), ("w", (0, 0, 0, 255), (255, 255, 255, 0))]:
            img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            cx, cy = 64, 64
            
            if rank == 1: # Chuột (Rat)
                # Head
                draw.polygon([(40, 75), (88, 75), (64, 105)], fill=fill_color)
                # Ears (round)
                draw.ellipse([26, 32, 54, 60], fill=fill_color)
                draw.ellipse([74, 32, 102, 60], fill=fill_color)
                # Snout & eyes
                eye_col = (0, 0, 0, 255) if color_name == "b" else (255, 255, 255, 255)
                draw.ellipse([50, 70, 56, 76], fill=eye_col)
                draw.ellipse([72, 70, 78, 76], fill=eye_col)
                # Whiskers
                draw.line([(30, 85), (55, 88)], fill=fill_color, width=3)
                draw.line([(30, 95), (55, 92)], fill=fill_color, width=3)
                draw.line([(98, 85), (73, 88)], fill=fill_color, width=3)
                draw.line([(98, 95), (73, 92)], fill=fill_color, width=3)
                
            elif rank == 2: # Mèo (Cat)
                # Head
                draw.ellipse([36, 44, 92, 96], fill=fill_color)
                # Pointed ears
                draw.polygon([(36, 56), (30, 24), (54, 46)], fill=fill_color)
                draw.polygon([(92, 56), (98, 24), (74, 46)], fill=fill_color)
                # Eyes
                eye_col = (0, 0, 0, 255) if color_name == "b" else (255, 255, 255, 255)
                draw.ellipse([46, 62, 54, 74], fill=eye_col)
                draw.ellipse([74, 62, 82, 74], fill=eye_col)
                # Whiskers
                draw.line([(24, 70), (42, 72)], fill=fill_color, width=3)
                draw.line([(24, 80), (42, 76)], fill=fill_color, width=3)
                draw.line([(104, 70), (86, 72)], fill=fill_color, width=3)
                draw.line([(104, 80), (86, 76)], fill=fill_color, width=3)

            elif rank == 3: # Sói (Wolf)
                # Sharp predatory wolf head & ears
                draw.polygon([(64, 108), (42, 60), (52, 22), (64, 46), (76, 22), (86, 60)], fill=fill_color)
                # Scruff fur sides
                draw.polygon([(34, 70), (46, 55), (44, 80)], fill=fill_color)
                draw.polygon([(94, 70), (82, 55), (84, 80)], fill=fill_color)
                # Eyes
                eye_col = (0, 0, 0, 255) if color_name == "b" else (255, 255, 255, 255)
                draw.polygon([(50, 58), (58, 62), (52, 66)], fill=eye_col)
                draw.polygon([(78, 58), (70, 62), (76, 66)], fill=eye_col)

            elif rank == 4: # Chó (Dog)
                # Head
                draw.ellipse([40, 42, 88, 98], fill=fill_color)
                # Drooping ears
                draw.ellipse([22, 46, 44, 88], fill=fill_color)
                draw.ellipse([84, 46, 106, 88], fill=fill_color)
                # Snout
                eye_col = (0, 0, 0, 255) if color_name == "b" else (255, 255, 255, 255)
                draw.ellipse([48, 58, 56, 66], fill=eye_col)
                draw.ellipse([72, 58, 80, 66], fill=eye_col)
                draw.ellipse([58, 76, 70, 86], fill=eye_col)

            elif rank == 5: # Báo (Leopard)
                # Sleek feline head
                draw.ellipse([36, 42, 92, 94], fill=fill_color)
                draw.polygon([(38, 50), (32, 28), (52, 44)], fill=fill_color)
                draw.polygon([(90, 50), (96, 28), (76, 44)], fill=fill_color)
                eye_col = (0, 0, 0, 255) if color_name == "b" else (255, 255, 255, 255)
                draw.ellipse([46, 60, 56, 70], fill=eye_col)
                draw.ellipse([72, 60, 82, 70], fill=eye_col)
                # Spots
                draw.ellipse([60, 48, 68, 54], fill=eye_col)
                draw.ellipse([44, 76, 50, 82], fill=eye_col)
                draw.ellipse([78, 76, 84, 82], fill=eye_col)

            elif rank == 6: # Hổ (Tiger)
                # Fierce broad feline head
                draw.ellipse([34, 40, 94, 96], fill=fill_color)
                draw.ellipse([28, 34, 46, 52], fill=fill_color)
                draw.ellipse([82, 34, 100, 52], fill=fill_color)
                eye_col = (0, 0, 0, 255) if color_name == "b" else (255, 255, 255, 255)
                draw.ellipse([46, 62, 56, 70], fill=eye_col)
                draw.ellipse([72, 62, 82, 70], fill=eye_col)
                # Tiger forehead stripes (King mark 王)
                draw.line([(52, 46), (76, 46)], fill=eye_col, width=3)
                draw.line([(56, 52), (72, 52)], fill=eye_col, width=3)
                draw.line([(64, 44), (64, 56)], fill=eye_col, width=3)

            elif rank == 7: # Sư Tử (Lion)
                # Large radiating mane
                draw.ellipse([22, 22, 106, 106], fill=fill_color)
                face_col = (0, 0, 0, 255) if color_name == "b" else (255, 255, 255, 255)
                draw.ellipse([38, 40, 90, 92], fill=face_col)
                # Inner face details
                inner_col = fill_color
                draw.ellipse([48, 54, 56, 64], fill=inner_col)
                draw.ellipse([72, 54, 80, 64], fill=inner_col)
                draw.polygon([(58, 70), (70, 70), (64, 78)], fill=inner_col)

            elif rank == 8: # Voi (Elephant)
                # Giant head, big flap ears, trunk
                # Big ears
                draw.ellipse([14, 38, 56, 88], fill=fill_color)
                draw.ellipse([72, 38, 114, 88], fill=fill_color)
                # Head
                draw.ellipse([36, 32, 92, 90], fill=fill_color)
                # Trunk curling down
                draw.line([(64, 70), (64, 106), (74, 106)], fill=fill_color, width=12)
                # Eyes
                eye_col = (0, 0, 0, 255) if color_name == "b" else (255, 255, 255, 255)
                draw.ellipse([46, 54, 52, 62], fill=eye_col)
                draw.ellipse([76, 54, 82, 62], fill=eye_col)
                # Tusks
                tusk_col = fill_color if color_name == "b" else (0, 0, 0, 255)
                draw.line([(54, 84), (46, 96)], fill=tusk_col, width=4)
                draw.line([(74, 84), (82, 96)], fill=tusk_col, width=4)

            filename = f"piece_{color_name}_{rank}.png"
            img.save(os.path.join(icons_dir, filename), "PNG")

    print(f"Generated 16 transparent animal PNG icons in {icons_dir}")

create_animal_icons()
