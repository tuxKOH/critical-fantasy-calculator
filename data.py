# Weapon Database with level requirements
WEAPON_DB = {
    'furioso': {
        'name': 'Furioso',
        'type': 'furioso',
        'stats': {'atk_min': 475, 'atk_max': 475},
        'level_req': 80,
        'image_url': 'https://trello.com/1/cards/685c870caeb2a5393cf32b1d/attachments/685c87e62f6c05fd2a869103/download/Furioso.png '
    },
    'wooden_sword': {
        'name': 'Wooden Sword',
        'type': 'sword',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'set': 'blessing',
        'level_req': 1,
        'image_url': ' https://trello.com/1/cards/683adc5901a8ede76a21c9f4/attachments/68593b8a5bcd1fea401f830a/download/WoodenSword.png'
    },
    'wooden_staff': {
        'name': 'Wooden Staff', 
        'type': 'staff',
        'stats': {'magic': 4},
        'set': 'blessing',
        'level_req': 1,
        'image_url': 'https://trello.com/1/cards/683ada834b01ed225b03759a/attachments/68593b47e44b5a74d33fbc68/download/WoodenBow.png'
    },
    'wooden_bow': {
        'name': 'Wooden Bow',
        'type': 'bow', 
        'stats': {'atk_min': 5, 'atk_max': 5},
        'set': 'blessing',
        'level_req': 1,
        'image_url': ' https://trello.com/1/cards/683ad967e61682b9d2f68fa5/attachments/68593b681d088e6a4bb939ca/download/WoodenStaff.png'
    },
    'divine_blade': {
        'name': 'Divine Blade',
        'type': 'sword',
        'stats': {'atk_min': 75, 'atk_max': 83},
        'set': 'explorer',
        'level_req': 15,
        'image_url': 'https://trello.com/1/cards/681a06e4780aaf135cc9aee4/attachments/68593b93fb34ec5ee985c15c/download/DivineBlade.png '
    },
    'forest_dweller_staff': {
        'name': 'Forest Dweller\'s Staff',
        'type': 'staff',
        'stats': {'magic': 60},
        'set': 'explorer',
        'level_req': 15,
        'image_url': 'https://trello.com/1/cards/681a06ebef158be2626ae3a0/attachments/68593bad8d747ec4e4a8b6b7/download/RootboundSpire.png '
    },
    'forest_dweller_bow': {
        'name': 'Forest Dweller\'s Bow',
        'type': 'bow',
        'stats': {'atk_min': 75, 'atk_max': 83},
        'set': 'explorer',
        'level_req': 15,
        'image_url': ' https://trello.com/1/cards/681a06e7a92b04a77b523379/attachments/68593bb8fe88e88c9bbfccb3/download/SylvanWhisper.png'
    },
    'crescendo_scythe': {
        'name': 'Crescendo Scythe',
        'type': 'scythe',
        'stats': {'atk_min': 75, 'atk_max': 75},
        'set': 'library_ruina',
        'level_req': 15,
        'image_url': 'https://trello.com/1/cards/681a06e0c776f008ed600898/attachments/68593beea4e7fac4a87de2f5/download/Crescendo.png '
    },
    'emerald_staff': {
        'name': 'Emerald Staff',
        'type': 'staff', 
        'stats': {'magic': 500},
        'level_req': 65,
        'image_url': ' https://trello.com/1/cards/6847bfee3b5d53410f93ec0a/attachments/68593c0b7df4b254272798b7/download/VerdantHeartwood.png'
    },
    'winter_howl': {
        'name': 'Winter Howl',
        'type': 'sword',
        'stats': {'atk_min': 325, 'atk_max': 360},
        'set': 'wolf_howl',
        'level_req': 65,
        'image_url': 'https://trello.com/1/cards/683da34a621446a6892692c3/attachments/68593c1436b07d3bea995187/download/WinterHowl.png '
    },
    'eventide': {
        'name': 'Eventide',
        'type': 'bow',
        'stats': {'atk_min': 325, 'atk_max': 360},
        'set': 'queen_bee',
        'level_req': 65,
        'image_url': 'https://trello.com/1/cards/683da358a19b5b7417b87b36/attachments/68593bfbf8d4fbbfd4e2228f/download/ApiaryFury.png '
    },
    'dawnbreak': {
        'name': 'Dawnbreak',
        'type': 'sword',
        'stats': {'atk_min': 1599, 'atk_max': 1599},
        'level_req': 190,
        'image_url': 'https://trello.com/1/cards/683ef40eb7b4cc5ad693305f/attachments/6934146d8fa2af966221e0b6/download/Screenshot_20251206-111754~2.png '
    }
}

