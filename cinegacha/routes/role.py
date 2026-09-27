# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from flask import Blueprint, request, jsonify
from cinegacha.services.asset_service import AssetService
from cinegacha.services.llm_client import LLMClient
from cinegacha.services.novel_service import NovelService

role_bp = Blueprint('role', __name__, url_prefix='/api')


@role_bp.route('/projects/<int:project_id>/assets', methods=['POST'])
def create_asset(project_id):
    """
    创建资产（角色/场景/道具）

    Request Body:
        {
            "name": "资产名称",
            "novel_id": 1,
            "type": "角色",  // 或 "场景" 或 "道具"
            "content": "资产描述",
            "content_word2": "二次描述"  // 可选
        }

    Returns:
        201: 创建成功
        400: 参数错误
    """
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_NAME", "message": "缺少资产名称"}
        }), 400

    if 'novel_id' not in data:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_NOVEL_ID", "message": "缺少小说 ID"}
        }), 400

    if 'type' not in data:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_TYPE", "message": "缺少资产类型"}
        }), 400

    if 'content' not in data:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_CONTENT", "message": "缺少资产内容"}
        }), 400

    try:
        service = AssetService()
        asset = service.create_asset(
            name=data['name'],
            novel_id=data['novel_id'],
            project_id=project_id,
            role_type=data['type'],
            content=data['content'],
            content_word2=data.get('content_word2')
        )

        return jsonify({
            "success": True,
            "data": {
                "id": asset.id,
                "name": asset.name,
                "novel_id": asset.novel_id,
                "project_id": asset.project_id,
                "type": data['type'],
                "content": asset.content,
                "created_at": asset.created_at.isoformat() if asset.created_at else None
            },
            "message": "资产创建成功"
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "CREATE_ERROR", "message": str(e)}
        }), 500


@role_bp.route('/projects/<int:project_id>/assets', methods=['GET'])
def list_assets(project_id):
    """
    列表资产

    Query Params:
        type: 资产类型过滤 (可选)

    Returns:
        200: 成功
    """
    role_type = request.args.get('type')

    try:
        service = AssetService()
        assets = service.list_assets(project_id=project_id, role_type=role_type)

        return jsonify({
            "success": True,
            "data": [
                {
                    "id": asset.id,
                    "name": asset.name,
                    "novel_id": asset.novel_id,
                    "project_id": asset.project_id,
                    "content": asset.content,
                    "content_word2": asset.content_word2,
                    "created_at": asset.created_at.isoformat() if asset.created_at else None
                }
                for asset in assets
            ],
            "total": len(assets)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "LIST_ERROR", "message": str(e)}
        }), 500


@role_bp.route('/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    """
    获取资产详情

    Args:
        asset_id: 资产 ID

    Returns:
        200: 成功
        404: 未找到
    """
    try:
        service = AssetService()
        asset = service.get_asset(asset_id)

        if asset is None:
            return jsonify({
                "success": False,
                "error": {"code": "ASSET_NOT_FOUND", "message": "资产不存在"}
            }), 404

        # 获取资产类型
        asset_type = None
        for tag in asset.tags:
            if tag.tag_category == "类型":
                asset_type = tag.tag_value
                break

        return jsonify({
            "success": True,
            "data": {
                "id": asset.id,
                "name": asset.name,
                "novel_id": asset.novel_id,
                "project_id": asset.project_id,
                "type": asset_type,
                "content": asset.content,
                "content_word2": asset.content_word2,
                "cover_url": asset.cover_url,
                "role_url": asset.role_url,
                "reference_image_url": asset.reference_image_url,
                "created_at": asset.created_at.isoformat() if asset.created_at else None,
                "updated_at": asset.updated_at.isoformat() if asset.updated_at else None
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "GET_ERROR", "message": str(e)}
        }), 500


@role_bp.route('/assets/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    """
    更新资产

    Args:
        asset_id: 资产 ID

    Request Body:
        {
            "name": "新名称",  // 可选
            "content": "新内容",  // 可选
            "content_word2": "新二次描述"  // 可选
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
        service = AssetService()
        asset = service.update_asset(asset_id, **data)

        return jsonify({
            "success": True,
            "data": {"id": asset.id, "name": asset.name},
            "message": "更新成功"
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "ASSET_NOT_FOUND", "message": str(e)}
        }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "UPDATE_ERROR", "message": str(e)}
        }), 500


