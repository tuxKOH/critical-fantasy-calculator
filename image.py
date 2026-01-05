"""
Image Generation Module for Critical Fantasy Damage Calculator
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

from flask import render_template, jsonify, send_file
from datetime import datetime
import io
import random
from PIL import Image as PILImage, ImageDraw, ImageFont, ImageOps
import base64
import tempfile
import os

class ImageGenerator:
    """圖片生成器類"""
    
    @staticmethod
    def generate_result_image(data, result, equipment_db, weapon_db):
        """生成计算结果圖片 - HTML -> PDF -> PNG"""
        try:
            # 准备模板数据
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # 武器信息
            weapon_id = data.get('selectedWeapon', '')
            weapon_data = weapon_db.get(weapon_id, {})
            weapon_name = weapon_data.get('name', 'No Weapon')
            weapon_type = weapon_data.get('type', 'Unknown')
            weapon_image_url = weapon_data.get('image_url', '')
            
            # 属性分配
            attribute_distribution = None
            if data.get('usePointSystem', False):
                attribute_distribution = {
                    'str': data.get('strength', 0),
                    'vit': data.get('vitality', 0),
                    'int': data.get('intelligence', 0),
                    'dex': data.get('dexterity', 0),
                    'total_used': data.get('strength', 0) + data.get('vitality', 0) + 
                                 data.get('intelligence', 0) + data.get('dexterity', 0)
                }
            
            # 装备信息
            equipment = data.get('equipment', [])
            equipment_list = []
            equipment_images = []
            for eq_id in equipment[:3]:
                eq_data = equipment_db.get(eq_id, {})
                if eq_data:
                    equipment_list.append({
                        'name': eq_data.get('name', eq_id),
                        'tier': eq_data.get('tier', '?'),
                        'id': eq_id,
                        'image_url': eq_data.get('image_url', ''),
                        'is_old': '_old' in eq_id
                    })
                    if eq_data.get('image_url'):
                        equipment_images.append(eq_data['image_url'])
            
            # 药水效果
            potions = []
            if data.get('magicPotion', False):
                potions.append("Magic Potion (1.75x Magic)")
            if data.get('attackPotion', False):
                potions.append("Attack Potion (+0.75x ATK)")
            if data.get('goldenApple', False):
                potions.append("Golden Apple (+0.50x ATK)")
            
            # DoT 效果
            dot_effects = []
            if result.get('burn_chance', 0) > 0:
                dot_effects.append(f"Burn: {result['burn_chance']}%")
            if result.get('bleed_chance', 0) > 0:
                dot_effects.append(f"Bleed: {result['bleed_chance']}%")
            if result.get('poison_chance', 0) > 0:
                dot_effects.append(f"Poison: {result['poison_chance']}%")
            if result.get('has_blood_butcher', False):
                dot_effects.append("Blood Butcher")
            
            # 玩家属性
            player_stats = None
            if result.get('calculated_stats', False) and result.get('player_stats'):
                player_stats = {
                    'total_hp': result['player_stats'].get('total_hp', 0),
                    'attack_multiplier': result['player_stats'].get('attack_multiplier', 1.0),
                    'min_damage': result['player_stats'].get('min_damage', 0),
                    'max_damage': result['player_stats'].get('max_damage', 0),
                    'magic_damage': result['player_stats'].get('magic_damage', 0),
                    'health': result['player_stats'].get('health', 0),
                    'shield': result['player_stats'].get('shield', 0)
                }
            
            # 渲染模板
            html = render_template('share_result.html',
                timestamp=timestamp,
                weapon_name=weapon_name,
                weapon_type=weapon_type,
                weapon_image_url=weapon_image_url,
                player_level=data.get('playerLevel', 1),
                class_level=result.get('class_level', 15),
                class_multiplier=result.get('class_multiplier', 1.0),
                base_damage=result.get('base_damage', 0),
                dot_damage=result.get('dot_damage', 0),
                ten_second_total=result.get('ten_second_damage', {}).get('total_damage', 0),
                final_damage=result.get('final_damage', 0),
                damage_after_crit=result.get('damage_after_crit', result.get('base_damage', 0)),
                damage_type='Magic' if result.get('damage_type') == 'magic' else 'Physical',
                crit_rate=result.get('crit_rate', 0),
                crit_damage=result.get('crit_damage', 0),
                effective_multiplier=result.get('effective_multiplier', 0),
                attack_mechanic=result.get('ten_second_damage', {}).get('mechanic', 'Default'),
                dot_effects=' • '.join(dot_effects) if dot_effects else 'No DoT Effects',
                equipment=equipment_list,
                equipment_count=len(equipment_list),
                potions=potions,
                potion_count=len(potions),
                player_stats=player_stats,
                attribute_distribution=attribute_distribution,
                burn_chance=result.get('burn_chance', 0),
                bleed_chance=result.get('bleed_chance', 0),
                poison_chance=result.get('poison_chance', 0)
            )
            
            # 使用 WeasyPrint 生成 PDF
            try:
                from weasyprint import HTML
                
                # 生成 PDF
                pdf_bytes = HTML(string=html).write_pdf()
                
                # 將 PDF 轉換為 PNG
                img_bytes = ImageGenerator.pdf_to_png(pdf_bytes)
                
                mimetype = 'image/png'
                download_name = f'damage_calc_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                
            except ImportError as e:
                print(f"WeasyPrint import error: {e}")
                # 如果 WeasyPrint 不可用，使用 PIL 創建簡單圖片
                return ImageGenerator.generate_simple_image_compact(result, data, 'result')
            except Exception as e:
                print(f"PDF generation error: {e}")
                return ImageGenerator.generate_simple_image_compact(result, data, 'result')
            
            # 返回文件
            img_io = io.BytesIO(img_bytes)
            return {
                'success': True,
                'file': img_io,
                'mimetype': mimetype,
                'download_name': download_name
            }
            
        except Exception as e:
            print(f"Error generating result image: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def generate_ranking_image(data, optimization_data, equipment_db, weapon_db):
        """生成排名圖片 - HTML -> PDF -> PNG"""
        try:
            if not optimization_data['success']:
                return {'success': False, 'error': 'Optimization failed'}
            
            # 准备模板数据
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # 武器信息
            weapon_id = data.get('selectedWeapon', '')
            weapon_data = weapon_db.get(weapon_id, {})
            weapon_name = weapon_data.get('name', 'No Weapon')
            weapon_image_url = weapon_data.get('image_url', '')
            
            # 属性分配
            stats_distribution = None
            if data.get('usePointSystem', False):
                stats_distribution = {
                    'str': data.get('strength', 0),
                    'vit': data.get('vitality', 0),
                    'int': data.get('intelligence', 0),
                    'dex': data.get('dexterity', 0),
                    'total_used': data.get('strength', 0) + data.get('vitality', 0) +
                                 data.get('intelligence', 0) + data.get('dexterity', 0)
                }
            
            # 排名类型名称
            rank_name = {
                'final_damage': 'Final Damage',
                'ten_second': '10-Second Damage',
                'dot': 'DoT Damage'
            }.get(optimization_data.get('optimization_type', 'final_damage'), 'Final Damage')
            
            # 排名颜色
            rank_colors = ['#ffd700', '#c0c0c0', '#cd7f32', '#3498db', '#2ecc71']
            
            # 处理每个组合的数据
            top_combinations = optimization_data.get('top_combinations', [])[:5]
            
            # 为每个组合添加装备图片信息
            for combo in top_combinations:
                equipment_images = []
                for eq_id in combo['equipment_ids']:
                    eq_data = equipment_db.get(eq_id, {})
                    if eq_data and eq_data.get('image_url'):
                        equipment_images.append(eq_data['image_url'])
                combo['equipment_images'] = equipment_images[:3]
            
            # 渲染模板
            html = render_template('share_ranking.html',
                timestamp=timestamp,
                weapon_name=weapon_name,
                weapon_image_url=weapon_image_url,
                player_level=data.get('playerLevel', 1),
                rank_name=rank_name,
                rank_colors=rank_colors,
                stats_distribution=stats_distribution,
                top_combinations=top_combinations,
                total_combinations_tested=optimization_data.get('total_combinations_tested', 0),
                available_equipment_count=optimization_data.get('available_equipment_count', 0),
                version=optimization_data.get('version', 'current'),
                optimization_type=optimization_data.get('optimization_type', 'final_damage')
            )
            
            # 使用 WeasyPrint 生成 PDF
            try:
                from weasyprint import HTML
                
                # 生成 PDF
                pdf_bytes = HTML(string=html).write_pdf()
                
                # 將 PDF 轉換為 PNG
                img_bytes = ImageGenerator.pdf_to_png(pdf_bytes)
                
                mimetype = 'image/png'
                download_name = f'damage_calc_ranking_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                
            except ImportError as e:
                print(f"WeasyPrint import error: {e}")
                return ImageGenerator.generate_simple_image_compact(optimization_data, data, 'ranking')
            except Exception as e:
                print(f"PDF generation error: {e}")
                return ImageGenerator.generate_simple_image_compact(optimization_data, data, 'ranking')
            
            # 返回文件
            img_io = io.BytesIO(img_bytes)
            return {
                'success': True,
                'file': img_io,
                'mimetype': mimetype,
                'download_name': download_name
            }
            
        except Exception as e:
            print(f"Error generating ranking image: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def pdf_to_png(pdf_bytes, dpi=150):
        """將 PDF 轉換為 PNG"""
        try:
            # 使用臨時文件
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                tmp_pdf.write(pdf_bytes)
                tmp_pdf_path = tmp_pdf.name
            
            # 嘗試使用 pdf2image 或 pdf2im 來轉換
            try:
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(pdf_bytes, dpi=dpi)
            except ImportError:
                # 備用方案：使用簡單的 PIL 方法
                from PIL import Image
                images = [Image.new('RGB', (800, 600), color='white')]
                draw = ImageDraw.Draw(images[0])
                draw.text((50, 50), "PDF to PNG conversion requires pdf2image", fill='black')
                draw.text((50, 80), "Install with: pip install pdf2image", fill='black')
            
            # 將所有頁面合併為單一圖像（假設只有一頁）
            if images:
                # 調整圖像大小以適合單頁
                img = images[0]
                
                # 確保圖像尺寸適合顯示
                max_width = 1200
                max_height = 1600
                
                # 調整大小但保持比例
                img_ratio = img.width / img.height
                target_ratio = max_width / max_height
                
                if img_ratio > target_ratio:
                    # 以寬度為基準調整
                    new_width = max_width
                    new_height = int(max_width / img_ratio)
                else:
                    # 以高度為基準調整
                    new_height = max_height
                    new_width = int(max_height * img_ratio)
                
                img = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                
                # 如果圖像太小，創建一個白色背景並將圖像置中
                if new_width < max_width or new_height < max_height:
                    background = PILImage.new('RGB', (max_width, max_height), color='white')
                    x_offset = (max_width - new_width) // 2
                    y_offset = (max_height - new_height) // 2
                    background.paste(img, (x_offset, y_offset))
                    img = background
            
            # 轉換為 bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, 'PNG', quality=90, optimize=True)
            img_bytes.seek(0)
            
            # 清理臨時文件
            try:
                os.unlink(tmp_pdf_path)
            except:
                pass
            
            return img_bytes.getvalue()
            
        except Exception as e:
            print(f"Error converting PDF to PNG: {e}")
            # 返回一個錯誤圖像
            return ImageGenerator.create_error_image("PDF to PNG conversion failed")
    
    @staticmethod
    def create_error_image(message):
        """創建錯誤圖像"""
        img = PILImage.new('RGB', (800, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Error Generating Image", fill='red', font=font)
        draw.text((50, 100), message, fill='black', font=font)
        draw.text((50, 150), "Please try again or use simple image mode.", fill='gray', font=font)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, 'PNG', quality=95)
        img_bytes.seek(0)
        return img_bytes.getvalue()
    
    @staticmethod
    def generate_simple_image_compact(data, config_data, image_type='result'):
        """生成紧凑的简单图片（备用方案）"""
        try:
            # 创建一個更緊湊的圖片
            width = 900
            height = 1200 if image_type == 'result' else 1400
            
            # 创建白色背景
            img = PILImage.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # 嘗試加載字體
            try:
                title_font = ImageFont.truetype("arial.ttf", 32)
                header_font = ImageFont.truetype("arial.ttf", 24)
                normal_font = ImageFont.truetype("arial.ttf", 18)
                small_font = ImageFont.truetype("arial.ttf", 14)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                normal_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            y_offset = 30
            
            if image_type == 'result':
                # 繪製標題
                draw.text((width//2, y_offset), "Fantasy Damage Calculator", fill='black', font=title_font, anchor='mm')
                y_offset += 50
                
                draw.text((width//2, y_offset), f"Result - {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                         fill='gray', font=small_font, anchor='mm')
                y_offset += 40
                
                # 分隔線
                draw.line([(50, y_offset), (width-50, y_offset)], fill='gray', width=2)
                y_offset += 30
                
                # 武器信息
                draw.text((50, y_offset), "Weapon:", fill='black', font=header_font)
                weapon_name = config_data.get('selectedWeapon', 'No Weapon')
                draw.text((200, y_offset), f"{weapon_name}", fill='#2c3e50', font=normal_font)
                y_offset += 35
                
                # 玩家等級和職業等級
                draw.text((50, y_offset), "Player Level:", fill='black', font=normal_font)
                player_level = config_data.get('playerLevel', 1)
                draw.text((200, y_offset), f"{player_level}", fill='#2c3e50', font=normal_font)
                
                draw.text((400, y_offset), "Class Level:", fill='black', font=normal_font)
                class_level = data.get('class_level', 15)
                class_multiplier = data.get('class_multiplier', 1.0)
                draw.text((550, y_offset), f"{class_level} ({class_multiplier}x)", fill='#2c3e50', font=normal_font)
                y_offset += 40
                
                # 屬性分配
                if config_data.get('usePointSystem', False):
                    draw.text((50, y_offset), "Attribute Points:", fill='#2c3e50', font=header_font)
                    y_offset += 30
                    
                    attr_colors = ['#e74c3c', '#3498db', '#9b59b6', '#2ecc71']
                    attributes = [
                        ("STR", config_data.get('strength', 0)),
                        ("VIT", config_data.get('vitality', 0)),
                        ("INT", config_data.get('intelligence', 0)),
                        ("DEX", config_data.get('dexterity', 0))
                    ]
                    
                    attr_width = width // 4
                    for i, (name, value) in enumerate(attributes):
                        x = 50 + i * attr_width
                        draw.text((x + attr_width//2, y_offset), name, 
                                 fill=attr_colors[i], font=normal_font, anchor='mm')
                        draw.text((x + attr_width//2, y_offset + 25), str(value), 
                                 fill='#2c3e50', font=normal_font, anchor='mm')
                    
                    y_offset += 60
                    
                    total_used = (config_data.get('strength', 0) + config_data.get('vitality', 0) +
                                 config_data.get('intelligence', 0) + config_data.get('dexterity', 0))
                    max_points = player_level * 2
                    draw.text((width//2, y_offset), f"Points: {total_used}/{max_points}", 
                             fill='#666', font=small_font, anchor='mm')
                    y_offset += 40
                
                # 分隔線
                draw.line([(50, y_offset), (width-50, y_offset)], fill='lightgray', width=1)
                y_offset += 30
                
                # 傷害結果 - 主要顯示
                draw.text((width//2, y_offset), "Damage Results", fill='#2c3e50', font=header_font, anchor='mm')
                y_offset += 40
                
                # 最終傷害（大號字體）
                final_damage = data.get('final_damage', 0)
                draw.text((width//2, y_offset), f"{final_damage:,.0f}", 
                         fill='#2ecc71', font=title_font, anchor='mm')
                y_offset += 50
                
                draw.text((width//2, y_offset), "Final Damage", fill='#666', font=small_font, anchor='mm')
                y_offset += 60
                
                # 其他傷害統計（網格佈局）
                col_width = width // 3
                
                # 第一行
                base_y = y_offset
                draw.text((col_width//2, base_y), "Base Damage", fill='#666', font=small_font, anchor='mm')
                draw.text((col_width//2, base_y+25), f"{data.get('base_damage', 0):,.0f}", 
                         fill='#3498db', font=normal_font, anchor='mm')
                
                draw.text((col_width + col_width//2, base_y), "DoT Damage", fill='#666', font=small_font, anchor='mm')
                draw.text((col_width + col_width//2, base_y+25), f"{data.get('dot_damage', 0):,.0f}", 
                         fill='#e74c3c', font=normal_font, anchor='mm')
                
                draw.text((2*col_width + col_width//2, base_y), "10s Total", fill='#666', font=small_font, anchor='mm')
                draw.text((2*col_width + col_width//2, base_y+25), f"{data.get('ten_second_damage', {}).get('total_damage', 0):,.0f}", 
                         fill='#f39c12', font=normal_font, anchor='mm')
                
                y_offset += 80
                
                # 第二行
                base_y = y_offset
                draw.text((col_width//2, base_y), "Damage After Crit", fill='#666', font=small_font, anchor='mm')
                damage_after_crit = data.get('damage_after_crit', 0)
                if damage_after_crit == 0:
                    damage_after_crit = data.get('base_damage', 0)
                draw.text((col_width//2, base_y+25), f"{damage_after_crit:,.0f}", 
                         fill='#9b59b6', font=normal_font, anchor='mm')
                
                draw.text((col_width + col_width//2, base_y), "Crit Rate", fill='#666', font=small_font, anchor='mm')
                draw.text((col_width + col_width//2, base_y+25), f"{data.get('crit_rate', 0)}%", 
                         fill='#8e44ad', font=normal_font, anchor='mm')
                
                draw.text((2*col_width + col_width//2, base_y), "Crit Damage", fill='#666', font=small_font, anchor='mm')
                draw.text((2*col_width + col_width//2, base_y+25), f"{data.get('crit_damage', 0)}%", 
                         fill='#8e44ad', font=normal_font, anchor='mm')
                
                y_offset += 80
                
                # 分隔線
                draw.line([(50, y_offset), (width-50, y_offset)], fill='lightgray', width=1)
                y_offset += 30
                
                # 詳細統計
                draw.text((50, y_offset), "Details:", fill='#2c3e50', font=header_font)
                y_offset += 40
                
                # 兩列佈局
                stats_left = [
                    ("Damage Type", data.get('damage_type', 'Physical').capitalize()),
                    ("Multiplier", f"{data.get('effective_multiplier', 0)}x")
                ]
                
                stats_right = [
                    ("Attack Mechanic", data.get('ten_second_damage', {}).get('mechanic', 'Default')),
                    ("Burn Chance", f"{data.get('burn_chance', 0)}%")
                ]
                
                for i, (label, value) in enumerate(stats_left):
                    draw.text((50, y_offset + i*30), f"{label}:", fill='#666', font=normal_font)
                    draw.text((250, y_offset + i*30), value, fill='#2c3e50', font=normal_font)
                
                for i, (label, value) in enumerate(stats_right):
                    draw.text((450, y_offset + i*30), f"{label}:", fill='#666', font=normal_font)
                    draw.text((650, y_offset + i*30), value, fill='#2c3e50', font=normal_font)
                
                y_offset += len(stats_left) * 30 + 10
                
                # 額外的DoT效果
                if data.get('bleed_chance', 0) > 0 or data.get('poison_chance', 0) > 0:
                    extra_stats = []
                    if data.get('bleed_chance', 0) > 0:
                        extra_stats.append(("Bleed Chance", f"{data.get('bleed_chance', 0)}%"))
                    if data.get('poison_chance', 0) > 0:
                        extra_stats.append(("Poison Chance", f"{data.get('poison_chance', 0)}%"))
                    
                    for i, (label, value) in enumerate(extra_stats):
                        if i % 2 == 0:
                            draw.text((50, y_offset), f"{label}:", fill='#666', font=normal_font)
                            draw.text((250, y_offset), value, fill='#2c3e50', font=normal_font)
                        else:
                            draw.text((450, y_offset), f"{label}:", fill='#666', font=normal_font)
                            draw.text((650, y_offset), value, fill='#2c3e50', font=normal_font)
                            y_offset += 30
                    
                    if len(extra_stats) % 2 == 1:
                        y_offset += 30
                
                y_offset += 30
                
                # 裝備信息
                if 'equipment' in config_data and config_data['equipment']:
                    draw.text((50, y_offset), "Equipment:", fill='#2c3e50', font=header_font)
                    y_offset += 40
                    
                    # 最多顯示3個裝備
                    for i, eq_id in enumerate(config_data['equipment'][:3]):
                        eq_text = eq_id.replace('_', ' ').title()
                        if i < 3:  # 第一行
                            draw.text((50 + i*300, y_offset), f"• {eq_text}", fill='#2c3e50', font=normal_font)
                        else:  # 第二行
                            draw.text((50 + (i-3)*300, y_offset+30), f"• {eq_text}", fill='#2c3e50', font=normal_font)
                    
                    if len(config_data['equipment']) > 3:
                        draw.text((50 + 2*300, y_offset), f"+{len(config_data['equipment'])-3} more", 
                                 fill='gray', font=small_font)
                    
                    y_offset += 60
                
                # 底部信息
                draw.text((width//2, height-30), f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                         fill='gray', font=small_font, anchor='mm')
                
            else:  # ranking
                # 繪製排名圖片
                draw.text((width//2, y_offset), "Optimization Rankings", fill='black', font=title_font, anchor='mm')
                y_offset += 50
                
                draw.text((width//2, y_offset), f"{datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                         fill='gray', font=small_font, anchor='mm')
                y_offset += 40
                
                # 分隔線
                draw.line([(50, y_offset), (width-50, y_offset)], fill='gray', width=2)
                y_offset += 30
                
                # 配置信息
                draw.text((50, y_offset), "Configuration:", fill='#2c3e50', font=header_font)
                y_offset += 40
                
                draw.text((50, y_offset), "Weapon:", fill='#666', font=normal_font)
                weapon_name = config_data.get('selectedWeapon', 'No Weapon')
                draw.text((200, y_offset), f"{weapon_name}", fill='#2c3e50', font=normal_font)
                
                draw.text((400, y_offset), "Player Level:", fill='#666', font=normal_font)
                player_level = config_data.get('playerLevel', 1)
                draw.text((550, y_offset), f"{player_level}", fill='#2c3e50', font=normal_font)
                y_offset += 40
                
                # 屬性分配
                if config_data.get('usePointSystem', False):
                    draw.text((50, y_offset), "Attribute Points:", fill='#2c3e50', font=header_font)
                    y_offset += 30
                    
                    attributes = [
                        ("STR", config_data.get('strength', 0)),
                        ("VIT", config_data.get('vitality', 0)),
                        ("INT", config_data.get('intelligence', 0)),
                        ("DEX", config_data.get('dexterity', 0))
                    ]
                    
                    attr_width = width // 4
                    for i, (name, value) in enumerate(attributes):
                        x = 50 + i * attr_width
                        draw.text((x + attr_width//2, y_offset), name, 
                                 fill='#2c3e50', font=normal_font, anchor='mm')
                        draw.text((x + attr_width//2, y_offset + 25), str(value), 
                                 fill='#2c3e50', font=normal_font, anchor='mm')
                    
                    y_offset += 60
                
                draw.text((50, y_offset), "Rank Type:", fill='#666', font=normal_font)
                rank_type = data.get('optimization_type', 'final_damage')
                rank_name = {
                    'final_damage': 'Final Damage',
                    'ten_second': '10s Total Damage',
                    'dot': 'DoT Damage'
                }.get(rank_type, 'Final Damage')
                draw.text((200, y_offset), rank_name, fill='#3498db', font=normal_font)
                y_offset += 50
                
                # 分隔線
                draw.line([(50, y_offset), (width-50, y_offset)], fill='lightgray', width=1)
                y_offset += 30
                
                # 排名結果
                draw.text((width//2, y_offset), "Top 5 Combinations", fill='#2c3e50', font=header_font, anchor='mm')
                y_offset += 40
                
                # 繪製排名
                top_combinations = data.get('top_combinations', [])[:5]
                for i, combo in enumerate(top_combinations):
                    # 排名卡片背景
                    card_y = y_offset
                    card_height = 100
                    
                    # 排名號碼
                    rank_color = ['#ffd700', '#c0c0c0', '#cd7f32', '#3498db', '#2ecc71'][i] if i < 5 else '#3498db'
                    draw.text((70, card_y + 20), f"#{i+1}", fill=rank_color, font=header_font)
                    
                    # 分數
                    score = combo.get('score', 0)
                    draw.text((width-100, card_y + 20), f"{score:,.0f}", fill='#2c3e50', font=header_font)
                    
                    # 裝備名稱
                    eq_names = combo.get('equipment_names', [])
                    eq_text = ", ".join(eq_names[:2])  # 只顯示前2個
                    if len(eq_names) > 2:
                        eq_text += f" +{len(eq_names)-2}"
                    
                    # 確保文本不會超出範圍
                    max_text_width = width - 200
                    if len(eq_text) > 40:
                        eq_text = eq_text[:37] + "..."
                    
                    draw.text((120, card_y + 20), eq_text, fill='#2c3e50', font=normal_font)
                    
                    # 詳細統計
                    stats_y = card_y + 50
                    draw.text((120, stats_y), f"Final: {combo.get('final_damage', 0):,.0f}", 
                             fill='#666', font=small_font)
                    draw.text((320, stats_y), f"10s: {combo.get('ten_second_total', 0):,.0f}", 
                             fill='#666', font=small_font)
                    draw.text((520, stats_y), f"DoT: {combo.get('dot_damage', 0):,.0f}", 
                             fill='#666', font=small_font)
                    
                    # 分隔線
                    draw.line([(50, card_y + card_height), (width-50, card_y + card_height)], 
                             fill='#f0f0f0', width=1)
                    
                    y_offset += card_height + 10
                
                y_offset += 20
                
                # 統計信息
                draw.text((50, y_offset), "Statistics:", fill='#2c3e50', font=header_font)
                y_offset += 40
                
                col_width = width // 3
                stats_data = [
                    ("Combinations Tested", f"{data.get('total_combinations_tested', 0):,}"),
                    ("Available Equipment", str(data.get('available_equipment_count', 0))),
                    ("Version", data.get('version', 'current').capitalize())
                ]
                
                for i, (label, value) in enumerate(stats_data):
                    draw.text((50 + i*col_width, y_offset), label, fill='#666', font=small_font)
                    draw.text((50 + i*col_width, y_offset+20), value, fill='#2c3e50', font=normal_font)
                
                y_offset += 60
                
                # 底部信息
                draw.text((width//2, height-30), f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                         fill='gray', font=small_font, anchor='mm')
            
            # 保存到 BytesIO
            img_io = io.BytesIO()
            img.save(img_io, 'PNG', quality=90, optimize=True)
            img_io.seek(0)
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            if image_type == 'result':
                download_name = f'damage_calc_result_{timestamp_str}.png'
            else:
                download_name = f'damage_calc_ranking_{timestamp_str}.png'
            
            return {
                'success': True,
                'file': img_io,
                'mimetype': 'image/png',
                'download_name': download_name
            }
            
        except Exception as e:
            print(f"Error generating simple image: {e}")
            return {'success': False, 'error': str(e)}