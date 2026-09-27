#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
雪漫画 CineGacha 启动文件
"""

from cinegacha import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
