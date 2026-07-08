# 小木曾雪菜.skill

这是一个 Codex Skill，用来模仿《WHITE ALBUM2》里小木曾雪菜说话、想事情和处理关系的方式。

这个仓库不是用来保存或分发游戏文本的，而是把雪菜这个角色整理成一个可使用的 Codex Skill。它适合用来做角色扮演、关系分析、语气模仿、剧情理解边界提醒，以及“雪菜会怎么想/怎么说”一类任务。

## 仓库内容

- `SKILL.md`：可安装的 Codex Skill。
- `corpus/summary.json`：本地抽取流程得到的语料统计摘要，不包含逐句台词。
- `corpus/setsuna_candidate_dialogue.tsv`：雪菜相关篇章的候选对白抽取结果。
- `corpus/setsuna_high_precision_dialogue.tsv`：用于语气校准的高精度雪菜中心对白子集。
- `tools/wa2_special_corpus.py`：从上游汉化文本中抽取对白与统计摘要的本地脚本。

## 语料来源说明

本 Skill 的语料校准来自 GitHub 上公开的《WHITE ALBUM2 Special Contents》中文汉化插件/补丁项目：

- 汉化文本项目：<https://github.com/xhyf2666/WhiteAlbum2SpecialCHS>
- 补丁下载 release 来源：<https://github.com/xyx266617/WhiteAlbum2SpecialCHS/releases/download/1.0/WHITE.ALBUM2.Special.Contents.rar>

该项目中的汉化文本被本地脚本抽取后，用于统计小木曾雪菜相关篇章的语气特征，例如停顿、语尾、称呼、试探性表达和关系修复动作。

目前本仓库上传的是 Skill、两个雪菜相关对白抽取子集、统计摘要和抽取脚本；没有上传 raw 全量脚本目录、CG、补丁包或可替代原作体验的完整文本集合。

## 其他参考来源

- 官方角色介绍与官方专题页。
- 公开剧情梗概与角色资料页。
- 玩家路线分析与感想文章，用作低权重解释材料。

## 版权与引用边界

《WHITE ALBUM2》、小木曾雪菜及相关游戏素材属于各自权利方。本仓库只是一个角色风格整理和 Codex Skill；请不要把它当作原作文本、汉化补丁或完整语料发布源。

对白 TSV 只用于说明这个 Skill 的语气参考来源。若引用或再分发，请同时保留上游汉化项目来源、抽取方式和用途说明。
