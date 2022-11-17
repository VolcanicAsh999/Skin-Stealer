import requests
import base64
import json
from urllib import request

import pygame
pygame.init()

def download_skin(skin_dir, username):
    """Download the skin and return False if there is an error, True otherwise"""
    try:
        resp_to_get_uuid = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        uuid = resp_to_get_uuid.json()["id"]  # If this fail, the username is probably not valid
        resp_to_get_skin = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
        value_encoded = resp_to_get_skin.json()["properties"][0]["value"]
        value_decoded = base64.b64decode(value_encoded, )
        url_skin = json.loads(value_decoded.decode())["textures"]["SKIN"]["url"]
        request.urlretrieve(url_skin, skin_dir)
        return True
    except Exception as e:
        raise Warning(f"Error while downloading skin: {e}")

def load_skin(skin_dir):
    img = pygame.image.load(skin_dir)
    return img#.convert_alpha()

def show_skin(skinimg, mode='front'):
    frag = skinimg[mode]
    head = skinimg['head'][mode]
    head = pygame.transform.scale2x(pygame.transform.scale2x(head))
    frag = pygame.transform.scale2x(pygame.transform.scale2x(frag))
    d = pygame.display.set_mode((frag.get_width(), frag.get_height() + head.get_height()))
    d.blit(head, (16, 0))
    d.blit(frag, (0, head.get_height()-32))
    pygame.display.flip()

def _doitall(skin_dir, username):
    download_skin(skin_dir, username)
    skin = load_skin(skin_dir)
    img = get_img_from_skin(skin)
    show_skin(img)

def steal_and_load(username):
    _doitall('skins\\' + username + '.png', username)

def get_img_from_skin(skin: pygame.Surface) -> dict:
    """transform a minecraft skin into a dict of texture veertices"""
    skin.set_alpha(255)
    # Creating fragments
    names_fragments: dict[str, list[list[int], int]] = {
        "head":
            [[8, 8, 8, 8],
             [40, 8, 8, 8],
             8],

        "body":
            [[20, 20, 8, 12],
             [20, 20, 8, 12],
             4],

        "left_leg":
            [[4, 20, 4, 12],
             [4, 36, 4, 12],
             4],

        "right_leg":
            [[20, 52, 4, 12],
             [4, 52, 4, 12],
             4],

        "left_arm":
            [[44, 20, 4, 12],
             [44, 36, 4, 12],
             4],

        "right_arm":
            [[36, 52, 4, 12],
             [52, 52, 4, 12],
             4],
    }
    fragments: dict[str, dict[str, pygame.Surface] | pygame.Surface] = {}
    for name, sides in names_fragments.items():
        fragments[name] = frag = {}
        surface_1_rect, surface_2_rect, width_side = sides
        x_front_1, y_front_1 = surface_1_rect[:2]
        x_front_2, y_front_2 = surface_2_rect[:2]
        width, height = surface_1_rect[2: 4]
        for side_name, x, width_morceau in [("front", 0, width), ("left", -width_side, width_side), ("right", width, width_side)]:
            frag[side_name] = pygame.Surface((width_morceau, height))
            frag[side_name].blit(skin.subsurface([x_front_1+x, y_front_1, width_morceau, height]), (0, 0))
            frag[side_name].blit(skin.subsurface([x_front_2+x, y_front_2, width_morceau, height]), (0, 0))
    fragments["cou"] = {
        "front": fragments["body"]["front"].subsurface([2, 0, 4, 1]),
        "left": fragments["body"]["left"].subsurface([1, 0, 2, 1]),
        "right": fragments["body"]["right"].subsurface([1, 0, 2, 1]),
    }

    # Creating Front skin
    emplacements_front_skin = {
        "body": (4, 9),
        "cou": (6, 8),
        "left_leg": (4, 21),
        "right_leg": (8, 21),
        "left_arm": (0, 9),
        "right_arm": (12, 9)
    }
    front_skin = pygame.Surface((16, 33))
    front_skin.fill((0, 0, 1))
    front_skin.set_colorkey((0, 0, 1, 0), )
    for name, to in emplacements_front_skin.items():
        front_skin.blit(fragments[name]["front"], to)
    fragments["front"] = front_skin

    # Creating Sneaking Front skin
    sneaking_img = pygame.Surface((front_skin.get_width(), 12 * 3 + 21 * 2))
    sneaking_img.fill((0, 0, 1))
    sneaking_img.set_colorkey((0, 0, 1, 0))
    for x in range(front_skin.get_width()):
        for y in range(front_skin.get_height() - 21):
            for y_inc in range(3):
                sneaking_img.set_at((x, 42 + y * 3 + y_inc), front_skin.get_at((x, 21 + y)))
    for x in range(front_skin.get_width()):
        for y in range(21):
            for y_inc in range(2):
                sneaking_img.set_at((x, y * 2 + y_inc), front_skin.get_at((x, y)))
    fragments["sneaking_front"] = sneaking_img

    # Creating the head scroller
    fragments["head_scroller"] = head_scroller = {}
    head_scroller["horizontal"] = horizontal_scroller = pygame.Surface((16, 8))
    horizontal_scroller.fill((0, 0, 1))
    horizontal_scroller.set_colorkey((0, 0, 1, 0))
    horizontal_scroller.blit(skin.subsurface([4, 8, 16, 8]), (0, 0))
    horizontal_scroller.blit(skin.subsurface([36, 8, 16, 8]), (0, 0))

    # Creating the head scroller
    head_scroller["vertical"] = vertical_scroller = pygame.Surface((8, 12))
    vertical_scroller.fill((0, 0, 1))
    vertical_scroller.set_colorkey((0, 0, 1, 0))
    vertical_scroller.blit(skin.subsurface([8, 6, 8, 10]), (0, 0))
    vertical_scroller.blit(skin.subsurface([40, 6, 8, 10]), (0, 0))
    # This two surface must be flipped
    vertical_scroller.blit(pygame.transform.flip(skin.subsurface([16, 6, 8, 2]), False, True), (0, 10))
    vertical_scroller.blit(pygame.transform.flip(skin.subsurface([48, 6, 8, 2]), False, True), (0, 10))

    return fragments
