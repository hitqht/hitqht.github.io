媒体附件文件夹使用说明
========================

本文件夹用于存放网站引用的所有图片 / 视频附件，按用途分三个子目录：

  team/   团队成员照片
  blog/   博客文章插图、视频
  misc/   其它杂项（横幅照片、首页卡片图等）

■ 团队成员照片（team/）
  把真人照片按下面的文件名放进 team/，网页会自动显示，无需改任何代码：
    shan-wenchen.jpg   单文臣
    ding-yao.jpg       丁尧
    xia-yi.jpg         夏毅
    zhou-junwen.jpg    周俊文
    xu-chengran.jpg    许成然
    li-dongsheng.jpg   李东声
    du-heli.jpg        杜和醨
    yin-hang.jpg       尹航
  · 建议：正方形、不小于 400×400 像素的 JPG（png 也可以，把文件名后缀一并改为 .png 即可，
    但需在 team.html 里把对应 img 的 src 后缀改掉）。
  · 没放照片的成员会显示 _placeholder.svg 灰色占位头像。

■ 博客插图与视频（blog/）
  示例文章引用了 post1-fig1.jpg、post1-fig2.jpg、post1-demo.mp4，
  放入同名文件即自动替换占位图/占位视频。
  新文章插图命名建议：<文章 slug>-fig<序号>.jpg，例如 floorplan-fig1.jpg。

■ 杂项（misc/）
    qihongtuo.jpg   主页「个人简介」个人照片（竖版 3:4，建议 ≥600×800 像素）
  放入后主页照片自动替换占位图；_portrait.svg 为占位图，请勿删除。

■ 注意
  · 文件名一律用小写字母、数字和连字符，不要用中文或空格（避免链接编码问题）。
  · 图片建议压缩到 500KB 以内再上传，视频尽量用 mp4 (H.264)。
  · 以下划线开头的文件（_placeholder.svg、_figure.svg）是占位图，请勿删除。
