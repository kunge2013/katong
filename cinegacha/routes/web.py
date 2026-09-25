# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from flask import Blueprint, render_template, flash, redirect, url_for
from cinegacha.services.novel_service import NovelService
from cinegacha import db
from cinegacha.models.novel import Novel
from cinegacha.models.project import Project

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    """首页"""
    novel_count = db.session.query(Novel).count()
    project_count = db.session.query(Project).count()
    return render_template('index.html', novel_count=novel_count, project_count=project_count)


@web_bp.route('/novels')
def novels_list():
    """小说列表页面"""
    service = NovelService()
    novels, _ = service.list_novels(page=1, per_page=100)
    return render_template('novels.html', novels=novels)


@web_bp.route('/novels/new')
def novel_new():
    """创建小说页面"""
    return render_template('novel_new.html')


@web_bp.route('/novels/<int:novel_id>')
def novel_detail(novel_id):
    """小说详情页面"""
    service = NovelService()
    novel = service.get_novel(novel_id)
    if not novel:
        flash('小说不存在', 'error')
        return redirect(url_for('web.novels_list'))
    return render_template('novel_detail.html', novel=novel)


# [AGC:START] tool=Cc author=fangkun
@web_bp.route('/settings')
def settings():
    """设置页面"""
    return render_template('settings.html')
# [AGC:END]