EQUIPMENT_DB = {
    # ==================== 當前版本 (KPatch2 更新後) ====================
    
    # Tier I
    'hunting_dagger': {
        'name': 'Hunting Dagger',
        'tier': 'I',
        'stats': {'atk_min': 12, 'atk_max': 12},
        'special_effects': {},
        'set': 'explorer',
        'level_req': 1,
        'image_url': 'https://trello.com/1/cards/683b04d92c71047dab4be58d/attachments/68593c5534d24f23f80e31d3/download/HuntingDagger.png '
    },
    'metal_plate': {
        'name': 'Metal Plate',
        'tier': 'I',
        'stats': {'shield': 15},
        'special_effects': {},
        'level_req': 2,
        'image_url': 'https://trello.com/1/cards/68594a8c3b466d2b42de69b6/attachments/6859c80bb98fd0796959b91b/download/MetalPlate.png '
    },
    'sharpener_rock': {
        'name': 'Sharpener\'s Rock',
        'tier': 'I', 
        'stats': {'crit_chance': 5, 'crit_damage': 10},
        'special_effects': {},
        'level_req': 10,
        'image_url': 'https://trello.com/1/cards/683b0219439d534dd50d0aa8/attachments/6859c8a264ac8780568c1806/download/SharpenerRock.png '
    },
    
    # Tier II
    'ancient_hammer': {
        'name': 'Ancient Hammer',
        'tier': 'II',
        'stats': {'atk_min': 50, 'atk_max': 50},
        'special_effects': {},
        'level_req': 10,
        'image_url': 'https://trello.com/1/cards/683afec2447470817295e791/attachments/6857f35b3a934caff9e78259/download/AncientHammer.png '
    },
    'ancient_wood_armor': {
        'name': 'Ancient Wood Armor',
        'tier': 'II',
        'stats': {'health': 100, 'shield': 15},
        'special_effects': {},
        'level_req': 10,
        'image_url': ' https://trello.com/1/cards/685949bdc16253486cb46f67/attachments/68594b3a663135a3bf1597ae/download/AncientWoodArmor.png'
    },
    'copper_sword': {
        'name': 'Copper Sword',
        'tier': 'II',
        'stats': {'atk_min': 30, 'atk_max': 30},
        'special_effects': {},
        'level_req': 5,
        'image_url': 'https://trello.com/1/cards/681a05527ec25cc481366c97/attachments/6859e20ef20f9a9f7b12b4ea/download/CopperSword.png '
    },
    'dual_sword': {
        'name': 'Dual Sword',
        'tier': 'IV',
        'stats': {'atk_min': 135, 'atk_max': 149},
        'special_effects': {'double_damage_chance': 0.10},
        'level_req': 100,
        'image_url': ' https://trello.com/1/cards/6852a03969d3d5c58d5d03d6/attachments/6859e21ef738d09e1c93a601/download/DualBlades.png'
    },
    'forest_dweller_axe': {
        'name': 'Forest Dweller\'s Axe',
        'tier': 'II',
        'stats': {'atk_min': 40, 'atk_max': 40, 'crit_chance': 5},
        'special_effects': {'bleed_chance': 0.02},
        'set': 'forest_dweller',
        'level_req': 10,
        'image_url': 'https://trello.com/1/cards/68594aef34831e327f27d918/attachments/6859ca0de831ecb78bc87b1b/download/LeafAxe.png '
    },
    'volatile_crystal': {  # KPatch2 更新：45 -> 115
        'name': 'Volatile Crystal',
        'tier': 'II',
        'stats': {'magic': 115},
        'special_effects': {},
        'level_req': 5,
        'image_url': ' https://trello.com/1/cards/68a865f398d22ae285b4a7e6/attachments/68a865f398d22ae285b4a822/download/VolatileGem.png'
    },
    
    # Tier III
    'alderite_axe': {
        'name': 'Alderite Axe',
        'tier': 'III',
        'stats': {'atk_min': 175, 'atk_max': 194, 'magic': 140, 'crit_chance': 5},
        'special_effects': {},
        'level_req': 35,
        'image_url': 'https://trello.com/1/cards/68529d7d5c7008290ba7293d/attachments/6857f389557a239e98a98758/download/AlderiteAxe.png '
    },
    'aqua_crystal': {
        'name': 'Aqua Crystal',
        'tier': 'III',
        'stats': {'magic': 110},
        'special_effects': {},
        'level_req': 30,
        'image_url': 'https://trello.com/1/cards/68a87f6d2e103719805af902/attachments/68bb5d032ae88364c179c21a/download/AquaLapis.png '
    },
    'arcane_spellbook': {
        'name': 'Arcane Spellbook',
        'tier': 'III',
        'stats': {'magic': 100},
        'special_effects': {},
        'level_req': 25,
        'image_url': 'https://trello.com/1/cards/683b008e8d950fd6c81f04b0/attachments/6859e3f30087babe01744e3d/download/ArcaneSpellbook.png '
    },
    'bee_headgear': {  # KPatch2 新增的裝備
        'name': 'Bee Headgear',
        'tier': 'IV',
        'stats': {'shield': 60, 'atk_min': 200, 'atk_max': 200},
        'special_effects': {},
        'level_req': 40,
        'image_url': 'https://trello.com/1/cards/68a865ec72154620a0f15b73/attachments/68bb5c05e30e1bba81e6ae9a/download/BeeHeadgear.png '
    },
    'corrupted_fang': {
        'name': 'Corrupted Fang',
        'tier': 'III',
        'stats': {'magic': 130, 'atk_min': 35, 'atk_max': 35},
        'special_effects': {},
        'level_req': 30,
        'image_url': 'https://trello.com/1/cards/685ce6f7b02bcb9685654cfa/attachments/685ce731af78784e1fb0999b/download/CorruptedFang.png '
    },
    'daybreak': {
        'name': 'Daybreak',
        'tier': 'III',
        'stats': {'atk_min': 100, 'atk_max': 111},
        'special_effects': {'burn_chance': 0.52},
        'set': 'flame',
        'level_req': 70,
        'image_url': 'https://trello.com/1/cards/68594a12b56f28e382997c75/attachments/6859e61e9679574ae10d547a/download/FlameSword.png '
    },
    'enchanted_blade': {
        'name': 'Enchanted Blade',
        'tier': 'III',
        'stats': {'atk_min': 125, 'atk_max': 125, 'magic': 100},
        'special_effects': {},
        'level_req': 25,
        'image_url': 'https://trello.com/1/cards/683d4a3fbb9d04019cb8d51b/attachments/68439d5347b6be7e982ae545/download/image.png '
    },
    'magicians_hat': {
        'name': 'Magician\'s Hat',
        'tier': 'III',
        'stats': {'magic': 80, 'health': 30},
        'special_effects': {},
        'level_req': 25,
        'image_url': 'https://trello.com/1/cards/683d7e1c94c96f0d38398fb9/attachments/6859c879bf98faa9c13535f6/download/MagicianHat.png '
    },
    'mana_lantern': {
        'name': 'Mana Lantern',
        'tier': 'III',
        'stats': {'magic': 90},
        'special_effects': {},
        'level_req': 25,
        'image_url': 'https://trello.com/1/cards/683d7e1c94c96f0d38398fb9/attachments/6859c879bf98faa9c13535f6/download/MagicianHat.png'
    },
    
    # Tier IV
    'atlantis_armor': {
        'name': 'Atlantis Armor',
        'tier': 'IV',
        'stats': {'health': 75, 'shield': 10},
        'special_effects': {},
        'level_req': 50,
        'image_url': 'https://trello.com/1/cards/68529b3c737a3c7afda9c97b/attachments/6859e5d5e51380a8bc8cfe1c/download/AtlantisArmor.png '
    },
    'bee_breastplate': {
        'name': 'Bee Breastplate',
        'tier': 'IV',
        'stats': {'health': 460, 'shield': 40},
        'special_effects': {},
        'set': 'queen_bee',
        'level_req': 65,
        'image_url': ' https://trello.com/1/cards/682359df9736afb25a1f423b/attachments/6859e6a98d2c9a9fae9561b4/download/HoneyArmor.png'
    },
    'black_wolf_necklace': {
        'name': 'Black Wolf Necklace',
        'tier': 'IV',
        'stats': {'atk_min': 225, 'atk_max': 249, 'crit_chance': 15, 'crit_damage': 22},
        'special_effects': {},
        'set': 'wolf_howl',
        'level_req': 45,
        'image_url': 'https://trello.com/1/cards/681a05762ba7af5e4a99fa1d/attachments/6859e5ed77751a75859eecff/download/BlackWolfNecklace.png '
    },
    'blood_butcher': {
        'name': 'Blood Butcher',
        'tier': 'IV',
        'stats': {'atk_min': 250, 'atk_max': 277, 'crit_chance': 16},
        'special_effects': {'blood_butcher': True},
        'set': 'crimson',
        'level_req': 50,
        'image_url': ' https://trello.com/1/cards/6852a2eab0691a86d59e769d/attachments/6859e6e6b2fea32b021a1de9/download/CrimsoniteBlade.png'
    },
    'crimson_slime_fang': {
        'name': 'Crimson Slime Fang',
        'tier': 'IV',
        'stats': {'magic': 220, 'crit_damage': 27},
        'special_effects': {},
        'set': 'crimson',
        'level_req': 65,
        'image_url': ' https://trello.com/1/cards/681a057deb3be17e8bc026bd/attachments/68bb5d7a79e1b6dc07e6a602/download/CrimsonSlimeFang.png'
    },
    'cursed_spellbook': {
        'name': 'Cursed Spellbook',
        'tier': 'IV',
        'stats': {'magic': 400},
        'special_effects': {'damage_multiplier': 1.3},
        'set': 'crimson',
        'level_req': 100,
        'image_url': 'https://trello.com/1/cards/68529f5acab2f93890583d40/attachments/6859e655c8324d38b250fac7/download/BloodSpellbook.png '
    },
    'evernight': {  # KPatch2 更新：ATK 450→250，增加 250 Magic
        'name': 'Evernight',
        'tier': 'IV',
        'stats': {'atk_min': 250, 'atk_max': 250, 'magic': 250},
        'special_effects': {},
        'set': 'flame',
        'level_req': 100,
        'image_url': 'https://trello.com/1/cards/68a88237dcedbda58c2ccde1/attachments/68bb5d173fd32e73405c19d5/download/PerennialBloom.png '
    },
    'forest_crown': {
        'name': 'Forest Crown',
        'tier': 'IV',
        'stats': {'health': 775, 'shield': 275},
        'special_effects': {},
        'level_req': 65,
        'image_url': 'https://trello.com/1/cards/68594a22cb1930aa3b76dfdc/attachments/6859bedfc21a9b4f1210fbb8/download/ForestCrown.png '
    },
    'ghost_lantern': {
        'name': 'Ghost Lantern',
        'tier': 'III',
        'stats': {'magic': 480},
        'special_effects': {},
        'level_req': 65,
        'image_url': ' https://trello.com/1/cards/690379feae36ff694060866b/attachments/69037c5c3f138dd4acc72c6c/download/Screenshot_20251030-145405~2.png'
    },
    'kitsune_gloves': {  # KPatch2 更新：屬性提升，階級和等級提高
        'name': 'Kitsune Gloves',
        'tier': 'IV',
        'stats': {'crit_damage': 50, 'magic': 125, 'atk_min': 125, 'atk_max': 125},
        'special_effects': {},
        'level_req': 65,
        'image_url': 'https://trello.com/1/cards/68c2cf52e9b086cb83aaa083/attachments/69037dceb8075acf01b01c96/download/Screenshot_20251030-150018~2.png '
    },
    'slime_crown': {  # KPatch2 更新：HP 200→1125，增加 200 ATK
        'name': 'Slime Crown',
        'tier': 'IV',
        'stats': {'health': 1125, 'shield': 50, 'atk_min': 200, 'atk_max': 200},
        'special_effects': {},
        'level_req': 35,
        'image_url': 'https://trello.com/1/cards/68594acfe81e32098ab1cbb5/attachments/6859c9b0f93fb61adbdcb1c6/download/KingSlimeCrown.png '
    },
    'volcanic_axe': {
        'name': 'Volcanic Axe',
        'tier': 'IV',
        'stats': {'atk_min': 280, 'atk_max': 280},
        'special_effects': {'burn_chance': 0.05},
        'set': 'wolf_howl',
        'level_req': 65,
        'image_url': ' https://trello.com/1/cards/68c2d8a5787843e5ac524ba9/attachments/69020d28c213a489fd5917f3/download/Screenshot_20251029-124319_2-removebg-preview.png'
    },
    'winter_spirit': {
        'name': 'Winter Spirit',
        'tier': 'IV',
        'stats': {'atk_min': 200, 'atk_max': 200, 'health': 50},
        'special_effects': {'freeze_chance': 0.02},
        'level_req': 65,
        'image_url': ' https://trello.com/1/cards/68c2d8a2dfbf39178d6820b3/attachments/69020e605c3d247d249d7a61/download/Screenshot_20251029-125140_2-removebg-preview.png'
    },
    
    # Tier V
    'queenbee_crown': {
        'name': 'Queen Bee\'s Crown',
        'tier': 'V',
        'stats': {'atk_min': 800, 'atk_max': 888, 'crit_chance': 20, 'crit_damage': 80},
        'special_effects': {'bleed_chance': 0.26},
        'set': 'queen_bee',
        'level_req': 150,
        'image_url': 'https://trello.com/1/cards/685e44b7aaf0b09fd78f3215/attachments/685f3a448f4e2823beb572da/download/QueenBeeCrown.png '
    },
    'volatile_gem': {  # KPatch2 更新：增加 10% Bleed Chance
        'name': 'Volatile Gem',
        'tier': 'V',
        'stats': {'magic': 315},
        'special_effects': {
            'burn_chance': 0.11,
            'poison_chance': 0.11,
            'dot_bonus': 0.20,
            'bleed_chance': 0.10  # 新增 10% 流血機率
        },
        'set': 'flame',
        'level_req': 150,
        'image_url': ' https://trello.com/1/cards/68594af20d38a03c0bd148c2/attachments/6859ca1779e348a39f379352/download/VolatileGem.png'
    },
    
    # Mana-Focused Passives
    'mana_crystal': {
        'name': 'Mana Crystal',
        'tier': 'II',
        'stats': {'magic': 25},
        'special_effects': {},
        'level_req': 5,
        'image_url': ' https://trello.com/1/cards/681a05844dd524b6aeb5e28d/attachments/6859e238166b29d93693cc8a/download/ManaCrystal.png'
    },
    
    # ==================== 舊版裝備 (KPatch1) - 只針對有改動的裝備 ====================
   
    # Kitsune Gloves 舊版
    'kitsune_gloves_old': {
        'name': 'Kitsune Gloves (Old)',
        'tier': 'III',
        'stats': {'crit_damage': 10, 'magic': 100, 'atk_min': 100, 'atk_max': 100},  # 舊版屬性
        'special_effects': {},
        'level_req': 45,
        'is_old': True,
        'image_url': 'https://trello.com/1/cards/68c2cf52e9b086cb83aaa083/attachments/69037dceb8075acf01b01c96/download/Screenshot_20251030-150018~2.png'
    }
}