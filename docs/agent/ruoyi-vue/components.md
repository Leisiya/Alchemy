# 组件文档要点（通用若依）

> 类型：**通用若依**  
> 来源：<https://doc.ruoyi.vip/ruoyi-vue/document/zjwd.html>  
> 组件源码多在 `ruoyi-ui/src/components/`

## 表格分页 `Pagination`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| total | — | 总条数 |
| page | 1 | 当前页（常 `.sync` 到 `queryParams.pageNum`） |
| limit | 20 | 页大小（`.sync` → `pageSize`） |
| pageSizes | [10,20,30,50] | 可选页大小 |
| layout | total, sizes, prev, pager, next, jumper | 布局 |
| background | true | 按钮背景 |
| autoScroll | true | 翻页滚顶 |
| hidden | false | 隐藏 |

事件：`@pagination` → 重新拉列表。

## 富文本 `Editor`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| value | — | 内容（常 v-model） |
| height / minHeight | — | 高度 |
| readOnly | false | 只读 |
| fileSize | 5 | 上传限制 MB |
| type | url | 图片存 url 或 base64 |

## 工具栏右侧 `RightToolbar`

显隐搜索、显隐列；`columns`、`showColumnsType`（checkbox/transfer）、`storageKey` 记忆列状态。

## 图片上传 `ImageUpload` / 预览 `ImagePreview`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| value | — | 字符串或数组 |
| action | /common/upload | 上传地址 |
| limit | 5 | 数量 |
| fileSize | 5 | MB |
| fileType | 图片类型数组 | 限制扩展名 |
| disabled | false | 仅查看 |
| drag | true | 拖拽排序 |

预览：`src`、`width`、`height`。

## 文件上传 `FileUpload`

同图片上传，默认 `fileType` 含 doc/xls/ppt/txt/pdf。

## 数据字典 `DictTag`

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| options | null | 字典项 |
| value | — | 当前值（可数组） |
| showValue | true | 无匹配时显示原值 |
| separator | , | 多值分隔 |

## 树分割面板

左侧树 + 右侧内容；关键：`treeData`、`nodeKey`、`treeProps`、`defaultWidth`、`storageKey`、`filterMethod`。

## 导入 Excel 对话框

| 参数 | 必传 | 说明 |
| --- | --- | --- |
| action | 是 | 上传接口 |
| templateAction | 否 | 模板下载 |
| title / width | 否 | 对话框 |
| updateSupportLabel | 否 | 覆盖更新文案 |

## 其他

- **树形选择**：基于 `@riophae/vue-treeselect` 等封装  
- **任务表达式**：定时任务 cron 选择器  

## Agent 选用建议

- 列表页：Pagination + RightToolbar + DictTag  
- 附件：ImageUpload / FileUpload，注意 Token 头与 `profile` 路径  
- 复杂产品 UI：不必硬套生成页布局，可复用上述原子组件
