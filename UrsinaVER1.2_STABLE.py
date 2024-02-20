from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math
import random

app = Ursina()

# Constants
block_size = 1
num_blocks = 50
player_start_height = 30

# Terrain generation function using Simplex noise with reduced height scale
def generate_terrain():
    terrain = [[random.randint(1, 5) for _ in range(num_blocks)] for _ in range(num_blocks)]
    for z in range(num_blocks):
        for x in range(num_blocks):
            simplex_value = math.sin(x / 10) + math.sin(z / 10)
            terrain[x][z] = int(simplex_value * 5) + 1  # Adjusted height scale
    return terrain

terrain_map = generate_terrain()

# Create a player entity with refined controls
player = FirstPersonController(y=player_start_height, position=(num_blocks // 2, player_start_height, num_blocks // 2))

# Create a block class with lighting
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=texture,
            color=color.white,
            scale=block_size,
            collider='box',
        )

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                self.mine_block()
            elif key == 'right mouse down':
                self.place_block()

    def mine_block(self):
        destroy(self)

    def place_block(self):
        voxel = Voxel(position=self.position + mouse.normal, texture=block_types[selected_block])

# Create the terrain using the Voxel class
for z in range(num_blocks):
    for x in range(num_blocks):
        height = terrain_map[x][z]
        for y in range(height):
            voxel = Voxel(position=(x, y, z), texture='grass' if y == height - 1 else 'dirt')

# Create a directional light for the day-night cycle
DirectionalLight(direction=(1, 1, 1), color=(0.8, 0.8, 0.8, 1), mode='ambient')

# Add sky
sky = Sky(texture='sky_sunset')

# Inventory system for block types
block_types = ['grass', 'dirt', 'stone']
selected_block = 0

def cycle_block():
    global selected_block
    selected_block = (selected_block + 1) % len(block_types)
    print(f"Selected Block: {block_types[selected_block]}")

# Heads-Up Display (HUD) for inventory
class Inventory(Text):
    def __init__(self):
        super().__init__(
            text='Inventory: ',
            origin=(0, 0),
            x=-0.8,
            y=0.4,
            background=True,
            padding=(0.02, 0.02),
        )

    def update_text(self):
        self.text = 'Inventory: ' + block_types[selected_block]

inventory_display = Inventory()

# Day-night cycle
time_of_day = 0  # 0 to 1 (0 = midnight, 0.5 = noon, 1 = midnight)

# Input handling for cycling blocks, updating HUD, and day-night cycle
def update():
    global time_of_day

    if held_keys['scroll up']:
        cycle_block()
    elif held_keys['scroll down']:
        cycle_block()
    inventory_display.update_text()

    # Update day-night cycle
    time_of_day = (time_of_day + 0.0005) % 1
    sky.texture = f'sky_{int(time_of_day * 24)}.png'

# Run the application
app.run()