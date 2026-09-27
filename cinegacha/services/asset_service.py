# [AGC:START] tool=Cc author=fangkun
from typing import Optional
from cinegacha import db
from cinegacha.models.role import Role, RoleTag


class AssetService:
    """资产管理服务"""

    def create_asset(
        self,
        name: str,
        novel_id: int,
        project_id: int,
        role_type: str,
        content: str,
        content_word2: Optional[str] = None
    ) -> Role:
        """
        创建资产（角色/场景/道具）
        """
        role = Role(
            name=name,
            novel_id=novel_id,
            project_id=project_id,
            content=content,
            content_word2=content_word2
        )
        db.session.add(role)
        db.session.flush()

        tag = RoleTag(role_id=role.id, tag_category="类型", tag_value=role_type)
        db.session.add(tag)
        db.session.commit()

        return role

    def get_asset(self, asset_id: int) -> Optional[Role]:
        """获取资产"""
        return db.session.get(Role, asset_id)

    def list_assets(
        self,
        project_id: int,
        role_type: Optional[str] = None
    ) -> list[Role]:
        """列出资产，可按类型过滤"""
        query = db.session.query(Role).filter(Role.project_id == project_id)

        if role_type:
            query = query.join(RoleTag).filter(
                RoleTag.tag_category == "类型",
                RoleTag.tag_value == role_type
            )

        return query.all()

    def update_asset(self, asset_id: int, **kwargs) -> Role:
        """更新资产"""
        role = db.session.get(Role, asset_id)
        if not role:
            raise ValueError(f"资产 {asset_id} 不存在")

        for key, value in kwargs.items():
            if hasattr(role, key):
                setattr(role, key, value)

        db.session.commit()
        return role

    def delete_asset(self, asset_id: int) -> bool:
        """删除资产"""
        role = db.session.get(Role, asset_id)
        if not role:
            return False

        db.session.delete(role)
        db.session.commit()
        return True
# [AGC:END]