@role_bp.route('/assets/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    """
    删除资产

    Args:
        asset_id: 资产 ID

    Returns:
        200: 成功
        404: 未找到
    """
    try:
        service = AssetService()
        result = service.delete_asset(asset_id)

        if not result:
            return jsonify({
                "success": False,
                "error": {"code": "ASSET_NOT_FOUND", "message": "资产不存在"}
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


@role_bp.route('/projects/<int:project_id>/extract-assets', methods=['POST'])
def extract_assets(project_id):
    """
    从小说提取资产（角色/场景/道具）

    Request Body:
        {
            "novel_id": 1,
            "api_key": "sk-xxx"  // DeepSeek API key
        }

    Returns:
        200: 提取成功
        400: 参数错误
    """
    data = request.get_json()

    if not data or 'novel_id' not in data:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_NOVEL_ID", "message": "缺少小说 ID"}
        }), 400

    if 'api_key' not in data:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_API_KEY", "message": "缺少 API key"}
        }), 400

    try:
        # 获取小说内容
        novel_service = NovelService()
        novel = novel_service.get_novel(data['novel_id'])

        if not novel:
            return jsonify({
                "success": False,
                "error": {"code": "NOVEL_NOT_FOUND", "message": "小说不存在"}
            }), 404

        if not novel.content:
            return jsonify({
                "success": False,
                "error": {"code": "NO_CONTENT", "message": "小说内容为空"}
            }), 400

        # 初始化 LLM 客户端
        llm_client = LLMClient(api_key=data['api_key'])

        # 提取资产
        extracted = {
            "characters": [],
            "scenes": [],
            "props": []
        }

        try:
            extracted["characters"] = llm_client.extract_characters(novel.content)
        except Exception as e:
            print(f"提取角色失败: {e}")

        try:
            extracted["scenes"] = llm_client.extract_scenes(novel.content)
        except Exception as e:
            print(f"提取场景失败: {e}")

        try:
            extracted["props"] = llm_client.extract_props(novel.content)
        except Exception as e:
            print(f"提取道具失败: {e}")

        # 创建资产记录
        asset_service = AssetService()
        created_assets = {
            "characters": [],
            "scenes": [],
            "props": []
        }

        for char in extracted["characters"]:
            try:
                asset = asset_service.create_asset(
                    name=char.get("name", "未命名角色"),
                    novel_id=data['novel_id'],
                    project_id=project_id,
                    role_type="角色",
                    content=char.get("description", "")
                )
                created_assets["characters"].append({
                    "id": asset.id,
                    "name": asset.name
                })
            except Exception as e:
                print(f"创建角色失败: {e}")

        for scene in extracted["scenes"]:
            try:
                asset = asset_service.create_asset(
                    name=scene.get("name", "未命名场景"),
                    novel_id=data['novel_id'],
                    project_id=project_id,
                    role_type="场景",
                    content=scene.get("description", "")
                )
                created_assets["scenes"].append({
                    "id": asset.id,
                    "name": asset.name
                })
            except Exception as e:
                print(f"创建场景失败: {e}")

        for prop in extracted["props"]:
            try:
                asset = asset_service.create_asset(
                    name=prop.get("name", "未知道具"),
                    novel_id=data['novel_id'],
                    project_id=project_id,
                    role_type="道具",
                    content=prop.get("description", "")
                )
                created_assets["props"].append({
                    "id": asset.id,
                    "name": asset.name
                })
            except Exception as e:
                print(f"创建道具失败: {e}")

        return jsonify({
            "success": True,
            "data": {
                "extracted": {
                    "characters": len(extracted["characters"]),
                    "scenes": len(extracted["scenes"]),
                    "props": len(extracted["props"])
                },
                "created": created_assets
            },
            "message": "资产提取完成"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "EXTRACT_ERROR", "message": str(e)}
        }), 500
