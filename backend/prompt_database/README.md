# 提示词数据库使用说明

## 目录结构
```
backend/
└── prompt_database/
    └── jimeng/
        ├── prompt.xlsx     # Excel提示词文件
        └── images/         # 图片文件夹（可选）
            ├── cat.jpg
            ├── sunset.png
            └── ...
```

## Excel文件格式要求

### 列名配置
- **A列**: `name` - 提示词名称（中文）
- **B列**: `image` - 图片文件名（可选，纯文本，不是Excel公式）
- **C列**: `prompt` - 提示词内容（英文）

### 图片文件说明
- 如果B列填写图片文件名（如 `sunset.jpg`），对应的图片文件应放在 `images/` 文件夹中
- 支持的图片格式：JPG, JPEG, PNG, GIF, WEBP
- 后端会自动将图片转换为Base64编码返回给前端
- 如果不需要图片，B列可以留空

### 示例数据
| name | image | prompt |
|------|-------|--------|
| 美丽的日落风景 | sunset_landscape.jpg | A beautiful sunset landscape with golden hour lighting... |
| 可爱的小猫咪 | cute_cat.jpg | An adorable kitten with fluffy fur, big bright eyes... |
| 现代都市夜景 |  | Modern city skyline at night, skyscrapers with glowing... |

**注意**: B列应该填写纯文本文件名，不要使用Excel公式（如`=DISPIMG(...)`），系统会自动过滤掉公式。

## 使用方法

1. **编辑Excel文件**
   - 直接编辑 `backend/prompt_database/jimeng/prompt.xlsx`
   - 按照A、B、C列格式添加提示词
   - 保存文件

2. **添加图片（可选）**
   - 将图片文件放入 `backend/prompt_database/jimeng/images/` 目录
   - 在Excel的B列填写对应的文件名
   - 前端会自动显示图片预览

3. **前端使用**
   - 在网页中点击"提示词"菜单
   - 搜索、浏览、复制提示词
   - 支持中文模糊搜索
   - 自动显示图片预览（Base64编码）

4. **API接口**
   - `GET /api/prompt/search` - 搜索提示词
   - `GET /api/prompt/stats` - 获取统计信息
   - `GET /api/prompt/platforms` - 获取平台列表

## 注意事项

- ✅ 不需要数据库，直接读取Excel文件
- ✅ 支持实时更新，修改Excel文件后立即生效
- ✅ 图片自动转换为Base64编码，无需配置静态文件服务
- ✅ 提示词名称支持中文搜索
- ⚠️ Excel的B列应填写纯文本文件名，不要使用公式
- ⚠️ 图片文件应放在 `images/` 子目录中 