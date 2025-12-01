# Weapon Database with level requirements
WEAPON_DB = {
    'furioso': {
        'name': 'Furioso',
        'type': 'furioso',
        'stats': {'atk_min': 350, 'atk_max': 350},
        'level_req': 50
    },
    'wooden_sword': {
        'name': 'Wooden Sword',
        'type': 'sword',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'set': 'blessing',
        'level_req': 1
    },
    'wooden_staff': {
        'name': 'Wooden Staff', 
        'type': 'staff',
        'stats': {'magic': 4},
        'set': 'blessing',
        'level_req': 1
    },
    'wooden_bow': {
        'name': 'Wooden Bow',
        'type': 'bow', 
        'stats': {'atk_min': 5, 'atk_max': 5},
        'set': 'blessing',
        'level_req': 1
    },
    'divine_blade': {
        'name': 'Divine Blade',
        'type': 'sword',
        'stats': {'atk_min': 75, 'atk_max': 83},
        'set': 'explorer',
        'level_req': 15
    },
    'forest_dweller_staff': {
        'name': 'Forest Dweller\'s Staff',
        'type': 'staff',
        'stats': {'magic': 60},
        'set': 'explorer',
        'level_req': 15
    },
    'forest_dweller_bow': {
        'name': 'Forest Dweller\'s Bow',
        'type': 'bow',
        'stats': {'atk_min': 75, 'atk_max': 83},
        'set': 'explorer',
        'level_req': 15
    },
    'crescendo_scythe': {
        'name': 'Crescendo Scythe',
        'type': 'scythe',
        'stats': {'atk_min': 75, 'atk_max': 75},
        'set': 'library_ruina',
        'level_req': 15
    },
    'emerald_staff': {
        'name': 'Emerald Staff',
        'type': 'staff', 
        'stats': {'magic': 500},
        'level_req': 65
    },
    'winter_howl': {
        'name': 'Winter Howl',
        'type': 'sword',
        'stats': {'atk_min': 325, 'atk_max': 360},
        'set': 'wolf_howl',
        'level_req': 65
    },
    'eventide': {
        'name': 'Eventide',
        'type': 'bow',
        'stats': {'atk_min': 325, 'atk_max': 360},
        'set': 'queen_bee',
        'level_req': 65
    }
}

