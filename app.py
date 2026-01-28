import os
import json
import subprocess
from flask import Flask, request, render_template_string, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'secret_key_for_flash_messages'

# ================= 配置区域 =================
# 请修改为你存放 MP3 的实际目录路径
MUSIC_DIR = "/Users/admin/Downloads/music/yuyin"
# ===========================================

# 检查目录是否存在
if not os.path.exists(MUSIC_DIR):
    print(f"错误: 目录 {MUSIC_DIR} 不存在，请在代码中修改 MUSIC_DIR 路径。")

def get_mp3_files():
    """获取目录下所有 MP3 文件"""
    files = []
    if os.path.exists(MUSIC_DIR):
        for f in os.listdir(MUSIC_DIR):
            if f.lower().endswith('.mp3'):
                files.append(f)
    return sorted(files)

def get_metadata(filename):
    """
    使用 ffprobe 获取 metadata 信息 (返回 JSON 格式)
    """
    filepath = os.path.join(MUSIC_DIR, filename)
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        filepath
    ]
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        data = json.loads(result)
        tags = data.get('format', {}).get('tags', {})
        return tags
    except Exception as e:
        print(f"读取 Metadata 失败: {e}")
        return {}

def update_metadata_ffmpeg(filename, new_tags):
    input_path = os.path.join(MUSIC_DIR, filename)
    temp_path = os.path.join(MUSIC_DIR, f"temp_{filename}")

    # 核心逻辑：
    # -map 0: 映射输入文件的所有流（包括音频和封面图片）
    # -c copy: 所有流（音频和图像）都进行流复制，不重新编码，无损且快
    # -id3v2_version 3: 使用兼容性最好的 ID3 格式
    cmd = [
        'ffmpeg', '-i', input_path,
        '-map', '0',
        '-c', 'copy'
    ]

    # 添加元数据修改参数
    valid_keys = ['title', 'artist', 'album', 'date', 'genre']
    for key in valid_keys:
        val = new_tags.get(key, '').strip()
        cmd.extend(['-metadata', f'{key}={val}'])

    # 关键点：将视频流标记为“附件图片”（即封面），防止 FFmpeg 把它当成普通视频轨道处理
    cmd.extend(['-disposition:v:0', 'attached_pic'])

    # 输出路径，-y 表示如果临时文件已存在则覆盖
    cmd.extend([temp_path, '-y', '-loglevel', 'error'])

    print(f"正在尝试保留所有内容修改: {filename}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True)
        if os.path.exists(temp_path):
            os.replace(temp_path, input_path)
            return True
    except subprocess.CalledProcessError as e:
        # 如果还是报错，说明该文件的封面图（Video Stream）编码无法被直接 copy 写入 MP3
        # 此时唯一的办法是重新编码封面图（将图片流从 copy 改为 mjpeg）
        error_msg = e.stderr.decode('utf-8', errors='ignore')
        print(f"保留内容修改失败，尝试降级修复方案...")
        return fallback_update_with_recode_cover(filename, new_tags)


def fallback_update_with_recode_cover(filename, new_tags):
    """
    降级方案：处理MP2编码的MP3文件
    """
    input_path = os.path.join(MUSIC_DIR, filename)
    temp_path = os.path.join(MUSIC_DIR, f"temp_fix_{filename}")

    # 针对MP2编码的MP3文件，重新编码为标准的MP3格式
    cmd = [
        'ffmpeg', '-i', input_path,
        '-c:a', 'libmp3lame',  # 使用标准的MP3编码器
        '-q:a', '2',           # 高质量设置（0-9，0是最高质量）
        '-id3v2_version', '3',
        '-write_id3v1', '1',
        '-map_metadata', '0'   # 保留原始元数据
    ]

    # 添加新的元数据（会覆盖原有的）
    valid_keys = ['title', 'artist', 'album', 'date', 'genre']
    for key in valid_keys:
        val = new_tags.get(key, '').strip()
        if val:
            cmd.extend(['-metadata', f'{key}={val}'])

    cmd.extend([temp_path, '-y', '-loglevel', 'warning'])

    print(f"检测到MP2编码的MP3文件，重新编码为标准MP3格式...")

    try:
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if process.returncode == 0 and os.path.exists(temp_path):
            # 验证输出文件
            if os.path.getsize(temp_path) > 1024:  # 大于1KB
                os.replace(temp_path, input_path)
                print(f"成功重新编码为MP3: {filename}")
                return True
            else:
                print(f"输出文件太小，可能编码失败")
                os.remove(temp_path)
                return False
        else:
            print(f"重新编码失败: {process.stderr[:500]}")
            return False

    except Exception as e:
        print(f"处理异常: {e}")
        return False
# ================= 路由与视图 =================

@app.route('/')
def index():
    files = get_mp3_files()
    return render_template_string(HTML_TEMPLATE, view='list', files=files, dir=MUSIC_DIR)

@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit(filename):
    if request.method == 'POST':
        new_tags = {
            'title': request.form.get('title'),
            'artist': request.form.get('artist'),
            'album': request.form.get('album'),
            'date': request.form.get('date'),
            'genre': request.form.get('genre'),
        }
        if update_metadata_ffmpeg(filename, new_tags):
            flash(f'成功修改: {filename}', 'success')
            return redirect(url_for('index'))
        else:
            flash('修改失败，请检查控制台日志', 'danger')
            return redirect(url_for('edit', filename=filename))

    # GET 请求：读取当前信息并填入表单
    tags = get_metadata(filename)
    return render_template_string(HTML_TEMPLATE, view='edit', filename=filename, tags=tags)

# ================= 简易 HTML 模板 =================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MP3 Tag 编辑器 (FFmpeg)</title>
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.1.3/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding-top: 20px; }
        .container { max-width: 800px; background: white; padding: 30px; border-radius: 10px; shadow: 0 0 10px rgba(0,0,0,0.1); }
        .tag-badge { font-size: 0.8em; color: #666; }
    </style>
</head>
<body>
<div class="container shadow">
    <h2 class="mb-4">🎵 MP3 Tag 编辑器</h2>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% if view == 'list' %}
        <p class="text-muted">当前目录: <code>{{ dir }}</code></p>
        <div class="list-group">
            {% for file in files %}
            <a href="{{ url_for('edit', filename=file) }}" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                <span>{{ file }}</span>
                <span class="badge bg-primary rounded-pill">编辑</span>
            </a>
            {% else %}
                <div class="alert alert-warning">该目录下没有 MP3 文件</div>
            {% endfor %}
        </div>
    {% elif view == 'edit' %}
        <div class="card">
            <div class="card-header">编辑: <strong>{{ filename }}</strong></div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">标题 (Title)</label>
                        <input type="text" class="form-control" name="title" value="{{ tags.get('title', '') }}">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">艺术家 (Artist)</label>
                        <input type="text" class="form-control" name="artist" value="{{ tags.get('artist', '') }}">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">专辑 (Album)</label>
                        <input type="text" class="form-control" name="album" value="{{ tags.get('album', '') }}">
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">年份 (Date/Year)</label>
                            <input type="text" class="form-control" name="date" value="{{ tags.get('date', '') }}">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">流派 (Genre)</label>
                            <input type="text" class="form-control" name="genre" value="{{ tags.get('genre', '') }}">
                        </div>
                    </div>
                    <div class="d-flex justify-content-between">
                        <a href="{{ url_for('index') }}" class="btn btn-secondary">返回列表</a>
                        <button type="submit" class="btn btn-success">保存修改 (FFmpeg)</button>
                    </div>
                </form>
            </div>
        </div>
    {% endif %}
</div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, port=5002)
