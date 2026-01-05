"""
Critical Fantasy Damage Calculator
Copyright (C) 2024  @tux_koh

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
import math
from itertools import combinations
from data import EQUIPMENT_DB, WEAPON_DB
from image import ImageGenerator
from datetime import datetime
import io
import os
import tempfile
import random

app = Flask(__name__)

# 添加自定义过滤器
@app.template_filter('format_number')
def format_number_filter(value):
    """格式化数字为带逗号的字符串"""
    try:
        if isinstance(value, (int, float)):
            return f"{int(value):,}"
        else:
            return str(value)
    except:
        return str(value)

# ================ Configuration Constants ================
MAX_LEVEL = 200
# ========================================================

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

class DamageCalculator:
    # ... 保持原有的 DamageCalculator 类不变 ...
    # (所有原有的计算方法保持不变)
    
    STR_DMG_MIN = 2.4
    STR_DMG_MAX = 7.5
    INT_MAGIC = 8.0
    VIT_HP = 75
    BASE_HP = 100
    DEF_SHIELD = 17
    DEX_CRIT = 0.8
    BASE_CRIT_RATE = 1.0
    BASE_CRIT_DAMAGE = 100
    MAX_DEX_CRIT = 50 * DEX_CRIT
    
    BASE_MIN_ATK = 8
    BASE_MAX_ATK = 15
    BASE_MAGIC = 10
    
    MAX_CLASS_LEVEL = 15
    CLASS_LEVEL_MULTIPLIER_PER_LEVEL = 0.02
    BASE_CLASS_LEVEL_MULTIPLIER = 1.0
    
    @staticmethod
    def calculate_class_multiplier(class_level):
        if class_level < 1:
            return DamageCalculator.BASE_CLASS_LEVEL_MULTIPLIER + DamageCalculator.CLASS_LEVEL_MULTIPLIER_PER_LEVEL
        
        effective_level = max(1, min(class_level, DamageCalculator.MAX_CLASS_LEVEL))
        return DamageCalculator.BASE_CLASS_LEVEL_MULTIPLIER + (effective_level * DamageCalculator.CLASS_LEVEL_MULTIPLIER_PER_LEVEL)
    
    @staticmethod
    def calculate_max_points(level):
        return level * 2
    
    @staticmethod
    def calculate_equipment_bonus(equipment_data):
        bonuses = {
            'atk_min': 0,
            'atk_max': 0,
            'magic': 0,
            'crit_chance': 0,
            'crit_damage': 0,
            'health': 0,
            'shield': 0
        }
        
        stats = equipment_data.get('stats', {})
        
        if 'atk_min' in stats and 'atk_max' in stats:
            drop_min = stats['atk_min']
            drop_max = stats['atk_max']
            middle_value = (drop_min + drop_max) / 2
            
            bonuses['atk_min'] = middle_value * 0.85
            bonuses['atk_max'] = middle_value * 1.25
        
        if 'magic' in stats:
            bonuses['magic'] = stats['magic']
        
        if 'crit_chance' in stats:
            bonuses['crit_chance'] = stats['crit_chance']
        if 'crit_damage' in stats:
            bonuses['crit_damage'] = stats['crit_damage']
        if 'health' in stats:
            bonuses['health'] = stats['health']
        if 'shield' in stats:
            bonuses['shield'] = stats['shield']
            
        return bonuses
    
    @staticmethod
    def calculate_stats_from_points(strength, vitality, intelligence, dexterity, defense, level):
        effective_dex_crit = min(dexterity, 50) * DamageCalculator.DEX_CRIT
        
        return {
            'min_damage': strength * DamageCalculator.STR_DMG_MIN + DamageCalculator.BASE_MIN_ATK,
            'max_damage': strength * DamageCalculator.STR_DMG_MAX + DamageCalculator.BASE_MAX_ATK,
            'health': DamageCalculator.BASE_HP + vitality * DamageCalculator.VIT_HP,
            'magic_damage': intelligence * DamageCalculator.INT_MAGIC + DamageCalculator.BASE_MAGIC,
            'crit_chance': DamageCalculator.BASE_CRIT_RATE + effective_dex_crit,
            'crit_damage': DamageCalculator.BASE_CRIT_DAMAGE,
            'shield': defense * DamageCalculator.DEF_SHIELD
        }
    
    @staticmethod
    def calculate_ten_second_damage(base_damage, dot_damage, weapon_type, expected_damage):
        base_damage_per_hit = expected_damage
        dot_damage_per_hit = dot_damage
        
        if weapon_type == 'staff':
            total_base_damage = base_damage_per_hit * 7
            total_dot_damage = dot_damage_per_hit * 4
            total_damage = total_base_damage + total_dot_damage
            
            return {
                'hit_1': base_damage_per_hit + dot_damage_per_hit,
                'hit_2': base_damage_per_hit + dot_damage_per_hit,
                'hit_3': base_damage_per_hit + dot_damage_per_hit,
                'hit_4': base_damage_per_hit + dot_damage_per_hit,
                'total_damage': total_damage,
                'mechanic': 'Flow: 7x total damage in 10 seconds (4 hits)'
            }
        
        elif weapon_type == 'bow':
            total_base_damage = base_damage_per_hit * 7
            total_dot_damage = dot_damage_per_hit * 4
            total_damage = total_base_damage + total_dot_damage
            
            return {
                'hit_1': base_damage_per_hit + dot_damage_per_hit,
                'hit_2': base_damage_per_hit + dot_damage_per_hit,
                'hit_3': base_damage_per_hit + dot_damage_per_hit,
                'hit_4': base_damage_per_hit + dot_damage_per_hit,
                'total_damage': total_damage,
                'mechanic': 'Brust: 7x total damage in 10 seconds (4 hits)'
            }
        
        elif weapon_type in ['sword', 'blade']:
            total_base_damage = base_damage_per_hit * 10
            total_dot_damage = dot_damage_per_hit * 4
            total_damage = total_base_damage + total_dot_damage
            
            return {
                'hit_1': base_damage_per_hit + dot_damage_per_hit,
                'hit_2': base_damage_per_hit + dot_damage_per_hit,
                'hit_3': base_damage_per_hit + dot_damage_per_hit,
                'hit_4': base_damage_per_hit + dot_damage_per_hit,
                'total_damage': total_damage,
                'mechanic': 'Chain: 10x total damage in 10 seconds (4 hits)'
            }
        
        elif weapon_type == 'scythe':
            total_base_damage = base_damage_per_hit * 4.8
            total_dot_damage = dot_damage_per_hit * 4
            total_damage = total_base_damage + total_dot_damage
            
            return {
                'hit_1': base_damage_per_hit + dot_damage_per_hit,
                'hit_2': base_damage_per_hit + dot_damage_per_hit,
                'hit_3': base_damage_per_hit + dot_damage_per_hit,
                'hit_4': base_damage_per_hit + dot_damage_per_hit,
                'total_damage': total_damage,
                'mechanic': 'Reverberation: 4.8x total damage in 10 seconds (4 hits)'
            }
        
        elif weapon_type == 'furioso':
            total_base_damage = base_damage_per_hit * 3.7
            total_dot_damage = dot_damage_per_hit * 4
            total_damage = total_base_damage + total_dot_damage
            
            return {
                'hit_1': base_damage_per_hit + dot_damage_per_hit,
                'hit_2': base_damage_per_hit + dot_damage_per_hit,
                'hit_3': base_damage_per_hit + dot_damage_per_hit,
                'hit_4': base_damage_per_hit + dot_damage_per_hit,
                'hit_5': base_damage_per_hit + dot_damage_per_hit,
                'total_damage': total_damage,
                'mechanic': 'Furioso: 3.7x total damage + bleed on 4th hit in 10 seconds (4 hits)'
            }
        
        else:
            total_base_damage = base_damage_per_hit * 4
            total_dot_damage = dot_damage_per_hit * 4
            total_damage = total_base_damage + total_dot_damage
            
            return {
                'hit_1': base_damage_per_hit + dot_damage_per_hit,
                'hit_2': base_damage_per_hit + dot_damage_per_hit,
                'hit_3': base_damage_per_hit + dot_damage_per_hit,
                'hit_4': base_damage_per_hit + dot_damage_per_hit,
                'total_damage': total_damage,
                'mechanic': 'Default: 4x damage in 10 seconds (4 hits)'
            }
    
    @staticmethod
    def calculate_damage(data):
        try:
            use_old_version = data.get('useOldVersion', False)
            
            class_level = int(data.get('classLevel', 15))
            class_multiplier = DamageCalculator.calculate_class_multiplier(class_level)
            
            use_point_system = data.get('usePointSystem', False)
            selected_weapon = data.get('selectedWeapon', '')
            player_level = data.get('playerLevel', MAX_LEVEL)
            
            if selected_weapon:
                weapon_data = WEAPON_DB.get(selected_weapon, {})
                damage_type = 'magic' if weapon_data.get('type') == 'staff' else 'attack'
            else:
                damage_type = 'attack'
            
            set_counts = {
                'flame': 0,
                'wolf_howl': 0,
                'crimson': 0,
                'queen_bee': 0,
                'explorer': 0,
                'forest_dweller': 0,
                'library_ruina': 0,
                'blessing': 0
            }
            
            equipment_health_bonus = 0
            
            if use_point_system:
                strength = int(data.get('strength', 0))
                vitality = int(data.get('vitality', 0))
                intelligence = int(data.get('intelligence', 0))
                dexterity = int(data.get('dexterity', 0))
                defense = int(data.get('defense', 0))
                
                base_stats = DamageCalculator.calculate_stats_from_points(
                    strength, vitality, intelligence, dexterity, defense, player_level
                )
                
                min_damage = base_stats['min_damage']
                max_damage = base_stats['max_damage']
                magic_damage = base_stats['magic_damage']
                base_crit_rate = base_stats['crit_chance']
                base_crit_damage = base_stats['crit_damage']
                base_health = base_stats['health']
                base_shield = base_stats['shield']
                
                if selected_weapon:
                    weapon_data = WEAPON_DB.get(selected_weapon, {})
                    weapon_bonus = DamageCalculator.calculate_equipment_bonus(weapon_data)
                    
                    min_damage += weapon_bonus['atk_min']
                    max_damage += weapon_bonus['atk_max']
                    magic_damage += weapon_bonus['magic']
                    base_crit_rate += weapon_bonus['crit_chance']
                    base_crit_damage += weapon_bonus['crit_damage']
                    equipment_health_bonus += weapon_bonus['health']
                    
                    if weapon_data.get('set'):
                        set_counts[weapon_data['set']] += 1
                
                avg_physical_damage = (min_damage + max_damage) / 2
                
            else:
                min_damage = float(data.get('minDamage', 0)) or DamageCalculator.BASE_MIN_ATK
                max_damage = float(data.get('maxDamage', 0)) or DamageCalculator.BASE_MAX_ATK
                magic_damage = float(data.get('magicDamage', 0)) or DamageCalculator.BASE_MAGIC
                base_crit_rate = float(data.get('critRate', DamageCalculator.BASE_CRIT_RATE))
                base_crit_damage = float(data.get('critDamage', DamageCalculator.BASE_CRIT_DAMAGE))
                base_health = 0
                base_shield = 0
                
                if selected_weapon:
                    weapon_data = WEAPON_DB.get(selected_weapon, {})
                    if weapon_data.get('set'):
                        set_counts[weapon_data['set']] += 1
                
                avg_physical_damage = (min_damage + max_damage) / 2
            
            has_magic_potion = data.get('magicPotion', False)
            has_attack_potion = data.get('attackPotion', False)
            has_golden_apple = data.get('goldenApple', False)
            
            equipment = data.get('equipment', [])
            
            total_crit_rate = base_crit_rate
            total_crit_damage = base_crit_damage
            
            for eq in equipment:
                eq_data = EQUIPMENT_DB.get(eq, {})
                
                if use_point_system:
                    eq_bonus = DamageCalculator.calculate_equipment_bonus(eq_data)
                    
                    min_damage += eq_bonus['atk_min']
                    max_damage += eq_bonus['atk_max']
                    magic_damage += eq_bonus['magic']
                    total_crit_rate += eq_bonus['crit_chance']
                    total_crit_damage += eq_bonus['crit_damage']
                    equipment_health_bonus += eq_bonus['health']
                
                if eq_data.get('set'):
                    set_counts[eq_data['set']] += 1
            
            if use_point_system:
                avg_physical_damage = (min_damage + max_damage) / 2
            
            effective_min_damage = min_damage
            effective_max_damage = max_damage
            effective_avg_physical_damage = avg_physical_damage
            effective_magic_damage = magic_damage
            
            attack_multiplier = 1.0
            if has_attack_potion:
                attack_multiplier += 0.75
            if has_golden_apple:
                attack_multiplier += 0.50
            
            if attack_multiplier > 1.0:
                effective_min_damage *= attack_multiplier
                effective_max_damage *= attack_multiplier
                effective_avg_physical_damage *= attack_multiplier
            
            if has_magic_potion:
                effective_magic_damage *= 1.75
            
            set_bonus_applied = {
                'wolf_howl': False,
                'crimson': False,
                'forest_dweller': False,
                'explorer': False,
                'flame': False
            }
            
            if set_counts['wolf_howl'] >= 2:
                total_crit_rate += 12
                set_bonus_applied['wolf_howl'] = True
            
            if set_counts['crimson'] >= 2:
                effective_magic_damage *= 1.18
                set_bonus_applied['crimson'] = True
            
            if set_counts['forest_dweller'] >= 2 and damage_type == 'attack':
                effective_min_damage *= 1.18
                effective_max_damage *= 1.18
                effective_avg_physical_damage *= 1.18
                set_bonus_applied['forest_dweller'] = True
            
            if set_counts['explorer'] >= 2:
                set_bonus_applied['explorer'] = True
            
            if damage_type == 'magic':
                base_damage = effective_magic_damage
                crit_base_damage = base_damage
            else:
                base_damage = effective_avg_physical_damage
                crit_base_damage = effective_max_damage
            
            crit_rate = min(total_crit_rate / 100, 1.0)
            crit_damage_multiplier = 1 + (total_crit_damage / 100)
            
            expected_non_crit_damage = base_damage * (1 - crit_rate)
            expected_crit_damage = crit_base_damage * crit_damage_multiplier * crit_rate
            expected_damage = expected_non_crit_damage + expected_crit_damage
            
            damage_after_crit = crit_base_damage * crit_damage_multiplier
            
            total_damage = expected_damage * class_multiplier
            damage_after_crit = damage_after_crit * class_multiplier
            
            dot_damage = 0
            has_cursed_spellbook = 'cursed_spellbook' in equipment
            has_dual_sword = 'dual_sword' in equipment
            
            if has_cursed_spellbook:
                total_damage *= 1.30
                damage_after_crit *= 1.30
            
            if has_dual_sword:
                dual_sword_multiplier = 1 + (0.15 * (2 - 1))
                total_damage *= dual_sword_multiplier
                damage_after_crit *= dual_sword_multiplier
            
            flame_set_count = set_counts['flame']
            burn_chance = 0
            bleed_chance = 0
            poison_chance = 0
            has_volatile_gem = False
            
            flame_items = ['daybreak', 'evernight', 'volatile_gem']
            flame_old_items = ['daybreak_old', 'evernight_old', 'volatile_gem_old']
            
            if use_old_version:
                items_to_check = flame_old_items
            else:
                items_to_check = flame_items
            
            for item in equipment:
                if item in items_to_check or (use_old_version and item in flame_items):
                    eq_data = EQUIPMENT_DB.get(item, {})
                    special_effects = eq_data.get('special_effects', {})
                    
                    if item in ['daybreak', 'daybreak_old']:
                        burn_chance += special_effects.get('burn_chance', 0.52)
                    elif item in ['evernight', 'evernight_old']:
                        burn_chance += special_effects.get('burn_chance', 0.40)
                    elif item in ['volatile_gem', 'volatile_gem_old']:
                        burn_chance += special_effects.get('burn_chance', 0.11)
                        poison_chance += special_effects.get('poison_chance', 0.11)
                        has_volatile_gem = True
            
            if flame_set_count >= 2:
                burn_chance += 0.10
                set_bonus_applied['flame'] = True
            
            if 'queenbee_crown' in equipment or 'queenbee_crown_old' in equipment:
                eq_id = 'queenbee_crown_old' if 'queenbee_crown_old' in equipment else 'queenbee_crown'
                eq_data = EQUIPMENT_DB.get(eq_id, {})
                special_effects = eq_data.get('special_effects', {})
                bleed_chance += special_effects.get('bleed_chance', 0.26)
            
            if 'volatile_gem' in equipment and not use_old_version:
                bleed_chance += 0.10
            
            final_burn_chance = min(burn_chance, 1) * 100
            final_bleed_chance = min(bleed_chance, 1) * 100
            final_poison_chance = min(poison_chance, 1) * 100
            
            if burn_chance > 0:
                burn_damage = effective_magic_damage * 0.33 * 5
                if has_volatile_gem:
                    burn_damage += effective_magic_damage * 0.20
                dot_damage += burn_damage * min(burn_chance, 1)
            
            if bleed_chance > 0:
                bleeding_damage = effective_avg_physical_damage * 0.25 * 5
                dot_damage += bleeding_damage * min(bleed_chance, 1)
            
            if poison_chance > 0:
                poison_damage = effective_magic_damage * 0.40 * 5
                poison_damage += effective_magic_damage * 0.20
                dot_damage += poison_damage * min(poison_chance, 1)
            
            has_blood_butcher = 'blood_butcher' in equipment or 'blood_butcher_old' in equipment
            if has_blood_butcher:
                blood_damage = effective_min_damage * 0.05 * 9
                dot_damage += blood_damage
            
            final_damage = total_damage + dot_damage
            
            weapon_type = WEAPON_DB.get(selected_weapon, {}).get('type', 'sword') if selected_weapon else 'sword'
            ten_second_data = DamageCalculator.calculate_ten_second_damage(
                base_damage, dot_damage, weapon_type, total_damage
            )
            
            total_health = 0
            total_shield = 0
            total_hp = 0
            
            if use_point_system:
                total_health = base_health + equipment_health_bonus
                total_shield = base_shield
                
                explorer_hp_bonus = 200 if set_counts['explorer'] >= 2 else 0
                total_health += explorer_hp_bonus
                
                total_hp = total_health + total_shield
            
            calculation_details = {
                'class_level': {
                    'level': class_level,
                    'multiplier': class_multiplier
                },
                'base_stats': {
                    'min_damage': min_damage,
                    'max_damage': max_damage,
                    'magic_damage': magic_damage,
                    'base_crit_rate': base_crit_rate,
                    'base_crit_damage': base_crit_damage
                },
                'after_equipment': {
                    'min_damage': min_damage,
                    'max_damage': max_damage,
                    'magic_damage': magic_damage,
                    'total_crit_rate': total_crit_rate,
                    'total_crit_damage': total_crit_damage
                },
                'after_potions': {
                    'effective_min_damage': effective_min_damage,
                    'effective_max_damage': effective_max_damage,
                    'effective_magic_damage': effective_magic_damage
                },
                'set_bonuses': set_bonus_applied,
                'crit_calculation': {
                    'crit_rate_percent': crit_rate * 100,
                    'crit_damage_multiplier': crit_damage_multiplier,
                    'crit_base_damage': crit_base_damage,
                    'expected_non_crit_damage': expected_non_crit_damage,
                    'expected_crit_damage': expected_crit_damage,
                    'expected_damage': expected_damage,
                    'damage_after_crit': damage_after_crit
                },
                'dot_calculation': {
                    'burn_chance': final_burn_chance,
                    'bleed_chance': final_bleed_chance,
                    'poison_chance': final_poison_chance,
                    'has_blood_butcher': has_blood_butcher,
                    'burn_damage': burn_damage if burn_chance > 0 else 0,
                    'bleeding_damage': bleeding_damage if bleed_chance > 0 else 0,
                    'poison_damage': poison_damage if poison_chance > 0 else 0
                }
            }
            
            result = {
                'success': True,
                'use_point_system': use_point_system,
                'class_level': class_level,
                'class_multiplier': round(class_multiplier, 3),
                'min_damage': round(min_damage, 2),
                'max_damage': round(max_damage, 2),
                'magic_damage': round(magic_damage, 2),
                'avg_physical_damage': round(avg_physical_damage, 2),
                'effective_min_damage': round(effective_min_damage, 2),
                'effective_max_damage': round(effective_max_damage, 2),
                'effective_avg_physical_damage': round(effective_avg_physical_damage, 2),
                'effective_magic_damage': round(effective_magic_damage, 2),
                'base_damage': round(base_damage, 2),
                'expected_damage': round(expected_damage, 2),
                'damage_after_crit': round(damage_after_crit, 2),
                'crit_multiplied_damage': round(total_damage, 2),
                'dot_damage': round(dot_damage, 2),
                'final_damage': round(final_damage, 2),
                'effective_multiplier': round(final_damage / base_damage, 2) if base_damage > 0 else 0,
                'crit_rate': round(total_crit_rate, 1),
                'crit_damage': round(total_crit_damage, 1),
                'burn_chance': round(final_burn_chance, 1),
                'bleed_chance': round(final_bleed_chance, 1),
                'poison_chance': round(final_poison_chance, 1),
                'has_blood_butcher': has_blood_butcher,
                'flame_set_count': flame_set_count,
                'damage_type': damage_type,
                'set_counts': set_counts,
                'set_bonuses_applied': set_bonus_applied,
                'potion_effects': {
                    'magic_potion': has_magic_potion,
                    'attack_potion': has_attack_potion,
                    'golden_apple': has_golden_apple,
                    'attack_multiplier': round(attack_multiplier, 2)
                },
                'calculated_stats': use_point_system,
                'ten_second_damage': {
                    'hit_1': round(ten_second_data['hit_1'], 2),
                    'hit_2': round(ten_second_data['hit_2'], 2),
                    'hit_3': round(ten_second_data['hit_3'], 2),
                    'hit_4': round(ten_second_data.get('hit_4', 0), 2),
                    'hit_5': round(ten_second_data.get('hit_5', 0), 2),
                    'total_damage': round(ten_second_data['total_damage'], 2),
                    'mechanic': ten_second_data['mechanic']
                },
                'calculation_details': calculation_details,
                'version': 'old' if use_old_version else 'current'
            }
            
            if use_point_system:
                result['player_stats'] = {
                    'health': total_health,
                    'shield': total_shield,
                    'total_hp': total_hp,
                    'min_damage': effective_min_damage,
                    'max_damage': effective_max_damage,
                    'magic_damage': effective_magic_damage,
                    'crit_rate': total_crit_rate,
                    'crit_damage': total_crit_damage,
                    'attack_multiplier': round(attack_multiplier, 2)
                }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

def is_mobile_device(user_agent):
    mobile_keywords = [
        'mobile', 'android', 'iphone', 'ipad', 'ipod', 
        'blackberry', 'webos', 'windows phone', 'kindle'
    ]
    user_agent = user_agent.lower()
    return any(keyword in user_agent for keyword in mobile_keywords)

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = is_mobile_device(user_agent)
    
    return render_template('index.html', 
                         equipment_db=EQUIPMENT_DB, 
                         weapon_db=WEAPON_DB,
                         is_mobile=is_mobile)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    result = DamageCalculator.calculate_damage(data)
    return jsonify(result)

@app.route('/optimize', methods=['POST'])
def optimize_damage():
    data = request.get_json()
    
    try:
        base_config = {
            'usePointSystem': data.get('usePointSystem', False),
            'selectedWeapon': data.get('selectedWeapon', ''),
            'magicPotion': data.get('magicPotion', False),
            'attackPotion': data.get('attackPotion', False),
            'goldenApple': data.get('goldenApple', False),
            'useOldVersion': data.get('useOldVersion', False),
            'classLevel': data.get('classLevel', 15),
            'playerLevel': data.get('playerLevel', MAX_LEVEL)  # 添加 playerLevel
        }
        
        if base_config['usePointSystem']:
            base_config.update({
                'strength': data.get('strength', 0),
                'vitality': data.get('vitality', 0),
                'intelligence': data.get('intelligence', 0),
                'dexterity': data.get('dexterity', 0),
                'defense': 0
            })
        else:
            base_config.update({
                'minDamage': data.get('minDamage', 0),
                'maxDamage': data.get('maxDamage', 0),
                'magicDamage': data.get('magicDamage', 0),
                'critRate': data.get('critRate', 1),
                'critDamage': data.get('critDamage', 100)
            })
        
        use_old_version = base_config.get('useOldVersion', False)
        
        if use_old_version:
            all_equipment = []
            for eq_id in EQUIPMENT_DB.keys():
                if eq_id.endswith('_old'):
                    all_equipment.append(eq_id)
                elif '_old' not in eq_id and eq_id + '_old' not in EQUIPMENT_DB:
                    all_equipment.append(eq_id)
        else:
            all_equipment = [eq_id for eq_id in EQUIPMENT_DB.keys() if not eq_id.endswith('_old')]
        
        max_equipment = 3
        
        all_combinations = list(combinations(all_equipment, max_equipment))
        
        results = []
        for i, combo in enumerate(all_combinations):
            if i % 100 == 0:
                print(f"Testing combination {i}/{len(all_combinations)}")
            
            test_config = base_config.copy()
            test_config['equipment'] = list(combo)
            
            result = DamageCalculator.calculate_damage(test_config)
            if result['success']:
                results.append({
                    'equipment': list(combo),
                    'final_damage': result['final_damage'],
                    'ten_second_total': result['ten_second_damage']['total_damage'],
                    'crit_rate': result['crit_rate'],
                    'crit_damage': result['crit_damage']
                })
        
        results.sort(key=lambda x: x['final_damage'], reverse=True)
        
        top_combinations = results[:10]
        
        formatted_results = []
        for combo in top_combinations:
            equipment_names = [EQUIPMENT_DB[eq_id]['name'] for eq_id in combo['equipment']]
            formatted_results.append({
                'equipment_ids': combo['equipment'],
                'equipment_names': equipment_names,
                'final_damage': round(combo['final_damage'], 2),
                'ten_second_total': round(combo['ten_second_total'], 2),
                'crit_rate': round(combo['crit_rate'], 1),
                'crit_damage': round(combo['crit_damage'], 1)
            })
        
        return jsonify({
            'success': True,
            'top_combinations': formatted_results,
            'total_combinations_tested': len(all_combinations),
            'version': 'old' if use_old_version else 'current'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/optimize_advanced', methods=['POST'])
def optimize_damage_advanced():
    data = request.get_json()
    
    try:
        player_level = data.get('playerLevel', MAX_LEVEL)
        
        base_config = {
            'usePointSystem': data.get('usePointSystem', False),
            'selectedWeapon': data.get('selectedWeapon', ''),
            'magicPotion': data.get('magicPotion', False),
            'attackPotion': data.get('attackPotion', False),
            'goldenApple': data.get('goldenApple', False),
            'playerLevel': player_level,
            'useOldVersion': data.get('useOldVersion', False),
            'classLevel': data.get('classLevel', 15)
        }
        
        if base_config['usePointSystem']:
            base_config.update({
                'strength': data.get('strength', 0),
                'vitality': data.get('vitality', 0),
                'intelligence': data.get('intelligence', 0),
                'dexterity': data.get('dexterity', 0),
                'defense': 0
            })
        else:
            base_config.update({
                'minDamage': data.get('minDamage', 0),
                'maxDamage': data.get('maxDamage', 0),
                'magicDamage': data.get('magicDamage', 0),
                'critRate': data.get('critRate', 1),
                'critDamage': data.get('critDamage', 100)
            })
        
        optimization_type = data.get('optimizationType', 'final_damage')
        
        use_old_version = base_config.get('useOldVersion', False)
        
        available_equipment = []
        for eq_id, eq_data in EQUIPMENT_DB.items():
            if eq_data.get('level_req', 0) > player_level:
                continue
            
            if use_old_version:
                if eq_id.endswith('_old'):
                    available_equipment.append(eq_id)
                elif '_old' not in eq_id and eq_id + '_old' not in EQUIPMENT_DB:
                    available_equipment.append(eq_id)
            else:
                available_equipment.append(eq_id)
        
        max_equipment = 3
        
        all_combinations = list(combinations(available_equipment, max_equipment))
        
        filtered_combinations = []
        for combo in all_combinations:
            valid = True
            items_by_base = {}
            
            for item_id in combo:
                base_name = item_id.replace('_old', '')
                if base_name not in items_by_base:
                    items_by_base[base_name] = []
                items_by_base[base_name].append(item_id)
            
            for base_name, versions in items_by_base.items():
                if len(versions) > 1:
                    has_old = any('_old' in v for v in versions)
                    has_new = any('_old' not in v for v in versions)
                    if has_old and has_new:
                        valid = False
                        break
            
            if valid:
                filtered_combinations.append(combo)
        
        results = []
        # 限制测试的组合数量以避免性能问题
        max_combinations_to_test = min(100000, len(filtered_combinations))
        
        if len(filtered_combinations) > max_combinations_to_test:
            tested_combinations = random.sample(filtered_combinations, max_combinations_to_test)
        else:
            tested_combinations = filtered_combinations
        
        for i, combo in enumerate(tested_combinations):
            if i % 100 == 0:
                print(f"Testing combination {i}/{len(tested_combinations)}")
            
            test_config = base_config.copy()
            test_config['equipment'] = list(combo)
            
            has_old_items = any('_old' in item_id for item_id in combo)
            
            result = DamageCalculator.calculate_damage(test_config)
            if result['success']:
                if optimization_type == 'final_damage':
                    score = result['final_damage']
                elif optimization_type == 'ten_second':
                    score = result['ten_second_damage']['total_damage']
                elif optimization_type == 'dot':
                    score = result['dot_damage']
                else:
                    score = result['final_damage']
                
                results.append({
                    'equipment': list(combo),
                    'final_damage': result['final_damage'],
                    'ten_second_total': result['ten_second_damage']['total_damage'],
                    'dot_damage': result['dot_damage'],
                    'crit_rate': result['crit_rate'],
                    'crit_damage': result['crit_damage'],
                    'score': score,
                    'has_old_items': has_old_items
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        top_combinations = results[:10]
        
        formatted_results = []
        for combo in top_combinations:
            equipment_names = []
            for eq_id in combo['equipment']:
                eq_data = EQUIPMENT_DB[eq_id]
                name = eq_data['name']
                if eq_id.endswith('_old'):
                    name = f"{name} (Old)"
                equipment_names.append(name)
            
            formatted_results.append({
                'equipment_ids': combo['equipment'],
                'equipment_names': equipment_names,
                'final_damage': round(combo['final_damage'], 2),
                'ten_second_total': round(combo['ten_second_total'], 2),
                'dot_damage': round(combo['dot_damage'], 2),
                'crit_rate': round(combo['crit_rate'], 1),
                'crit_damage': round(combo['crit_damage'], 1),
                'score': round(combo['score'], 2),
                'has_old_items': combo.get('has_old_items', False)
            })
        
        return jsonify({
            'success': True,
            'top_combinations': formatted_results,
            'total_combinations_tested': len(tested_combinations),
            'total_combinations_available': len(filtered_combinations),
            'optimization_type': optimization_type,
            'available_equipment_count': len(available_equipment),
            'allows_mixed_versions': True,
            'version': 'mixed' if any(r.get('has_old_items', False) for r in top_combinations) else 'current'
        })
        
    except Exception as e:
        print(f"Error in optimize_advanced: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/optimize_stats', methods=['POST'])
def optimize_stats():
    data = request.get_json()
    
    try:
        player_level = data.get('playerLevel', MAX_LEVEL)
        total_points = DamageCalculator.calculate_max_points(player_level)
        vitality = int(data.get('vitality', 0))
        selected_weapon = data.get('selectedWeapon', '')
        
        weapon_type = 'physical'
        if selected_weapon and WEAPON_DB.get(selected_weapon, {}).get('type') == 'staff':
            weapon_type = 'magic'
        
        remaining_points = total_points - vitality
        
        if remaining_points <= 0:
            return jsonify({
                'success': True,
                'recommendation': {
                    'strength': 0,
                    'intelligence': 0,
                    'dexterity': 0,
                    'reason': 'All points allocated to vitality'
                }
            })
        
        if player_level < 50:
            if weapon_type == 'magic':
                intelligence = int(remaining_points * 0.85)
                dexterity = min(int(remaining_points * 0.15), 50)
                strength = 0
            else:
                strength = int(remaining_points * 0.85)
                dexterity = min(int(remaining_points * 0.15), 50)
                intelligence = 0
            defense = 0
            
        elif player_level < 100:
            if weapon_type == 'magic':
                intelligence = int(remaining_points * 0.75)
                dexterity = min(int(remaining_points * 0.25), 50)
                strength = 0
            else:
                strength = int(remaining_points * 0.75)
                dexterity = min(int(remaining_points * 0.25), 50)
                intelligence = 0
            defense = 0
            
        else:
            if weapon_type == 'magic':
                intelligence = int(remaining_points * 0.65)
                dexterity = min(int(remaining_points * 0.35), 50)
                strength = 0
            else:
                strength = int(remaining_points * 0.65)
                dexterity = min(int(remaining_points * 0.35), 50)
                intelligence = 0
            defense = 0
        
        total_used = vitality + strength + intelligence + dexterity + defense
        remaining_after_optimization = total_points - total_used
        
        if remaining_after_optimization > 0:
            if weapon_type == 'magic':
                intelligence += remaining_after_optimization
            else:
                strength += remaining_after_optimization
        
        return jsonify({
            'success': True,
            'recommendation': {
                'strength': strength,
                'intelligence': intelligence,
                'dexterity': dexterity,
                'defense': defense,
                'total_used': vitality + strength + intelligence + dexterity + defense,
                'remaining': total_points - (vitality + strength + intelligence + dexterity + defense),
                'weapon_type': weapon_type,
                'reason': f'Optimized for {weapon_type} damage at level {player_level}'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/generate_result_image', methods=['POST'])
def generate_result_image():
    """生成计算结果图片"""
    try:
        data = request.get_json()
        
        # 获取计算结果
        result = DamageCalculator.calculate_damage(data)
        if not result['success']:
            return jsonify({'success': False, 'error': 'Calculation failed'})
        
        # 使用 ImageGenerator 生成图片
        image_result = ImageGenerator.generate_result_image(data, result, EQUIPMENT_DB, WEAPON_DB)
        
        if not image_result['success']:
            return jsonify({'success': False, 'error': image_result['error']})
        
        # 返回文件
        return send_file(
            image_result['file'],
            mimetype=image_result['mimetype'],
            as_attachment=True,
            download_name=image_result['download_name']
        )
        
    except Exception as e:
        print(f"Error generating result image: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/generate_ranking_image', methods=['POST'])
def generate_ranking_image():
    """生成排名图片"""
    try:
        data = request.get_json()
        
        # 首先执行优化计算
        response = optimize_damage_advanced()
        optimization_data = response.get_json()
        
        # 使用 ImageGenerator 生成图片
        image_result = ImageGenerator.generate_ranking_image(data, optimization_data, EQUIPMENT_DB, WEAPON_DB)
        
        if not image_result['success']:
            return jsonify({'success': False, 'error': image_result['error']})
        
        # 返回文件
        return send_file(
            image_result['file'],
            mimetype=image_result['mimetype'],
            as_attachment=True,
            download_name=image_result['download_name']
        )
        
    except Exception as e:
        print(f"Error generating ranking image: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)