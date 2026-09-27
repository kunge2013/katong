# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from flask import Blueprint, request, jsonify
from cinegacha.services.storyboard_service import StoryboardService
from cinegacha.services.derivation_service import DerivationService

script_bp = Blueprint('script', __name__, url_prefix='/api')


@script_bp.route('/projects/<int:project_id>/storyboard/split', methods=['POST'])
def split_storyboard(project_id):
    """
    执行分镜拆分

    Request Body:
        {
            "api_key": "sk-xxx"
        }

    Returns:
        200: 拆分成功
        400: 参数错误
    """
    data = request.get_json()

    if not data or 'api_key' not in data:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_API_KEY", "message": "缺少 API key"}
        }), 400

    try:
        service = StoryboardService()
        scripts = service.split_storyboard(project_id, data['api_key'])

        return jsonify({
            "success": True,
            "data": {
                "total": len(scripts),
                "scripts": [
                    {
                        "id": script.id,
                        "shot_id": script.shot_id,
                        "shot_index": script.shot_index,
                        "content_preview": script.content[:100] + "..." if script.content and len(script.content) > 100 else script.content
                    }
                    for script in scripts
                ]
            },
            "message": "分镜拆分完成"
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "SPLIT_ERROR", "message": str(e)}
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "SPLIT_ERROR", "message": str(e)}
        }), 500


@script_bp.route('/projects/<int:project_id>/scripts', methods=['GET'])
def list_scripts(project_id):
    """
    获取项目的分镜列表

    Returns:
        200: 成功
    """
    try:
        service = StoryboardService()
        scripts = service.get_scripts(project_id)

        return jsonify({
            "success": True,
            "data": [
                {
                    "id": script.id,
                    "project_id": script.project_id,
                    "shot_id": script.shot_id,
                    "shot_index": script.shot_index,
                    "content": script.content,
                    "presets": script.presets,
                    "image_prompt": script.image_prompt,
                    "video_prompt": script.video_prompt,
                    "screen_prompt": script.screen_prompt,
                    "main_image": script.main_image,
                    "created_at": script.created_at.isoformat() if script.created_at else None
                }
                for script in scripts
            ],
            "total": len(scripts)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "LIST_ERROR", "message": str(e)}
        }), 500


@script_bp.route('/scripts/<int:script_id>', methods=['GET'])
def get_script(script_id):
    """
    获取分镜详情

    Args:
        script_id: 分镜 ID

    Returns:
        200: 成功
        404: 未找到
    """
    try:
        service = StoryboardService()
        script = service.get_script(script_id)

        if not script:
            return jsonify({
                "success": False,
                "error": {"code": "SCRIPT_NOT_FOUND", "message": "分镜不存在"}
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "id": script.id,
                "project_id": script.project_id,
                "shot_id": script.shot_id,
                "shot_index": script.shot_index,
                "content": script.content,
                "presets": script.presets,
                "image_prompt": script.image_prompt,
                "video_prompt": script.video_prompt,
                "screen_prompt": script.screen_prompt,
                "main_image": script.main_image,
                "candidate_images": script.candidate_images,
                "created_at": script.created_at.isoformat() if script.created_at else None,
                "updated_at": script.updated_at.isoformat() if script.updated_at else None
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "GET_ERROR", "message": str(e)}
        }), 500


@script_bp.route('/scripts/<int:script_id>', methods=['PUT'])
def update_script(script_id):
    """
    更新分镜

    Args:
        script_id: 分镜 ID

    Request Body:
        {
            "content": "新内容",
            "presets": "[\"角色1\", \"场景1\"]"
        }

    Returns:
        200: 成功
        404: 未找到
    """
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": {"code": "NO_DATA", "message": "缺少更新数据"}
        }), 400

    try:
        service = StoryboardService()
        script = service.update_script(script_id, **data)

        return jsonify({
            "success": True,
            "data": {"id": script.id, "shot_index": script.shot_index},
            "message": "更新成功"
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "SCRIPT_NOT_FOUND", "message": str(e)}
        }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "UPDATE_ERROR", "message": str(e)}
        }), 500


@script_bp.route('/scripts/<int:script_id>', methods=['DELETE'])
def delete_script(script_id):
    """
    删除分镜

    Args:
        script_id: 分镜 ID

    Returns:
        200: 成功
        404: 未找到
    """
    try:
        service = StoryboardService()
        result = service.delete_script(script_id)

        if not result:
            return jsonify({
                "success": False,
                "error": {"code": "SCRIPT_NOT_FOUND", "message": "分镜不存在"}
            }), 404

        return jsonify({
            "success": True,
            "message": "删除成功"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "DELETE_ERROR", "message": str(e)}
        }), 500


@script_bp.route('/scripts/<int:script_id>/derive', methods=['POST'])
def derive_image_prompt(script_id):
    """
    为分镜生成图像提示词

    Args:
        script_id: 分镜 ID

    Request Body:
        {
            "api_key": "sk-xxx"
        }

    Returns:
        200: 推导成功
        400: 参数错误
    """
    data = request.get_json()

    if not data or 'api_key' not in data:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_API_KEY", "message": "缺少 API key"}
        }), 400

    try:
        service = DerivationService()
        script = service.derive_image_prompt(script_id, data['api_key'])

        return jsonify({
            "success": True,
            "data": {
                "id": script.id,
                "image_prompt": script.image_prompt,
                "prompt_length": len(script.image_prompt) if script.image_prompt else 0
            },
            "message": "图像提示词推导完成"
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "DERIVE_ERROR", "message": str(e)}
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "DERIVE_ERROR", "message": str(e)}
        }), 500


@script_bp.route('/projects/<int:project_id>/derive-all', methods=['POST'])
def derive_all_prompts(project_id):
    """
    为项目所有分镜生成图像提示词

    Args:
        project_id: 项目 ID

    Request Body:
        {
            "api_key": "sk-xxx"
        }

    Returns:
        200: 推导成功
    """
    data = request.get_json()

    if not data or 'api_key' not in data:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_API_KEY", "message": "缺少 API key"}
        }), 400

    try:
        service = DerivationService()
        scripts = service.derive_all(project_id, data['api_key'])

        return jsonify({
            "success": True,
            "data": {
                "total": len(scripts),
                "derived": [
                    {
                        "id": script.id,
                        "shot_index": script.shot_index,
                        "prompt_length": len(script.image_prompt) if script.image_prompt else 0
                    }
                    for script in scripts
                ]
            },
            "message": "批量推导完成"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "DERIVE_ERROR", "message": str(e)}
        }), 500
