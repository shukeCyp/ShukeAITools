#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词管理API路由
"""

import os
import pandas as pd
import base64
import io
from flask import Blueprint, request, jsonify
from pathlib import Path
from openpyxl import load_workbook
from PIL import Image

# 创建蓝图
prompt_bp = Blueprint('prompt', __name__, url_prefix='/api/prompt')

# 提示词数据库路径 - backend目录下的prompt_database
PROMPT_DATABASE_PATH = Path(__file__).parent.parent.parent / 'prompt_database'

def extract_images_from_excel(excel_file, platform='jimeng'):
    """从Excel文件中提取图片并返回Base64编码的字典"""
    images = {}
    
    try:
        # 使用openpyxl加载工作簿
        wb = load_workbook(excel_file)
        ws = wb.active
        
        print(f"开始从Excel提取图片，工作表名: {ws.title}")
        
        # 检查是否有图片
        if not hasattr(ws, '_images') or not ws._images:
            print("工作表中没有找到图片对象")
            return images
        
        print(f"发现 {len(ws._images)} 个图片对象")
        
        # 遍历工作表中的所有图片
        for idx, image in enumerate(ws._images):
            try:
                print(f"处理图片 {idx + 1}")
                
                # 尝试多种方式获取图片数据
                img_bytes = None
                row_idx = None
                
                # 方法1: 尝试_data方法
                if hasattr(image, '_data') and callable(image._data):
                    try:
                        img_bytes = image._data()
                        print(f"图片 {idx + 1}: 使用_data()方法获取数据，大小: {len(img_bytes) if img_bytes else 0}")
                    except Exception as e:
                        print(f"图片 {idx + 1}: _data()方法失败: {str(e)}")
                
                # 方法2: 尝试ref属性
                if not img_bytes and hasattr(image, 'ref'):
                    try:
                        img_bytes = image.ref
                        print(f"图片 {idx + 1}: 使用ref属性获取数据，大小: {len(img_bytes) if img_bytes else 0}")
                    except Exception as e:
                        print(f"图片 {idx + 1}: ref属性失败: {str(e)}")
                
                # 方法3: 尝试image属性
                if not img_bytes and hasattr(image, 'image'):
                    try:
                        img_bytes = image.image
                        print(f"图片 {idx + 1}: 使用image属性获取数据，大小: {len(img_bytes) if img_bytes else 0}")
                    except Exception as e:
                        print(f"图片 {idx + 1}: image属性失败: {str(e)}")
                
                # 获取位置信息
                if hasattr(image, 'anchor') and image.anchor:
                    try:
                        if hasattr(image.anchor, '_from') and hasattr(image.anchor._from, 'row'):
                            row_idx = image.anchor._from.row
                            print(f"图片 {idx + 1}: 位置行号 {row_idx}")
                        elif hasattr(image.anchor, 'row'):
                            row_idx = image.anchor.row
                            print(f"图片 {idx + 1}: 位置行号 {row_idx}")
                    except Exception as e:
                        print(f"图片 {idx + 1}: 获取位置失败: {str(e)}")
                
                # 如果没有位置信息，使用索引
                if row_idx is None:
                    row_idx = idx + 2  # 假设从第2行开始（考虑表头）
                    print(f"图片 {idx + 1}: 使用默认行号 {row_idx}")
                
                # 处理图片数据
                if img_bytes:
                    try:
                        # 确保img_bytes是字节类型
                        if isinstance(img_bytes, str):
                            img_bytes = img_bytes.encode('utf-8')
                        
                        pil_image = Image.open(io.BytesIO(img_bytes))
                        
                        # 转换为RGB格式（如果不是的话）
                        if pil_image.mode != 'RGB':
                            pil_image = pil_image.convert('RGB')
                        
                        # 调整图片大小（可选，避免图片过大）
                        max_size = (400, 300)
                        pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
                        
                        # 保存为JPEG格式的字节流
                        img_buffer = io.BytesIO()
                        pil_image.save(img_buffer, format='JPEG', quality=85)
                        img_buffer.seek(0)
                        
                        # 编码为Base64
                        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                        
                        # 存储到字典中，使用行号作为键
                        images[row_idx] = f"data:image/jpeg;base64,{img_base64}"
                        print(f"成功提取图片 {idx + 1} - 行号: {row_idx}, Base64大小: {len(img_base64)//1024}KB")
                        
                    except Exception as e:
                        print(f"处理图片 {idx + 1} 失败: {str(e)}")
                        continue
                else:
                    print(f"图片 {idx + 1}: 无法获取图片数据")
                    
            except Exception as e:
                print(f"提取图片 {idx + 1} 总体失败: {str(e)}")
                continue
        
        print(f"总共提取到 {len(images)} 张图片")
        return images
        
    except Exception as e:
        print(f"从Excel提取图片失败: {str(e)}")
        return {}

def get_image_base64(image_filename, platform='jimeng'):
    """获取图片的Base64编码（从文件系统）"""
    if not image_filename:
        return None
    
    try:
        # 图片文件路径 - 在prompt_database/{platform}/images/目录下
        image_path = PROMPT_DATABASE_PATH / platform / 'images' / image_filename
        
        if not image_path.exists():
            return None
        
        # 读取图片文件并转换为Base64
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # 根据文件扩展名确定MIME类型
            ext = image_path.suffix.lower()
            if ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif ext == '.png':
                mime_type = 'image/png'
            elif ext == '.gif':
                mime_type = 'image/gif'
            elif ext == '.webp':
                mime_type = 'image/webp'
            else:
                mime_type = 'image/jpeg'  # 默认
            
            return f"data:{mime_type};base64,{img_base64}"
    except Exception as e:
        print(f"读取图片失败 {image_filename}: {str(e)}")
        return None

def load_prompt_data(platform='jimeng'):
    """加载指定平台的提示词数据"""
    try:
        platform_path = PROMPT_DATABASE_PATH / platform
        excel_file = platform_path / 'prompt.xlsx'
        
        if not excel_file.exists():
            return {'success': False, 'message': f'提示词文件不存在: {excel_file}', 'data': []}
        
        # 先提取Excel中的所有图片
        excel_images = extract_images_from_excel(excel_file, platform)
        
        # 读取Excel文件 - 只读取值，不执行公式
        df = pd.read_excel(excel_file, engine='openpyxl')
        
        # 确保列名正确
        expected_columns = ['name', 'image', 'prompt']
        if not all(col in df.columns for col in expected_columns):
            return {'success': False, 'message': f'Excel文件格式错误，需要包含列: {expected_columns}', 'data': []}
        
        # 转换为字典列表
        prompts = []
        for idx, row in df.iterrows():
            # 跳过空行
            if pd.isna(row['name']) or str(row['name']).strip() == '':
                continue
            
            # 处理图片字段
            image_value = str(row['image']).strip() if not pd.isna(row['image']) else ''
            image_base64 = None
            
            # 优先从Excel中提取的图片获取（行号+1因为Excel从1开始，再+1因为有表头）
            excel_row = idx + 2  # DataFrame索引从0开始，Excel行号从1开始，还要考虑表头
            if excel_row in excel_images:
                image_base64 = excel_images[excel_row]
                print(f"使用Excel中的图片 - 行号: {excel_row}")
            # 如果Excel中没有图片，尝试从文件系统读取
            elif image_value and not (image_value.startswith('=') or 'DISPIMG' in image_value):
                image_base64 = get_image_base64(image_value, platform)
                if image_base64:
                    print(f"使用文件系统图片: {image_value}")
            
            prompt_item = {
                'name': str(row['name']).strip(),
                'image_filename': image_value if not (image_value.startswith('=') or 'DISPIMG' in image_value) else '',
                'image_base64': image_base64,
                'prompt': str(row['prompt']).strip() if not pd.isna(row['prompt']) else ''
            }
            prompts.append(prompt_item)
        
        return {'success': True, 'message': f'成功加载 {len(prompts)} 个提示词', 'data': prompts}
        
    except Exception as e:
        return {'success': False, 'message': f'读取提示词文件失败: {str(e)}', 'data': []}

@prompt_bp.route('/search', methods=['GET'])
def search_prompts():
    """搜索提示词"""
    try:
        # 获取查询参数
        platform = request.args.get('platform', 'jimeng')
        query = request.args.get('query', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 加载提示词数据
        result = load_prompt_data(platform)
        if not result['success']:
            return jsonify(result), 400
        
        prompts = result['data']
        
        # 如果有查询关键词，进行模糊搜索
        if query:
            query_lower = query.lower()
            filtered_prompts = []
            for prompt in prompts:
                if query_lower in prompt['name'].lower():
                    filtered_prompts.append(prompt)
            prompts = filtered_prompts
        
        # 分页处理
        total = len(prompts)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_prompts = prompts[start:end]
        
        return jsonify({
            'success': True,
            'message': f'找到 {total} 个匹配的提示词',
            'data': {
                'prompts': paginated_prompts,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        print(f"搜索提示词失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'搜索提示词失败: {str(e)}'
        }), 500

@prompt_bp.route('/platforms', methods=['GET'])
def get_platforms():
    """获取可用的平台列表"""
    try:
        platforms = []
        if PROMPT_DATABASE_PATH.exists():
            for item in PROMPT_DATABASE_PATH.iterdir():
                if item.is_dir():
                    excel_file = item / 'prompt.xlsx'
                    if excel_file.exists():
                        platforms.append({
                            'name': item.name,
                            'display_name': item.name.title(),
                            'file_path': str(excel_file)
                        })
        
        return jsonify({
            'success': True,
            'message': f'找到 {len(platforms)} 个平台',
            'data': platforms
        })
        
    except Exception as e:
        print(f"获取平台列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取平台列表失败: {str(e)}'
        }), 500

@prompt_bp.route('/detail/<platform>/<name>', methods=['GET'])
def get_prompt_detail(platform, name):
    """获取特定提示词详情"""
    try:
        # 加载提示词数据
        result = load_prompt_data(platform)
        if not result['success']:
            return jsonify(result), 400
        
        prompts = result['data']
        
        # 查找匹配的提示词
        for prompt in prompts:
            if prompt['name'] == name:
                return jsonify({
                    'success': True,
                    'message': '获取提示词详情成功',
                    'data': prompt
                })
        
        return jsonify({
            'success': False,
            'message': f'未找到名称为 "{name}" 的提示词'
        }), 404
        
    except Exception as e:
        print(f"获取提示词详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取提示词详情失败: {str(e)}'
        }), 500

@prompt_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取提示词统计信息"""
    try:
        stats = {
            'total_platforms': 0,
            'total_prompts': 0,
            'platform_stats': []
        }
        
        if PROMPT_DATABASE_PATH.exists():
            for item in PROMPT_DATABASE_PATH.iterdir():
                if item.is_dir():
                    excel_file = item / 'prompt.xlsx'
                    if excel_file.exists():
                        result = load_prompt_data(item.name)
                        if result['success']:
                            prompt_count = len(result['data'])
                            stats['total_platforms'] += 1
                            stats['total_prompts'] += prompt_count
                            stats['platform_stats'].append({
                                'platform': item.name,
                                'count': prompt_count
                            })
        
        return jsonify({
            'success': True,
            'message': '获取统计信息成功',
            'data': stats
        })
        
    except Exception as e:
        print(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500 