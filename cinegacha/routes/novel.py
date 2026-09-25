# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from flask import Blueprint, request, jsonify
from cinegacha.services.novel_service import NovelService

novel_bp = Blueprint('novel', __name__, url_prefix='/api/novels')


@novel_bp.route('', methods=['POST'])
def create_novel():
    """
    创建小说

    Request Body:
        {
            "name": "小说名称",
            "text": "小说文本",  // 可选
            "url": "小说 URL"    // 可选
        }

    Returns:
        201: 创建成功
        400: 参数错误
    """
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_NAME", "message": "缺少小说名称"}
        }), 400

    try:
        service = NovelService()
        novel = service.create_novel(
            name=data['name'],
            text=data.get('text'),
            url=data.get('url')
        )

        return jsonify({
            "success": True,
            "data": {
                "id": novel.id,
                "name": novel.name,
                "original_text": novel.original_text[:100] + "..." if len(novel.original_text) > 100 else novel.original_text,
                "word_count": novel.word_count,
                "created_at": novel.created_at.isoformat() if novel.created_at else None
            },
            "message": "小说创建成功"
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "CREATE_ERROR", "message": str(e)}
        }), 500


@novel_bp.route('', methods=['GET'])
def list_novels():
    """
    列表小说

    Query Params:
        page: 页码 (default: 1)
        per_page: 每页数量 (default: 20)

    Returns:
        200: 成功
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    try:
        service = NovelService()
        novels, total = service.list_novels(page=page, per_page=per_page)

        return jsonify({
            "success": True,
            "data": [
                {
                    "id": novel.id,
                    "name": novel.name,
                    "word_count": novel.word_count,
                    "is_format_cleaned": novel.is_format_cleaned,
                    "is_serial_cleaned": novel.is_serial_cleaned,
                    "is_punct_cleaned": novel.is_punct_cleaned,
                    "created_at": novel.created_at.isoformat() if novel.created_at else None
                }
                for novel in novels
            ],
            "total": total,
            "page": page,
            "per_page": per_page
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "LIST_ERROR", "message": str(e)}
        }), 500


@novel_bp.route('/<int:novel_id>', methods=['GET'])
def get_novel(novel_id):
    """
    获取小说详情

    Args:
        novel_id: 小说 ID

    Returns:
        200: 成功
        404: 未找到
    """
    try:
        service = NovelService()
        novel = service.get_novel(novel_id)

        if novel is None:
            return jsonify({
                "success": False,
                "error": {"code": "NOVEL_NOT_FOUND", "message": "小说不存在"}
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "id": novel.id,
                "name": novel.name,
                "original_text": novel.original_text,
                "content": novel.content,
                "share_url": novel.share_url,
                "word_count": novel.word_count,
                "is_format_cleaned": novel.is_format_cleaned,
                "is_serial_cleaned": novel.is_serial_cleaned,
                "is_punct_cleaned": novel.is_punct_cleaned,
                "is_shot_cleaned": novel.is_shot_cleaned,
                "created_at": novel.created_at.isoformat() if novel.created_at else None,
                "updated_at": novel.updated_at.isoformat() if novel.updated_at else None
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "GET_ERROR", "message": str(e)}
        }), 500


@novel_bp.route('/<int:novel_id>/clean', methods=['POST'])
def clean_novel(novel_id):
    """
    清洗小说文本

    Args:
        novel_id: 小说 ID

    Returns:
        200: 清洗成功
        404: 小说不存在
    """
    try:
        service = NovelService()
        novel = service.clean_text(novel_id)

        return jsonify({
            "success": True,
            "data": {
                "id": novel.id,
                "name": novel.name,
                "content_preview": novel.content[:200] + "..." if len(novel.content) > 200 else novel.content,
                "word_count": novel.word_count,
                "is_format_cleaned": novel.is_format_cleaned,
                "is_serial_cleaned": novel.is_serial_cleaned,
                "is_punct_cleaned": novel.is_punct_cleaned,
                "is_shot_cleaned": novel.is_shot_cleaned
            },
            "message": "清洗完成"
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "NOVEL_NOT_FOUND", "message": str(e)}
        }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "CLEAN_ERROR", "message": str(e)}
        }), 500


@novel_bp.route('/<int:novel_id>', methods=['PUT'])
def update_novel(novel_id):
    """更新小说"""
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": {"code": "NO_DATA", "message": "缺少更新数据"}
        }), 400

    try:
        service = NovelService()
        novel = service.update_novel(novel_id, **data)

        return jsonify({
            "success": True,
            "data": {"id": novel.id, "name": novel.name},
            "message": "更新成功"
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "NOVEL_NOT_FOUND", "message": str(e)}
        }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "UPDATE_ERROR", "message": str(e)}
        }), 500


@novel_bp.route('/<int:novel_id>', methods=['DELETE'])
def delete_novel(novel_id):
    """删除小说"""
    try:
        service = NovelService()
        result = service.delete_novel(novel_id)

        if not result:
            return jsonify({
                "success": False,
                "error": {"code": "NOVEL_NOT_FOUND", "message": "小说不存在"}
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