EQUIPMENT_DB = {
    # Tier I
    'burning_torch': {
        'name': 'Burning Torch',
        'tier': 'I',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'special_effects': {},
        'level_req': 1
    },
    'climbing_hook': {
        'name': 'Climbing Hook',
        'tier': 'I',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'special_effects': {},
        'level_req': 1
    },
    'hunting_dagger': {
        'name': 'Hunting Dagger',
        'tier': 'I',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'special_effects': {},
        'set': 'explorer',
        'level_req': 1
    },
    'lantern': {
        'name': 'Lantern',
        'tier': 'I',
        'stats': {'magic': 5},
        'special_effects': {},
        'level_req': 5
    },
    'metal_plate': {
        'name': 'Metal Plate',
        'tier': 'I',
        'stats': {'shield': 10},
        'special_effects': {},
        'level_req': 2
    },
    'mining_pickaxe': {
        'name': 'Mining Pickaxe',
        'tier': 'I',
        'stats': {'atk_min': 5, 'atk_max': 5},
        'special_effects': {},
        'level_req': 1
    },
    'rabbits_foot': {
        'name': 'Rabbit\'s Foot',
        'tier': 'I',
        'stats': {'crit_chance': 3},
        'special_effects': {},
        'level_req': 5
    },
    'sharpener_rock': {
        'name': 'Sharpener\'s Rock',
        'tier': 'I', 
        'stats': {'crit_chance': 5, 'crit_damage': 10},
        'special_effects': {},
        'level_req': 10
    },
    'travellers_boots': {
        'name': 'Traveller\'s Boots',
        'tier': 'I',
        'stats': {'health': 20},
        'special_effects': {},
        'level_req': 1
    },
    
    # Tier II
    'adventurers_kit': {
        'name': 'Adventurer\'s Kit',
        'tier': 'II',
        'stats': {'health': 50, 'shield': 10},
        'special_effects': {},
        'level_req': 25
    },
    'ancient_hammer': {
        'name': 'Ancient Hammer',
        'tier': 'II',
        'stats': {'atk_min': 50, 'atk_max': 50},
        'special_effects': {},
        'level_req': 10
    },
    'ancient_wood_armor': {
        'name': 'Ancient Wood Armor',
        'tier': 'II',
        'stats': {'health': 80, 'shield': 15},
        'special_effects': {},
        'level_req': 10
    },
    'copper_sword': {
        'name': 'Copper Sword',
        'tier': 'II',
        'stats': {'atk_min': 30, 'atk_max': 30},
        'special_effects': {},
        'level_req': 5
    },
    'dual_sword': {
        'name': 'Dual Sword',
        'tier': 'IV',
        'stats': {'atk_min': 135, 'atk_max': 149},
        'special_effects': {'double_damage_chance': 0.15},
        'level_req': 100
    },
    'forest_dweller_axe': {
        'name': 'Forest Dweller\'s Axe',
        'tier': 'II',
        'stats': {'atk_min': 40, 'atk_max': 40, 'crit_chance': 5},
        'special_effects': {'bleed_chance': 0.02},
        'set': 'forest_dweller',
        'level_req': 10
    },
    'volatile_crystal': {
        'name': 'Volatile Crystal',
        'tier': 'II',
        'stats': {'magic': 45},
        'special_effects': {},
        'level_req': 5
    },
    
    # Tier III
    'alderite_axe': {
        'name': 'Alderite Axe',
        'tier': 'III',
        'stats': {'atk_min': 175, 'atk_max': 194, 'magic': 140, 'crit_chance': 5},
        'special_effects': {},
        'level_req': 35
    },
    'aqua_crystal': {
        'name': 'Aqua Crystal',
        'tier': 'III',
        'stats': {'magic': 110},
        'special_effects': {},
        'level_req': 30
    },
    'arcane_spellbook': {
        'name': 'Arcane Spellbook',
        'tier': 'III',
        'stats': {'magic': 100},
        'special_effects': {},
        'level_req': 25
    },
    'corrupted_fang': {
        'name': 'Corrupted Fang',
        'tier': 'III',
        'stats': {'magic': 130, 'atk_min': 35, 'atk_max': 35},
        'special_effects': {},
        'level_req': 30
    },
    'daybreak': {
        'name': 'Daybreak',
        'tier': 'III',
        'stats': {'atk_min': 100, 'atk_max': 111},
        'special_effects': {'burn_chance': 0.52},
        'set': 'flame',
        'level_req': 70
    },
    'enchanted_blade': {
        'name': 'Enchanted Blade',
        'tier': 'III',
        'stats': {'atk_min': 125, 'atk_max': 125, 'magic': 100},
        'special_effects': {},
        'level_req': 25
    },
    'magicians_hat': {
        'name': 'Magician\'s Hat',
        'tier': 'III',
        'stats': {'magic': 80, 'health': 30},
        'special_effects': {},
        'level_req': 25
    },
    'mana_lantern': {
        'name': 'Mana Lantern',
        'tier': 'III',
        'stats': {'magic': 90},
        'special_effects': {},
        'level_req': 25
    },
    
    # Tier IV
    'atlantis_armor': {
        'name': 'Atlantis Armor',
        'tier': 'IV',
        'stats': {'health': 75, 'shield': 10},
        'special_effects': {},
        'level_req': 50
    },
    'bee_breastplate': {
        'name': 'Bee Breastplate',
        'tier': 'IV',
        'stats': {'health': 460, 'shield': 40},
        'special_effects': {},
        'set': 'queen_bee',
        'level_req': 65
    },
    'black_wolf_necklace': {
        'name': 'Black Wolf Necklace',
        'tier': 'IV',
        'stats': {'atk_min': 225, 'atk_max': 249, 'crit_chance': 15, 'crit_damage': 22},
        'special_effects': {},
        'set': 'wolf_howl',
        'level_req': 45
    },
    'blood_butcher': {
        'name': 'Blood Butcher',
        'tier': 'IV',
        'stats': {'atk_min': 250, 'atk_max': 277, 'crit_chance': 16},
        'special_effects': {'blood_butcher': True},
        'set': 'crimson',
        'level_req': 50
    },
    'crimson_slime_fang': {
        'name': 'Crimson Slime Fang',
        'tier': 'IV',
        'stats': {'magic': 220, 'crit_damage': 27},
        'special_effects': {},
        'set': 'crimson',
        'level_req': 65
    },
    'cursed_spellbook': {
        'name': 'Cursed Spellbook',
        'tier': 'IV',
        'stats': {'magic': 400},
        'special_effects': {'damage_multiplier': 1.3},
        'set': 'crimson',
        'level_req': 100
    },
    'evernight': {
        'name': 'Evernight',
        'tier': 'IV',
        'stats': {'atk_min': 450, 'atk_max': 450},
        'special_effects': {'burn_chance': 0.40},
        'set': 'flame',
        'level_req': 100
    },
    'forest_crown': {
        'name': 'Forest Crown',
        'tier': 'IV',
        'stats': {'health': 775, 'shield': 275},
        'special_effects': {},
        'level_req': 65
    },
    'ghost_lantern': {
        'name': 'Ghost Lantern',
        'tier': 'IV',
        'stats': {'magic': 480},
        'special_effects': {},
        'level_req': 65
    },
    'slime_crown': {
        'name': 'Slime Crown',
        'tier': 'IV',
        'stats': {'health': 200, 'shield': 50},
        'special_effects': {},
        'level_req': 35
    },
    'volcanic_axe': {
        'name': 'Volcanic Axe',
        'tier': 'IV',
        'stats': {'atk_min': 280, 'atk_max': 280},
        'special_effects': {'burn_chance': 0.05},
        'set': 'wolf_howl',
        'level_req': 65
    },
    'winter_spirit': {
        'name': 'Winter Spirit',
        'tier': 'IV',
        'stats': {'atk_min': 200, 'atk_max': 200, 'health': 50},
        'special_effects': {'freeze_chance': 0.02},
        'level_req': 65
    },
    
    # Tier V
    'queenbee_crown': {
        'name': 'Queen Bee\'s Crown',
        'tier': 'V',
        'stats': {'atk_min': 800, 'atk_max': 888, 'crit_chance': 20, 'crit_damage': 80},
        'special_effects': {'bleed_chance': 0.26},
        'set': 'queen_bee',
        'level_req': 150
    },
    'volatile_gem': {
        'name': 'Volatile Gem',
        'tier': 'V',
        'stats': {'magic': 315},
        'special_effects': {
            'burn_chance': 0.11,
            'poison_chance': 0.11,
            'dot_bonus': 0.20
        },
        'set': 'flame',
        'level_req': 150
    },
    
    # Mana-Focused Passives
    'mana_crystal': {
        'name': 'Mana Crystal',
        'tier': 'II',
        'stats': {'magic': 25},
        'special_effects': {},
        'level_req': 5
    },
    'aqua_lapis': {
        'name': 'Aqua Lapis',
        'tier': 'III',
        'stats': {'magic': 70},
        'special_effects': {},
        'level_req': 30
    }
}
